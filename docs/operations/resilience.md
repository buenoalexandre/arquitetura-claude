# Resiliência e tratamento de erros

## Camadas de proteção (`llm/resilience.py`)

```
requisição
  │
  ├─ 1. Rate limit local (token bucket) ──────── excedeu → 429 rate_limited
  ├─ 2. Circuit breaker por modelo ───────────── aberto → falha rápida
  ├─ 3. Timeout por tentativa (asyncio.timeout)
  ├─ 4. Retentativas: só erros transitórios, backoff exponencial com jitter
  │       esgotou → breaker registra falha
  ├─ 5. Fallback de modelo (local) ───────────── 1 tentativa no fallback_model
  └─ 6. Fallback no servidor para recusas (fallbacks: "default" no provedor)
           se todos falharem → 503 llm_unavailable / 422 llm_refusal
```

## Classificação de erros

| Erro do provedor | Classe interna | Retenta? | Resposta da API |
|---|---|---|---|
| 429 (rate limit) | `TransientLLMError` (com `retry_after`) | Sim | 503 se esgotar |
| 5xx, 408, 409, sobrecarga | `TransientLLMError` | Sim | 503 se esgotar |
| Timeout ou falha de conexão | `TransientLLMError` | Sim | 503 se esgotar |
| 400, 401, 403, 404 | `PermanentLLMError` | Não | 503 (detalhe só no log) |
| `stop_reason = refusal` | `RefusalError` | Não (o fallback no servidor já tentou) | 422 |

As retentativas do SDK ficam desligadas (`max_retries=0`) para não multiplicar tentativas e
custo: a política fica concentrada em um único lugar.

## Parâmetros (`config/*.yaml` → `llm`)

| Parâmetro | Padrão | Ajuste |
|---|---|---|
| `timeout_seconds` | 60 | Menor em rotas interativas; use streaming para respostas longas |
| `max_retries` | 3 | 2 a 4; mais que isso piora a latência no pior caso |
| `retry_wait_base_seconds` | 0,5 | Base do backoff exponencial (máximo de 8 s) |
| `requests_per_minute` | 60 | Abaixo da cota do provedor |
| `circuit_breaker.failure_threshold` | 5 | Falhas consecutivas para abrir |
| `circuit_breaker.reset_timeout_seconds` | 30 | Tempo até a meia-abertura |
| `fallback_model` | `claude-sonnet-5-5` | Modelo de outra família ou região, validado por evals |

## Mecanismos de contingência

- **Degradação elegante:** quando o LLM estiver indisponível, responda 503 com mensagem clara;
  para funcionalidades não críticas, ofereça uma resposta estática ou enfileire o pedido.
- **Fila assíncrona:** cargas que não precisam de resposta imediata (resumos em lote) devem ir
  para uma fila e para a API de batch do provedor, que tem custo menor.
- **Multiprovedor ou multirregião:** um segundo `LLMProvider` (Bedrock, Vertex) como fallback
  exige ADR e evals próprios.
- **Idempotência:** operações com efeito colateral disparadas pelo modelo precisam de chave de
  idempotência, porque as retentativas podem repeti-las.

## Limites de uso

- Por requisição: `guardrails.max_input_chars` e `llm.max_tokens`.
- Por processo: token bucket (`requests_per_minute`).
- Por usuário ou tenant (recomendado em produção): rate limit no API gateway ou em Redis e
  orçamento diário de tokens por tenant.
- Por conta: limite de gasto configurado no console do provedor.
