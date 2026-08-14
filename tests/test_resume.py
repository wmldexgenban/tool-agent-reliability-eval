import asyncio

from agent_eval.config import ExperimentConfig
from agent_eval.runner.experiment import ExperimentRunner


def test_completed_episodes_are_skipped_on_resume(tmp_path) -> None:
    config = ExperimentConfig.model_validate(
        {
            "experiment_id": "resume-check",
            "environment": {"name": "inventory", "cases": 3, "seed": 4},
            "models": [{"name": "mock", "provider": "mock"}],
            "policies": ["baseline"],
            "output_dir": str(tmp_path / "results"),
            "report_dir": str(tmp_path / "reports"),
        }
    )
    first = asyncio.run(ExperimentRunner(config).run())
    second = asyncio.run(ExperimentRunner(config).run())
    assert first["scheduled"] == 3
    assert second["scheduled"] == 0
    assert second["completed"] == 3

