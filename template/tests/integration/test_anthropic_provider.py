"""Contrato do AnthropicProvider com um cliente dublê (sem rede).

O teste ``live`` só roda com ANTHROPIC_API_KEY definida: ``pytest -m live``.
"""

import os
from types import SimpleNamespace
from typing import Any

import anthropic
import httpx2
import pytest

from app.domain.models import Message
from app.llm.anthropic_provider import SERVER_FALLBACK_BETA, AnthropicProvider
from app.llm.provider import LLMRequest, PermanentLLMError, RefusalError, TransientLLMError

pytestmark = pytest.mark.integration

REQUEST = LLMRequest(
    system="sys",
    messages=[Message(role="user", content="oi")],
    model="claude-opus-5-5",
    max_tokens=100,
    effort="low",
)


class _Messages:
    def __init__(self, result: Any) -> None:
        self.result = result
        self.kwargs: dict[str, Any] = {}

    async def create(self, **kwargs: Any) -> Any:
        self.kwargs = kwargs
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def _client(result: Any) -> tuple[Any, _Messages]:
    messages = _Messages(result)
    return SimpleNamespace(beta=SimpleNamespace(messages=messages)), messages


def _response(stop_reason: str = "end_turn") -> Any:
    return SimpleNamespace(
        content=[SimpleNamespace(type="thinking"), SimpleNamespace(type="text", text="olá")],
        model="claude-opus-5-5",
        usage=SimpleNamespace(input_tokens=10, output_tokens=2),
        stop_reason=stop_reason,
    )


def _status_error(cls: type[anthropic.APIStatusError], status: int) -> anthropic.APIStatusError:
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    response = httpx2.Response(status, request=request, headers={"retry-after": "3"})
    return cls("erro", response=response, body=None)


async def test_success_maps_text_usage_and_request_shape() -> None:
    client, messages = _client(_response())
    result = await AnthropicProvider(10, client=client).complete(REQUEST)
    assert result.text == "olá"
    assert result.input_tokens == 10
    assert messages.kwargs["betas"] == [SERVER_FALLBACK_BETA]
    assert messages.kwargs["extra_body"]["fallbacks"] == "default"
    assert messages.kwargs["extra_body"]["output_config"] == {"effort": "low"}


async def test_refusal_raises() -> None:
    client, _ = _client(_response("refusal"))
    with pytest.raises(RefusalError):
        await AnthropicProvider(10, client=client).complete(REQUEST)


async def test_rate_limit_is_transient_with_retry_after() -> None:
    client, _ = _client(_status_error(anthropic.RateLimitError, 429))
    with pytest.raises(TransientLLMError) as info:
        await AnthropicProvider(10, client=client).complete(REQUEST)
    assert info.value.retry_after == 3.0


async def test_server_error_is_transient() -> None:
    client, _ = _client(_status_error(anthropic.InternalServerError, 500))
    with pytest.raises(TransientLLMError):
        await AnthropicProvider(10, client=client).complete(REQUEST)


async def test_bad_request_is_permanent() -> None:
    client, _ = _client(_status_error(anthropic.BadRequestError, 400))
    with pytest.raises(PermanentLLMError):
        await AnthropicProvider(10, client=client).complete(REQUEST)


@pytest.mark.live
@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="sem ANTHROPIC_API_KEY")
async def test_live_round_trip() -> None:
    result = await AnthropicProvider(60).complete(REQUEST)
    assert result.text
