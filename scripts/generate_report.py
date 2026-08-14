"""Regenerate a report from a persisted metrics file."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from agent_eval.evaluators.aggregate import render_report


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/generate_report.py <experiment_id>")
    experiment_id = sys.argv[1]
    metrics_path = Path("results") / f"{experiment_id}.metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    destination = Path("reports") / f"{experiment_id}.md"
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(render_report(experiment_id, metrics), encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    main()

