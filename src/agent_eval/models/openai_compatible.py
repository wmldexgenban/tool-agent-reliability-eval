"""Small OpenAI-compatible chat completion adapter."""

from __future__ import annotations

import os

import httpx

from .base import ModelProvider, ModelRequest, ModelResponse, ProviderError, TokenUsage
from .mock_provider import MockProvider


class OpenAICompatibleProvider(ModelProvider):
    """Adapter for providers exposing a chat-completions compatible endpoint."""

    def __init__(
        self,
        *,
        model_name: str,
        base_url: str,
        api_key: str,
        timeout_s: float = 30.0,
    ) -> None:
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s

    async def generate(self, request: ModelRequest) -> ModelResponse:
        body = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                response = await client.post(f"{self.base_url}/chat/completions", json=body, headers=headers)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise ProviderError("model request timed out", retryable=True) from exc
        except httpx.HTTPStatusError as exc:
            retryable = exc.response.status_code == 429 or exc.response.status_code >= 500
            raise ProviderError(
                f"model request failed with HTTP {exc.response.status_code}",
                status_code=exc.response.status_code,
                retryable=retryable,
            ) from exc
        except httpx.HTTPError as exc:
            raise ProviderError("model transport failed", retryable=True) from exc

        data = response.json()
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("provider returned an unexpected response shape") from exc
        raw_usage = data.get("usage")
        usage = TokenUsage.model_validate(
            {
                "prompt_tokens": raw_usage.get("prompt_tokens"),
                "completion_tokens": raw_usage.get("completion_tokens"),
                "total_tokens": raw_usage.get("total_tokens"),
            }
        ) if raw_usage else None
        return ModelResponse(text=text, usage=usage, model_name=self.model_name)


def provider_from_config(model_config: object) -> ModelProvider:
    """Build a provider from a validated ModelConfig without embedding credentials."""

    if model_config.provider == "mock":
        return MockProvider(model_config.model_name or model_config.name)
    api_key = os.getenv(model_config.api_key_env)
    base_url = model_config.base_url or os.getenv("MODEL_BASE_URL")
    model_name = model_config.model_name or os.getenv("MODEL_NAME")
    if not api_key or not base_url or not model_name:
        raise ValueError("openai_compatible provider requires API key, base URL, and model name")
    return OpenAICompatibleProvider(
        model_name=model_name,
        base_url=base_url,
        api_key=api_key,
        timeout_s=model_config.timeout_s,
    )
