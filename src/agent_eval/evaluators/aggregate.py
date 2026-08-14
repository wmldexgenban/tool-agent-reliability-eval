"""Metric aggregation and comparison report rendering."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from statistics import mean
from typing import Any


def _sum_optional(values: list[int | None]) -> int | None:
    present = [value for value in values if value is not None]
    return sum(present) if present else None


def deterministic_provider_note() -> str:
    """Label offline mock output so reports cannot be mistaken for model comparisons."""

    return (
        "Provider: MockProvider\n"
        "Purpose: pipeline validation\n\n"
        "These values come from the deterministic mock provider and are intended to verify "
        "framework behavior, not compare real model quality."
    )


def aggregate_outcomes(outcomes: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(outcomes)
    total = len(rows)
    if not total:
        return {
            "episodes": 0,
            "task_accuracy": 0.0,
            "unsupported_commit_rate": 0.0,
            "guard_rejection_rate": 0.0,
            "false_rejection_rate": 0.0,
            "evidence_coverage": 0.0,
            "avg_latency_ms": 0.0,
            "token_usage": {"prompt": None, "completion": None, "total": None},
        }

    evaluations = [row["evaluation"] for row in rows]
    usage = [row.get("usage") or {} for row in rows]
    return {
        "episodes": total,
        "task_accuracy": round(sum(item["task_correct"] for item in evaluations) / total, 4),
        "unsupported_commit_rate": round(sum(item["unsupported_commit"] for item in evaluations) / total, 4),
        "guard_rejection_rate": round(sum(item["guard_rejected"] for item in evaluations) / total, 4),
        "false_rejection_rate": round(sum(item["false_rejection"] for item in evaluations) / total, 4),
        "evidence_coverage": round(sum(item["evidence_valid"] for item in evaluations) / total, 4),
        "avg_latency_ms": round(mean(row["latency_ms"] for row in rows), 3),
        "token_usage": {
            "prompt": _sum_optional([item.get("prompt_tokens") for item in usage]),
            "completion": _sum_optional([item.get("completion_tokens") for item in usage]),
            "total": _sum_optional([item.get("total_tokens") for item in usage]),
        },
    }


def group_and_aggregate(outcomes: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in outcomes:
        grouped[f"{row['model']}::{row['policy']}"].append(row)
    return {key: aggregate_outcomes(value) for key, value in sorted(grouped.items())}


def render_report(
    experiment_id: str,
    metrics: dict[str, dict[str, Any]],
    provider_note: str | None = None,
    title: str | None = None,
) -> str:
    lines = [
        f"# {title or f'Evaluation Report: {experiment_id}'}",
        "",
        "This report summarizes synthetic tool-use episodes produced by the configured run.",
        "",
        "| Model | Policy | Episodes | Task Accuracy | Unsupported Commit Rate | Guard Rejection Rate | False Rejection Rate | Evidence Coverage | Avg Latency (ms) | Token Usage (p/c/t) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key, item in metrics.items():
        model, policy = key.rsplit("::", 1)
        token_usage = item["token_usage"]
        tokens = (
            f"{token_usage['prompt']}/{token_usage['completion']}/{token_usage['total']}"
            if token_usage["total"] is not None
            else "unavailable"
        )
        lines.append(
            f"| {model} | {policy} | {item['episodes']} | {item['task_accuracy']:.1%} | "
            f"{item['unsupported_commit_rate']:.1%} | {item['guard_rejection_rate']:.1%} | "
            f"{item['false_rejection_rate']:.1%} | {item['evidence_coverage']:.1%} | "
            f"{item['avg_latency_ms']:.3f} | "
            f"{tokens if tokens is not None else 'unavailable'} |"
        )
    lines += [
        "",
        "## Reading the trade-off",
        "",
        (
            "Accuracy measures useful task completion. Unsupported Commit measures accepted answers "
            "without a valid record reference. Guard Rejection and False Rejection show the cost and "
            "risk of deterministic evidence checks."
        ),
    ]
    if provider_note:
        lines += ["", provider_note]
    return "\n".join(lines) + "\n"
