"""Implementação do provedor usando o SDK oficial da Anthropic."""

from __future__ import annotations

import anthropic
from anthropic.types.beta import BetaMessageParam

from app.llm.provider import (
    LLMRequest,
    LLMResponse,
    PermanentLLMError,
    RefusalError,
    TransientLLMError,
)

# Fallback no servidor: se o modelo principal recusar, a API reexecuta a mesma requisição
# no modelo recomendado para a categoria da recusa (ver docs/operations/resilience.md).
SERVER_FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AnthropicProvider:
    name = "anthropic"

    def __init__(
        self,
        timeout_seconds: float,
        client: anthropic.AsyncAnthropic | None = None,
    ) -> None:
        # max_retries=0: as retentativas ficam na camada de resiliência, evitando que
        # SDK e aplicação multipliquem tentativas (e custo) entre si.
        self._client = client or anthropic.AsyncAnthropic(timeout=timeout_seconds, max_retries=0)

    async def complete(self, request: LLMRequest) -> LLMResponse:
        messages: list[BetaMessageParam] = [
            {"role": m.role, "content": m.content} for m in request.messages
        ]
        try:
            response = await self._client.beta.messages.create(
                model=request.model,
                max_tokens=request.max_tokens,
                system=request.system,
                messages=messages,
                betas=[SERVER_FALLBACK_BETA],
                extra_body={
                    "fallbacks": "default",
                    "output_config": {"effort": request.effort},
                },
            )
        except anthropic.RateLimitError as exc:
            retry_after = exc.response.headers.get("retry-after")
            raise TransientLLMError(
                "rate limit do provedor", float(retry_after) if retry_after else None
            ) from exc
        except anthropic.APIStatusError as exc:
            if exc.status_code >= 500 or exc.status_code in (408, 409):
                raise TransientLLMError(f"erro {exc.status_code} do provedor") from exc
            raise PermanentLLMError(f"erro {exc.status_code}: {exc.message}") from exc
        except anthropic.APIConnectionError as exc:  # inclui APITimeoutError
            raise TransientLLMError("falha de conexão com o provedor") from exc

        if response.stop_reason == "refusal":
            raise RefusalError("o modelo recusou a solicitação")

        text = "".join(block.text for block in response.content if block.type == "text")
        return LLMResponse(
            text=text,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stop_reason=str(response.stop_reason),
        )
