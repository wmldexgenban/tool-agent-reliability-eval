"""Extensible deterministic evidence policy."""

from __future__ import annotations

from collections.abc import Callable

from pydantic import BaseModel, Field

from agent_eval.agents.baseline import CandidateAnswer
from agent_eval.environments.base import ToolObservation

from .base import PolicyResult, SubmissionPolicy


class EvidenceRequirement(BaseModel):
    answer_type: str
    required_sources: list[str] = Field(min_length=1)
    validator: str


Validator = Callable[[CandidateAnswer, ToolObservation, str], bool]


class EvidenceRequirementRegistry:
    """Maps answer types to source requirements and named validators."""

    def __init__(self, requirements: list[EvidenceRequirement] | None = None) -> None:
        self._requirements = {item.answer_type: item for item in requirements or default_requirements()}
        self._validators: dict[str, Validator] = {"record_match": record_match_validator}

    def requirement_for(self, answer_type: str) -> EvidenceRequirement | None:
        return self._requirements.get(answer_type)

    def validator_for(self, name: str) -> Validator:
        try:
            return self._validators[name]
        except KeyError as exc:
            raise ValueError(f"unknown evidence validator: {name}") from exc


class EvidenceGuard(SubmissionPolicy):
    name = "evidence_guard"

    def __init__(self, registry: EvidenceRequirementRegistry | None = None) -> None:
        self.registry = registry or EvidenceRequirementRegistry()

    @property
    def instruction(self) -> str:
        return "Select an answer only when a visible record supports it and cite the exact record reference."

    def validate(self, candidate: CandidateAnswer, observation: ToolObservation) -> PolicyResult:
        requirement = self.registry.requirement_for(candidate.answer_type)
        if requirement is None:
            return PolicyResult(accepted=False, reason="unknown_answer_type")
        if not candidate.evidence_refs:
            return PolicyResult(
                accepted=False,
                reason="insufficient_evidence",
                required_sources=requirement.required_sources,
            )
        validator = self.registry.validator_for(requirement.validator)
        valid = [
            ref for ref in candidate.evidence_refs
            if validator(candidate, observation, ref) and self._source(ref) in requirement.required_sources
        ]
        if not valid:
            return PolicyResult(
                accepted=False,
                reason="insufficient_evidence",
                required_sources=requirement.required_sources,
            )
        return PolicyResult(
            accepted=True,
            reason="evidence_validated",
            required_sources=requirement.required_sources,
            validated_refs=valid,
        )

    @staticmethod
    def _source(ref: str) -> str:
        if ref.startswith("inventory:record:"):
            return "inventory_record"
        if ref.startswith("ticketing:record:"):
            return "ticket_record"
        return "unknown"


def default_requirements() -> list[EvidenceRequirement]:
    return [
        EvidenceRequirement(answer_type="inventory", required_sources=["inventory_record"], validator="record_match"),
        EvidenceRequirement(answer_type="ticket", required_sources=["ticket_record"], validator="record_match"),
    ]


def record_match_validator(candidate: CandidateAnswer, observation: ToolObservation, ref: str) -> bool:
    """Validate both the reference and its relation to the submitted value."""

    if ref not in observation.evidence_catalog:
        return False
    expected_prefix = "inventory:record:" if candidate.answer_type == "inventory" else "ticketing:record:"
    return ref == f"{expected_prefix}{candidate.value}"


def evidence_is_valid(candidate: CandidateAnswer, observation: ToolObservation) -> bool:
    """Reusable metric helper independent of the selected submission policy."""

    return EvidenceGuard().validate(candidate, observation).accepted

