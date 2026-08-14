"""Trace event types."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class TraceEvent(BaseModel):
    event_type: str
    at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data: dict[str, Any] = Field(default_factory=dict)


class AgentTrace(BaseModel):
    episode_id: str
    events: list[TraceEvent] = Field(default_factory=list)

