"""Command line interface for running and inspecting experiments."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import typer

from agent_eval.config import load_config
from agent_eval.evaluators.aggregate import deterministic_provider_note, render_report
from agent_eval.runner.experiment import ExperimentRunner

app = typer.Typer(help="Run configurable reliability evaluations for tool-using agents.")


@app.command()
def run(config: str = typer.Argument(..., help="Path to an experiment YAML file.")) -> None:
    """Run or resume an experiment and write its report."""

    experiment = load_config(config)
    typer.echo(f"Experiment: {experiment.experiment_id}")
    typer.echo(f"Cases: {experiment.environment.cases}")
    typer.echo(f"Policies: {', '.join(experiment.policies)}")
    typer.echo(f"Concurrency: {experiment.concurrency}")
    typer.echo("Running...")
    result = asyncio.run(ExperimentRunner(experiment).run())
    expected = result["cases"] * len(experiment.models) * len(experiment.policies)
    typer.echo(f"Completed: {result['completed']}/{expected}")
    typer.echo(f"Report: {result['report_path']}")


@app.command()
def report(
    experiment_id: str = typer.Argument(...),
    output_dir: str = typer.Option("results", help="Directory containing metrics JSON."),
    report_dir: str = typer.Option("reports", help="Directory receiving Markdown."),
) -> None:
    """Regenerate a Markdown report from persisted metrics."""

    metrics_path = Path(output_dir) / f"{experiment_id}.metrics.json"
    if not metrics_path.exists():
        raise typer.BadParameter(f"metrics file not found: {metrics_path}")
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    metadata_path = Path(output_dir) / f"{experiment_id}.meta.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}
    provider_note = deterministic_provider_note() if metadata.get("providers") == ["mock"] else None
    destination = Path(report_dir) / f"{experiment_id}.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_report(experiment_id, metrics, provider_note), encoding="utf-8")
    typer.echo(f"Report: {destination}")


if __name__ == "__main__":
    app()
