"""Policy interfaces and shared submission result types."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from agent_eval.agents.baseline import CandidateAnswer
from agent_eval.environments.base import ToolObservation


class PolicyResult(BaseModel):
    accepted: bool
    reason: str
    required_sources: list[str] = Field(default_factory=list)
    validated_refs: list[str] = Field(default_factory=list)


class SubmissionPolicy(ABC):
    name: str

    @property
    @abstractmethod
    def instruction(self) -> str:
        """Prompt addition for the agent."""

    @abstractmethod
    def validate(self, candidate: CandidateAnswer, observation: ToolObservation) -> PolicyResult:
        """Validate a candidate before final submission."""

