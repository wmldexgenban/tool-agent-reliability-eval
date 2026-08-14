"""Mutable recorder used by one episode and serialized with its result."""

from __future__ import annotations

from typing import Any

from .events import AgentTrace, TraceEvent


class TraceRecorder:
    def __init__(self, episode_id: str) -> None:
        self.trace = AgentTrace(episode_id=episode_id)

    def record(self, event_type: str, **data: Any) -> None:
        self.trace.events.append(TraceEvent(event_type=event_type, data=data))

    def snapshot(self) -> AgentTrace:
        return self.trace.model_copy(deep=True)

