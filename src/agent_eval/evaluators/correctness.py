"""Task-level correctness checks."""

from __future__ import annotations

from agent_eval.agents.baseline import CandidateAnswer
from agent_eval.environments.base import ToolObservation
from agent_eval.policies.base import PolicyResult


def task_is_correct(
    candidate: CandidateAnswer,
    observation: ToolObservation,
    policy_result: PolicyResult,
) -> bool:
    return policy_result.accepted and candidate.value == observation.ground_truth

