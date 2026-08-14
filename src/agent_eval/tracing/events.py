"""Trace event types."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class TraceEvent(BaseModel):
    event_type: str
    at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: dict[str, Any] = Field(default_factory=dict)


class AgentTrace(BaseModel):
    episode_id: str
    events: list[TraceEvent] = Field(default_factory=list)

