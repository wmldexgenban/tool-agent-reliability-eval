"""Deterministic provider for local demos and repeatable tests."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from .base import ModelProvider, ModelRequest, ModelResponse


class MockProvider(ModelProvider):
    """Selects a metadata hint for baseline and verifies records for guarded modes."""

    def __init__(self, model_name: str = "deterministic-mock") -> None:
        self.model_name = model_name

    async def generate(self, request: ModelRequest) -> ModelResponse:
        await asyncio.sleep(0)
        payload: dict[str, Any] = request.metadata["tool_response"]
        environment = request.metadata["environment"]
        policy = request.metadata["policy"]
        answer_type = "inventory" if environment == "inventory" else "ticket"
        rows = payload.get("items" if answer_type == "inventory" else "tickets", [])
        summary = payload.get("summary", {})

        if policy == "baseline":
            value = summary.get(
                "recommended_sku" if answer_type == "inventory" else "suggested_ticket_id",
                summary.get("suggested_value", "unknown"),
            )
            ref = f"{environment}:summary"
        elif rows and answer_type == "inventory":
            selected = max(rows, key=lambda row: row.get("available_stock", row.get("quantity_available", 0)))
            value = selected.get("sku") or selected.get("product_code")
            ref = f"inventory:record:{value}"
        elif rows:
            selected = max(rows, key=lambda row: row["priority_score"])
            value = selected["ticket_id"]
            ref = f"ticketing:record:{value}"
        else:
            value = summary.get(
                "recommended_sku" if answer_type == "inventory" else "suggested_ticket_id",
                summary.get("suggested_value", "unknown"),
            )
            ref = f"{environment}:summary"

        candidate = {
            "value": value,
            "answer_type": answer_type,
            "evidence_refs": [ref] if rows_exist(payload, answer_type, value, policy) else [],
            "confidence": 0.82 if policy == "baseline" else 0.94,
        }
        return ModelResponse(text=json.dumps(candidate), model_name=self.model_name)


def rows_exist(payload: dict[str, Any], answer_type: str, value: str, policy: str) -> bool:
    """Return whether the mock can cite the selected record in the visible response."""

    if policy == "baseline":
        return True
    key = "items" if answer_type == "inventory" else "tickets"
    value_key = "sku" if answer_type == "inventory" else "ticket_id"
    return any(row.get(value_key) == value for row in payload.get(key, []))
