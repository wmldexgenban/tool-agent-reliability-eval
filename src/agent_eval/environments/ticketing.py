"""Synthetic customer-support ticket API."""

from __future__ import annotations

import random
from typing import Any

from .base import ToolEnvironment, ToolObservation


class TicketingEnvironment(ToolEnvironment):
    name = "ticketing"

    def generate_cases(self, count: int, seed: int, **options: Any) -> list[ToolObservation]:
        rng = random.Random(seed)
        schema_semantics = options.get("schema_semantics", "explicit")
        evidence_mode = options.get("evidence_availability", "full")
        cases: list[ToolObservation] = []
        for index in range(count):
            tickets = [
                {"ticket_id": f"TCK-{index + 1:03d}-{suffix}", "priority_score": score, "queue": queue}
                for suffix, score, queue in (
                    ("A", 42 + index % 9, "billing"),
                    ("B", 76 + (index * 3) % 15, "account"),
                    ("C", 61 + (index * 5) % 18, "shipping"),
                    ("D", 88 + (index * 2) % 9, "security"),
                )
            ]
            truth = max(tickets, key=lambda ticket: ticket["priority_score"])
            hint = tickets[0]
            visible = tickets if evidence_mode == "full" else tickets[:-1] if evidence_mode == "partial" else []
            if schema_semantics == "explicit":
                summary = {"suggested_ticket_id": hint["ticket_id"], "selection_basis": "routing_hint"}
            else:
                summary = {"suggested_value": hint["ticket_id"], "basis": "hint"}
            cases.append(
                ToolObservation(
                    case_id=f"ticket-{index + 1:03d}",
                    task="Which customer ticket should be handled first?",
                    tool_name="support.search",
                    response={"tickets": visible, "summary": summary},
                    answer_type="ticket",
                    ground_truth=truth["ticket_id"],
                    evidence_catalog=[f"ticketing:record:{ticket['ticket_id']}" for ticket in visible],
                )
            )
            rng.random()
        return cases

