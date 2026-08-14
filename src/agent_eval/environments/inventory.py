"""Synthetic inventory API with a deliberately stale recommendation field."""

from __future__ import annotations

import random
from typing import Any

from .base import ToolEnvironment, ToolObservation


class InventoryEnvironment(ToolEnvironment):
    name = "inventory"

    def generate_cases(self, count: int, seed: int, **options: Any) -> list[ToolObservation]:
        rng = random.Random(seed)
        field_naming = options.get("field_naming", "strong")
        schema_semantics = options.get("schema_semantics", "explicit")
        evidence_mode = options.get("evidence_availability", "full")
        cases: list[ToolObservation] = []

        for index in range(count):
            prefix = f"SKU-{chr(65 + index % 20)}{17 + index:02d}"
            codes = [prefix, f"SKU-{chr(66 + index % 20)}{31 + index:02d}", f"SKU-{chr(67 + index % 20)}{44 + index:02d}"]
            quantities = [54 + (index * 7) % 18, 96 + (index * 11) % 21, 72 + (index * 5) % 19]
            warehouses = ["SG-01", "SG-02", "JP-01"]
            rows = [
                self._row(code, quantity, warehouse, field_naming)
                for code, quantity, warehouse in zip(codes, quantities, warehouses)
            ]
            truth_row = max(rows, key=lambda row: self._quantity(row, field_naming))
            recommended = rows[0]
            visible_rows = rows if evidence_mode == "full" else rows[:-1] if evidence_mode == "partial" else []
            if schema_semantics == "explicit":
                summary = {"recommended_sku": self._code(recommended, field_naming), "selection_basis": "system_hint"}
            else:
                summary = {"suggested_value": self._code(recommended, field_naming), "basis": "hint"}
            response = {"items": visible_rows, "summary": summary}
            refs = [f"inventory:record:{self._code(row, field_naming)}" for row in visible_rows]
            cases.append(
                ToolObservation(
                    case_id=f"inventory-{index + 1:03d}",
                    task="Which SKU currently has the highest available stock?",
                    tool_name="inventory.lookup",
                    response=response,
                    answer_type="inventory",
                    ground_truth=self._code(truth_row, field_naming),
                    evidence_catalog=refs,
                )
            )
            rng.random()  # Keep the seed part of the generation contract for future variants.
        return cases

    @staticmethod
    def _row(code: str, quantity: int, warehouse: str, naming: str) -> dict[str, Any]:
        if naming == "neutral":
            return {"product_code": code, "quantity_available": quantity, "site": warehouse}
        return {"sku": code, "available_stock": quantity, "warehouse": warehouse}

    @staticmethod
    def _code(row: dict[str, Any], naming: str) -> str:
        return row["product_code"] if naming == "neutral" else row["sku"]

    @staticmethod
    def _quantity(row: dict[str, Any], naming: str) -> int:
        return row["quantity_available"] if naming == "neutral" else row["available_stock"]

