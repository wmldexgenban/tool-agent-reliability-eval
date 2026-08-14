"""Typed YAML configuration for evaluation runs."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class EnvironmentConfig(BaseModel):
    name: Literal["inventory", "ticketing"]
    cases: int = Field(default=24, ge=1, le=200)
    seed: int = 7
    schema_semantics: Literal["explicit", "compact"] = "explicit"
    field_naming: Literal["strong", "neutral"] = "strong"
    evidence_availability: Literal["full", "partial", "none"] = "full"


class ModelConfig(BaseModel):
    name: str
    provider: Literal["mock", "openai_compatible"] = "mock"
    model_name: str | None = None
    base_url: str | None = None
    api_key_env: str = "MODEL_API_KEY"
    timeout_s: float = Field(default=30.0, gt=0)


class RetryConfig(BaseModel):
    max_attempts: int = Field(default=3, ge=1, le=8)
    base_delay_s: float = Field(default=0.05, ge=0)
    max_delay_s: float = Field(default=1.0, ge=0)


class ExperimentConfig(BaseModel):
    experiment_id: str
    environment: EnvironmentConfig
    models: list[ModelConfig] = Field(min_length=1)
    policies: list[Literal["baseline", "self_check", "evidence_guard"]] = Field(
        default_factory=lambda: ["baseline"]
    )
    concurrency: int = Field(default=5, ge=1, le=100)
    retry: RetryConfig = Field(default_factory=RetryConfig)
    output_dir: str = "results"
    report_dir: str = "reports"


def load_config(path: str | Path) -> ExperimentConfig:
    """Load and validate an experiment YAML file."""

    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return ExperimentConfig.model_validate(data)

