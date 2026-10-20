"""Resiliência para chamadas a LLM.

Camadas aplicadas, nesta ordem, a cada chamada:
1. Rate limit local (token bucket) — protege orçamento e cota do provedor.
2. Circuit breaker — falha rápido quando o provedor está instável.
3. Timeout por tentativa.
4. Retentativas com backoff exponencial + jitter, só para erros transitórios.
5. Fallback para um modelo alternativo quando o principal se esgota.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from dataclasses import replace
from enum import StrEnum

from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from app.core.config import LLMSettings
from app.core.errors import LLMRefusalError, LLMUnavailableError, RateLimitExceededError
from app.core.logging import get_logger
from app.llm.provider import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
    PermanentLLMError,
    RefusalError,
    TransientLLMError,
)
from app.observability.metrics import Metrics

log = get_logger(__name__)
Clock = Callable[[], float]


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(
        self, failure_threshold: int, reset_timeout: float, clock: Clock = time.monotonic
    ) -> None:
        self._threshold = failure_threshold
        self._reset_timeout = reset_timeout
        self._clock = clock
        self._failures = 0
        self._opened_at: float | None = None

    @property
    def state(self) -> CircuitState:
        if self._opened_at is None:
            return CircuitState.CLOSED
        if self._clock() - self._opened_at >= self._reset_timeout:
            return CircuitState.HALF_OPEN
        return CircuitState.OPEN

    def allow_request(self) -> bool:
        return self.state != CircuitState.OPEN

    def record_success(self) -> None:
        self._failures = 0
        self._opened_at = None

    def record_failure(self) -> None:
        self._failures += 1
        if self.state == CircuitState.HALF_OPEN or self._failures >= self._threshold:
            self._opened_at = self._clock()


class TokenBucket:
    def __init__(self, rate_per_minute: int, clock: Clock = time.monotonic) -> None:
        self._capacity = float(rate_per_minute)
        self._tokens = float(rate_per_minute)
        self._refill_per_second = rate_per_minute / 60.0
        self._clock = clock
        self._updated = clock()

    def try_acquire(self) -> bool:
        now = self._clock()
        elapsed = now - self._updated
        self._tokens = min(self._capacity, self._tokens + elapsed * self._refill_per_second)
        self._updated = now
        if self._tokens >= 1:
            self._tokens -= 1
            return True
        return False


class ResilientLLMClient:
    def __init__(self, provider: LLMProvider, settings: LLMSettings, metrics: Metrics) -> None:
        self._provider = provider
        self._settings = settings
        self._metrics = metrics
        # Um breaker por modelo: a instabilidade do principal não bloqueia o fallback.
        self._breakers: dict[str, CircuitBreaker] = {}
        self._bucket = TokenBucket(settings.requests_per_minute)

    def breaker(self, model: str) -> CircuitBreaker:
        if model not in self._breakers:
            self._breakers[model] = CircuitBreaker(
                self._settings.circuit_breaker.failure_threshold,
                self._settings.circuit_breaker.reset_timeout_seconds,
            )
        return self._breakers[model]

    async def complete(self, request: LLMRequest) -> LLMResponse:
        if not self._bucket.try_acquire():
            self._metrics.increment("llm_requests_total", status="rate_limited")
            raise RateLimitExceededError()
        try:
            return await self._call_with_retries(request)
        except LLMUnavailableError:
            fallback = self._settings.fallback_model
            if not fallback or fallback == request.model:
                raise
            log.warning("llm_fallback", primary=request.model, fallback=fallback)
            self._metrics.increment("llm_fallback_total", model=fallback)
            return await self._call_with_retries(replace(request, model=fallback), attempts=1)

    async def _call_with_retries(
        self, request: LLMRequest, attempts: int | None = None
    ) -> LLMResponse:
        breaker = self.breaker(request.model)
        if not breaker.allow_request():
            self._metrics.increment(
                "llm_requests_total", model=request.model, status="circuit_open"
            )
            raise LLMUnavailableError("circuit breaker aberto")

        retrying = AsyncRetrying(
            retry=retry_if_exception_type(TransientLLMError),
            stop=stop_after_attempt(attempts or self._settings.max_retries),
            wait=wait_random_exponential(multiplier=self._settings.retry_wait_base_seconds, max=8),
            reraise=False,
        )
        try:
            async for attempt in retrying:
                with attempt:
                    return await self._single_call(request)
        except RetryError as exc:
            breaker.record_failure()
            raise LLMUnavailableError() from exc
        except RefusalError as exc:
            breaker.record_success()  # recusa não indica instabilidade do provedor
            raise LLMRefusalError() from exc
        except PermanentLLMError as exc:
            raise LLMUnavailableError() from exc
        raise LLMUnavailableError()  # inalcançável: tenacity sempre retorna ou levanta

    async def _single_call(self, request: LLMRequest) -> LLMResponse:
        started = time.perf_counter()
        try:
            async with asyncio.timeout(self._settings.timeout_seconds):
                response = await self._provider.complete(request)
        except TimeoutError as exc:
            self._record(request.model, "timeout", started)
            raise TransientLLMError("timeout") from exc
        except TransientLLMError:
            self._record(request.model, "transient_error", started)
            raise
        self.breaker(request.model).record_success()
        self._record(request.model, "ok", started)
        self._metrics.increment("llm_tokens_total", response.input_tokens, kind="input")
        self._metrics.increment("llm_tokens_total", response.output_tokens, kind="output")
        return response

    def _record(self, model: str, status: str, started: float) -> None:
        elapsed_ms = (time.perf_counter() - started) * 1000
        self._metrics.increment("llm_requests_total", model=model, status=status)
        self._metrics.observe("llm_latency_ms", elapsed_ms, model=model)
