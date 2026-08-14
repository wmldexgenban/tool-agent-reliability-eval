"""Per-episode reliability classification."""

from __future__ import annotations

from agent_eval.agents.baseline import CandidateAnswer
from agent_eval.environments.base import ToolObservation
from agent_eval.policies.base import PolicyResult
from agent_eval.policies.evidence_guard import evidence_is_valid


def classify_reliability(
    candidate: CandidateAnswer,
    observation: ToolObservation,
    policy_result: PolicyResult,
    policy_name: str,
) -> dict[str, bool]:
    evidence_valid = evidence_is_valid(candidate, observation)
    return {
        "evidence_valid": evidence_valid,
        "unsupported_commit": policy_result.accepted and not evidence_valid,
        "guard_rejected": policy_name == "evidence_guard" and not policy_result.accepted,
        "false_rejection": policy_name == "evidence_guard" and not policy_result.accepted and evidence_valid,
    }

