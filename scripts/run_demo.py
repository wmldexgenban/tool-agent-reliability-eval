"""Run both built-in environments and create one portfolio-friendly summary."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import yaml

from agent_eval.agents.baseline import ToolUsingAgent
from agent_eval.config import ExperimentConfig
from agent_eval.environments.inventory import InventoryEnvironment
from agent_eval.evaluators.aggregate import deterministic_provider_note, render_report
from agent_eval.models.mock_provider import MockProvider
from agent_eval.policies.evidence_guard import EvidenceGuard
from agent_eval.policies.self_check import BaselinePolicy
from agent_eval.runner.episode import run_episode
from agent_eval.runner.experiment import ExperimentRunner


async def main() -> None:
    results = []
    for config_name in ("demo_inventory.yaml", "demo_ticket.yaml"):
        path = Path("configs") / config_name
        config = ExperimentConfig.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
        results.append(await ExperimentRunner(config).run())

    combined = {}
    for result in results:
        for key, metrics in result["metrics"].items():
            combined[f"{result['experiment_id']}/{key}"] = metrics
    report = render_report(
        "sample",
        combined,
        deterministic_provider_note(),
        title="Deterministic Demo Report",
    )
    Path("reports").mkdir(exist_ok=True)
    Path("reports/sample_report.md").write_text(report, encoding="utf-8")
    await write_example_trace()
    print("Created reports/sample_report.md")


async def write_example_trace() -> None:
    """Persist a compact structured trace for the portfolio walkthrough."""

    observation = InventoryEnvironment().generate_cases(1, 17, evidence_availability="full")[0]
    guard = EvidenceGuard()
    outcome = await run_episode(
        episode_id="portfolio-trace-example",
        model_name="deterministic-mock",
        observation=observation,
        agent=ToolUsingAgent(MockProvider(), "baseline", BaselinePolicy().instruction),
        policy=guard,
    )
    candidate = outcome.candidate
    if candidate is None:
        raise RuntimeError("example trace did not produce a candidate")
    payload = {
        "episode_id": outcome.episode_id,
        "task": observation.task,
        "candidate": candidate.value,
        "evidence_status": "supported" if outcome.evaluation["evidence_valid"] else "unsupported",
        "decision": "accepted" if outcome.policy_result.accepted else "rejected",
        "failure_stage": outcome.failure_stage,
        "events": [
            {"event_type": event.event_type, "data": event.data}
            for event in outcome.trace.events
            if event.event_type != "TOOL_RESPONSE_RECEIVED"
        ],
    }
    Path("reports/example_trace.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    asyncio.run(main())
