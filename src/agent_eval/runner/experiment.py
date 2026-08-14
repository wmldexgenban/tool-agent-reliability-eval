"""Batch experiment orchestration with incremental persistence and resume."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from agent_eval.agents.baseline import ToolUsingAgent
from agent_eval.config import ExperimentConfig
from agent_eval.environments.base import ToolEnvironment
from agent_eval.environments.inventory import InventoryEnvironment
from agent_eval.environments.ticketing import TicketingEnvironment
from agent_eval.evaluators.aggregate import (
    deterministic_provider_note,
    group_and_aggregate,
    render_report,
)
from agent_eval.models.base import ModelProvider
from agent_eval.models.openai_compatible import provider_from_config
from agent_eval.policies.base import SubmissionPolicy
from agent_eval.policies.evidence_guard import EvidenceGuard
from agent_eval.policies.self_check import BaselinePolicy, SelfCheckPolicy
from agent_eval.storage.jsonl import JsonlStore
from agent_eval.storage.sqlite import SQLiteStateStore

from .episode import EpisodeOutcome, failed_episode, run_episode
from .scheduler import ConcurrencyLimiter, with_retry

logger = logging.getLogger(__name__)


def environment_from_config(config: ExperimentConfig) -> ToolEnvironment:
    return InventoryEnvironment() if config.environment.name == "inventory" else TicketingEnvironment()


def policy_from_name(name: str) -> SubmissionPolicy:
    if name == "baseline":
        return BaselinePolicy()
    if name == "self_check":
        return SelfCheckPolicy()
    if name == "evidence_guard":
        return EvidenceGuard()
    raise ValueError(f"unsupported policy: {name}")


class ExperimentRunner:
    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.result_store = JsonlStore(self.output_dir / f"{config.experiment_id}.jsonl")
        self.state_store = SQLiteStateStore(self.output_dir / f"{config.experiment_id}.db")

    async def run(self) -> dict[str, Any]:
        environment = environment_from_config(self.config)
        observations = environment.generate_cases(
            self.config.environment.cases,
            self.config.environment.seed,
            schema_semantics=self.config.environment.schema_semantics,
            field_naming=self.config.environment.field_naming,
            evidence_availability=self.config.environment.evidence_availability,
        )
        completed = self.result_store.completed_ids() | self.state_store.completed_ids()
        limiter = ConcurrencyLimiter(self.config.concurrency)
        jobs: list[tuple[str, str, ModelProvider, SubmissionPolicy, Any]] = []
        for model_config in self.config.models:
            provider = provider_from_config(model_config)
            for policy_name in self.config.policies:
                policy = policy_from_name(policy_name)
                for observation in observations:
                    episode_id = (
                        f"{self.config.experiment_id}::{model_config.name}::{policy_name}::{observation.case_id}"
                    )
                    if episode_id not in completed:
                        jobs.append((episode_id, model_config.name, provider, policy, observation))
        logger.info("experiment=%s scheduled=%d skipped=%d", self.config.experiment_id, len(jobs), len(completed))

        async def execute(job: tuple[str, str, ModelProvider, SubmissionPolicy, Any]) -> EpisodeOutcome:
            episode_id, model_name, provider, policy, observation = job
            agent = ToolUsingAgent(provider, policy.name, policy.instruction)

            async def call() -> object:
                return await run_episode(
                    episode_id=episode_id,
                    model_name=model_name,
                    observation=observation,
                    agent=agent,
                    policy=policy,
                )

            try:
                outcome = await limiter.run(lambda: with_retry(call, self.config.retry))
            except Exception as exc:  # noqa: BLE001 - persist failed episodes for resume.
                outcome = failed_episode(
                    episode_id,
                    model_name,
                    observation,
                    policy,
                    recorder=None,
                    timer=0.0,
                    error=str(exc),
                )
            assert isinstance(outcome, EpisodeOutcome)
            self.result_store.append(outcome)
            logger.debug("episode=%s status=%s", outcome.episode_id, outcome.status)
            if outcome.status == "completed":
                self.state_store.mark_completed(outcome.episode_id)
            return outcome

        await asyncio.gather(*(execute(job) for job in jobs))
        rows = self.result_store.read_all()
        metrics = group_and_aggregate(row for row in rows if row.get("status") == "completed")
        metrics_path = self.output_dir / f"{self.config.experiment_id}.metrics.json"
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        metadata_path = self.output_dir / f"{self.config.experiment_id}.meta.json"
        metadata_path.write_text(
            json.dumps(
                {
                    "experiment_id": self.config.experiment_id,
                    "environment": self.config.environment.name,
                    "providers": [model.provider for model in self.config.models],
                    "policies": self.config.policies,
                    "cases": len(observations),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        report_path = Path(self.config.report_dir) / f"{self.config.experiment_id}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        provider_note = None
        if all(model.provider == "mock" for model in self.config.models):
            provider_note = deterministic_provider_note()
        report_path.write_text(render_report(self.config.experiment_id, metrics, provider_note), encoding="utf-8")
        return {
            "experiment_id": self.config.experiment_id,
            "cases": len(observations),
            "scheduled": len(jobs),
            "completed": sum(1 for row in rows if row.get("status") == "completed"),
            "metrics": metrics,
            "report_path": str(report_path),
        }
