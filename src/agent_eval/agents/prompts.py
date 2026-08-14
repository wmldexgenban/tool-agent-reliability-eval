"""Prompt templates kept separate from execution and policy code."""

from __future__ import annotations

import json
from typing import Any


def build_user_prompt(task: str, tool_response: dict[str, Any], policy: str, instruction: str) -> str:
    return (
        f"Task: {task}\n"
        f"Submission policy: {policy}\n"
        f"Policy instruction: {instruction}\n"
        "Return JSON with value, answer_type, evidence_refs, and confidence.\n"
        "TOOL_RESPONSE_JSON:\n"
        f"{json.dumps(tool_response, sort_keys=True)}"
    )

