"""Run both built-in environments and create one portfolio-friendly summary."""

from __future__ import annotations

import asyncio
from pathlib import Path

import yaml

from agent_eval.config import ExperimentConfig
from agent_eval.evaluators.aggregate import render_report
from agent_eval.runner.experiment import ExperimentRunner


async def main() -> None:
    results = []
    for config_name in ("demo_inventory.yaml", "demo_ticket.yaml"):
        path = Path("configs") / config_name
        config = ExperimentConfig.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
        results.append(await ExperimentRunner(config).run())

    combined = {}
    for result in results:
        for key, metrics in result["metrics"].items():
            combined[f"{result['experiment_id']}/{key}"] = metrics
    report = render_report(
        "sample",
        combined,
        "Sample results generated with the built-in deterministic mock provider.",
    )
    Path("reports").mkdir(exist_ok=True)
    Path("reports/sample_report.md").write_text(report, encoding="utf-8")
    print("Created reports/sample_report.md")


if __name__ == "__main__":
    asyncio.run(main())
