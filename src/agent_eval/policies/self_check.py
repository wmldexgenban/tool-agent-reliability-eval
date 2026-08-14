"""Prompt-only self-check policy."""

from agent_eval.agents.baseline import CandidateAnswer
from agent_eval.environments.base import ToolObservation

from .base import PolicyResult, SubmissionPolicy


class BaselinePolicy(SubmissionPolicy):
    name = "baseline"

    @property
    def instruction(self) -> str:
        return "Read the tool response and submit the most likely answer. Do not add a separate verification step."

    def validate(self, candidate: CandidateAnswer, observation: ToolObservation) -> PolicyResult:
        return PolicyResult(accepted=True, reason="baseline_submission")


class SelfCheckPolicy(SubmissionPolicy):
    name = "self_check"

    @property
    def instruction(self) -> str:
        return (
            "Before returning JSON, check the candidate against visible records, identify its supporting record, "
            "and make evidence_refs point to that record."
        )

    def validate(self, candidate: CandidateAnswer, observation: ToolObservation) -> PolicyResult:
        return PolicyResult(accepted=True, reason="prompt_self_check_completed")

