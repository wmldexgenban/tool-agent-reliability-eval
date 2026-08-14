"""Provider contracts shared by real and deterministic model backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    """Usage reported by a provider; unavailable values remain null."""

    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class ModelRequest(BaseModel):
    system_prompt: str
    user_prompt: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModelResponse(BaseModel):
    text: str
    usage: TokenUsage | None = None
    model_name: str


class ProviderError(RuntimeError):
    """A provider failure with retry metadata for the episode scheduler."""

    def __init__(self, message: str, *, status_code: int | None = None, retryable: bool = False):
        super().__init__(message)
        self.status_code = status_code
        self.retryable = retryable


class ModelProvider(ABC):
    """Async interface used by the runner."""

    model_name: str

    @abstractmethod
    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate one structured candidate response."""

