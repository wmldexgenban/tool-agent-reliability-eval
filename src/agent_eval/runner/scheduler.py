"""Concurrency and retry controls."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from agent_eval.config import RetryConfig
from agent_eval.models.base import ProviderError


async def with_retry(operation: Callable[[], Awaitable[object]], config: RetryConfig) -> object:
    """Retry timeouts and provider 429/5xx failures with bounded exponential backoff."""

    for attempt in range(config.max_attempts):
        try:
            return await operation()
        except (asyncio.TimeoutError, ProviderError) as exc:
            retryable = isinstance(exc, asyncio.TimeoutError) or exc.retryable
            if not retryable or attempt == config.max_attempts - 1:
                raise
            delay = min(config.max_delay_s, config.base_delay_s * (2**attempt))
            if delay:
                await asyncio.sleep(delay)
    raise RuntimeError("retry loop exited unexpectedly")


class ConcurrencyLimiter:
    def __init__(self, limit: int) -> None:
        self._semaphore = asyncio.Semaphore(limit)

    async def run(self, operation: Callable[[], Awaitable[object]]) -> object:
        async with self._semaphore:
            return await operation()

