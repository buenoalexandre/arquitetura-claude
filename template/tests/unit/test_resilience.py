import pytest

from app.core.config import LLMSettings
from app.core.errors import LLMUnavailableError, RateLimitExceededError
from app.domain.models import Message
from app.llm.fake_provider import FakeProvider
from app.llm.provider import LLMRequest
from app.llm.resilience import CircuitBreaker, CircuitState, ResilientLLMClient, TokenBucket
from app.observability.metrics import Metrics

pytestmark = pytest.mark.unit


def _request(model: str = "primary") -> LLMRequest:
    return LLMRequest(
        system="s", messages=[Message(role="user", content="oi")], model=model, max_tokens=100
    )


def _settings(**overrides: object) -> LLMSettings:
    base: dict[str, object] = {
        "max_retries": 3,
        "retry_wait_base_seconds": 0,
        "timeout_seconds": 1,
        "requests_per_minute": 1000,
        "fallback_model": None,
    }
    base.update(overrides)
    return LLMSettings.model_validate(base)


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_circuit_breaker_opens_and_half_opens() -> None:
    clock = FakeClock()
    breaker = CircuitBreaker(failure_threshold=2, reset_timeout=10, clock=clock)
    breaker.record_failure()
    assert breaker.state is CircuitState.CLOSED
    breaker.record_failure()
    assert breaker.state is CircuitState.OPEN
    clock.now = 11
    assert breaker.state is CircuitState.HALF_OPEN
    breaker.record_success()
    assert breaker.state is CircuitState.CLOSED


def test_token_bucket_limits_and_refills() -> None:
    clock = FakeClock()
    bucket = TokenBucket(rate_per_minute=2, clock=clock)
    assert bucket.try_acquire()
    assert bucket.try_acquire()
    assert not bucket.try_acquire()
    clock.now = 30
    assert bucket.try_acquire()


async def test_retries_transient_errors_then_succeeds() -> None:
    provider = FakeProvider(fail_times=2)
    client = ResilientLLMClient(provider, _settings(), Metrics())
    response = await client.complete(_request())
    assert response.text.startswith("Resposta simulada")
    assert len(provider.calls) == 3


async def test_exhausted_retries_raise_unavailable() -> None:
    client = ResilientLLMClient(FakeProvider(fail_times=10), _settings(), Metrics())
    with pytest.raises(LLMUnavailableError):
        await client.complete(_request())


async def test_open_circuit_fails_fast() -> None:
    provider = FakeProvider(fail_times=100)
    settings = _settings(max_retries=1, circuit_breaker={"failure_threshold": 1})
    client = ResilientLLMClient(provider, settings, Metrics())
    with pytest.raises(LLMUnavailableError):
        await client.complete(_request())
    calls_before = len(provider.calls)
    with pytest.raises(LLMUnavailableError):
        await client.complete(_request())
    assert len(provider.calls) == calls_before  # não chamou o provedor


async def test_fallback_model_is_used() -> None:
    provider = FakeProvider(failing_models={"primary"})
    client = ResilientLLMClient(provider, _settings(fallback_model="backup"), Metrics())
    response = await client.complete(_request())
    assert response.model == "backup"


async def test_timeout_is_transient() -> None:
    provider = FakeProvider(latency_seconds=0.2)
    settings = _settings(timeout_seconds=0.05, max_retries=1)
    client = ResilientLLMClient(provider, settings, Metrics())
    with pytest.raises(LLMUnavailableError):
        await client.complete(_request())


async def test_rate_limit() -> None:
    client = ResilientLLMClient(FakeProvider(), _settings(requests_per_minute=1), Metrics())
    await client.complete(_request())
    with pytest.raises(RateLimitExceededError):
        await client.complete(_request())
