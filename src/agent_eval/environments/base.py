"""Contracts for deterministic tool environments."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ToolObservation(BaseModel):
    case_id: str
    task: str
    tool_name: str
    response: dict[str, Any]
    answer_type: str
    ground_truth: str
    evidence_catalog: list[str] = Field(default_factory=list)


class ToolEnvironment(ABC):
    """Produces a task and the structured response exposed to an agent."""

    name: str

    @abstractmethod
    def generate_cases(self, count: int, seed: int, **options: Any) -> list[ToolObservation]:
        """Generate reproducible synthetic observations."""

