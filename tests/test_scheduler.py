import asyncio

from agent_eval.config import RetryConfig
from agent_eval.models.base import ProviderError
from agent_eval.runner.scheduler import with_retry


def test_retry_handles_transient_provider_error() -> None:
    attempts = 0

    async def operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ProviderError("temporary", status_code=503, retryable=True)
        return "ok"

    result = asyncio.run(with_retry(operation, RetryConfig(max_attempts=3, base_delay_s=0)))
    assert result == "ok"
    assert attempts == 3

