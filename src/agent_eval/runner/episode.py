"""One complete task-to-evaluation execution."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from agent_eval.agents.baseline import CandidateAnswer, ToolUsingAgent
from agent_eval.environments.base import ToolObservation
from agent_eval.evaluators.correctness import task_is_correct
from agent_eval.evaluators.reliability import classify_reliability
from agent_eval.models.base import ProviderError, TokenUsage
from agent_eval.policies.base import PolicyResult, SubmissionPolicy
from agent_eval.tracing.events import AgentTrace
from agent_eval.tracing.recorder import TraceRecorder


class EpisodeOutcome(BaseModel):
    episode_id: str
    status: str
    model: str
    policy: str
    case_id: str
    started_at: datetime
    finished_at: datetime
    latency_ms: float
    usage: TokenUsage | None = None
    candidate: CandidateAnswer | None = None
    policy_result: PolicyResult
    final_answer: str | None = None
    evaluation: dict[str, bool] = Field(default_factory=dict)
    trace: AgentTrace
    error: str | None = None


async def run_episode(
    *,
    episode_id: str,
    model_name: str,
    observation: ToolObservation,
    agent: ToolUsingAgent,
    policy: SubmissionPolicy,
) -> EpisodeOutcome:
    started_at = datetime.now(timezone.utc)
    timer = time.perf_counter()
    recorder = TraceRecorder(episode_id)
    recorder.record("TASK_CREATED", case_id=observation.case_id, task=observation.task)
    recorder.record("TOOL_RESPONSE_RECEIVED", tool_name=observation.tool_name, response=observation.response)
    try:
        turn = await agent.act(observation)
        candidate = turn.candidate
        recorder.record("CANDIDATE_SELECTED", candidate=candidate.model_dump(mode="json"))
        policy_result = policy.validate(candidate, observation)
        recorder.record(
            "EVIDENCE_CHECKED",
            accepted=policy_result.accepted,
            reason=policy_result.reason,
            validated_refs=policy_result.validated_refs,
        )
        recorder.record(
            "SUBMISSION_ACCEPTED" if policy_result.accepted else "SUBMISSION_REJECTED",
            reason=policy_result.reason,
        )
        reliability = classify_reliability(candidate, observation, policy_result, policy.name)
        evaluation = {
            "task_correct": task_is_correct(candidate, observation, policy_result),
            **reliability,
        }
        recorder.record("EPISODE_EVALUATED", evaluation=evaluation)
        usage = turn.response.usage
        return EpisodeOutcome(
            episode_id=episode_id,
            status="completed",
            model=model_name,
            policy=policy.name,
            case_id=observation.case_id,
            started_at=started_at,
            finished_at=datetime.now(timezone.utc),
            latency_ms=round((time.perf_counter() - timer) * 1000, 3),
            usage=usage,
            candidate=candidate,
            policy_result=policy_result,
            final_answer=candidate.value if policy_result.accepted else None,
            evaluation=evaluation,
            trace=recorder.snapshot(),
        )
    except ProviderError as exc:
        if exc.retryable:
            raise
        return failed_episode(episode_id, model_name, observation, policy, recorder, timer, str(exc))
    except Exception as exc:  # Preserve a failed trace so a later run can resume it.
        return failed_episode(episode_id, model_name, observation, policy, recorder, timer, str(exc))


def failed_episode(
    episode_id: str,
    model_name: str,
    observation: ToolObservation,
    policy: SubmissionPolicy,
    recorder: TraceRecorder | None,
    timer: float,
    error: str,
) -> EpisodeOutcome:
    if recorder is None:
        recorder = TraceRecorder(episode_id)
        recorder.record("TASK_CREATED", case_id=observation.case_id, task=observation.task)
        recorder.record("TOOL_RESPONSE_RECEIVED", tool_name=observation.tool_name, response=observation.response)
    if timer == 0.0:
        timer = time.perf_counter()
    policy_result = PolicyResult(accepted=False, reason="execution_error")
    recorder.record("SUBMISSION_REJECTED", reason="execution_error")
    return EpisodeOutcome(
        episode_id=episode_id,
        status="failed",
        model=model_name,
        policy=policy.name,
        case_id=observation.case_id,
        started_at=datetime.now(timezone.utc),
        finished_at=datetime.now(timezone.utc),
        latency_ms=round((time.perf_counter() - timer) * 1000, 3),
        policy_result=policy_result,
        evaluation={
            "task_correct": False,
            "evidence_valid": False,
            "unsupported_commit": False,
            "guard_rejected": False,
            "false_rejection": False,
        },
        trace=recorder.snapshot(),
        error=error,
    )
