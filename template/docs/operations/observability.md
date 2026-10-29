# Observabilidade e monitoramento

## Três sinais + auditoria

| Sinal | Implementação | Onde ver |
|---|---|---|
| Logs | structlog JSON, `correlation_id` em todos os eventos | stdout → coletor (Loki, CloudWatch, Datadog) |
| Métricas | `observability/metrics.py`, exposto em `GET /v1/metrics` (admin) | Painel / Prometheus / OTel |
| Traces | OpenTelemetry, span `chat` com atributos | Jaeger local (`make docker`), Langfuse, Tempo |
| Auditoria | Logger `audit`, um evento por interação | Armazenamento imutável |

## Métricas de IA

| Métrica | Labels | Para quê |
|---|---|---|
| `llm_requests_total` | `model`, `status` (`ok`, `timeout`, `transient_error`, `circuit_open`, `rate_limited`) | Taxa de erro por modelo |
| `llm_latency_ms` (p50, p95, máx.) | `model` | Latência do provedor |
| `llm_tokens_total` | `kind` (`input`, `output`) | Volume e tendência de contexto |
| `llm_cost_usd_total` | `model` | Gasto estimado |
| `llm_fallback_total` | `model` | Instabilidade do modelo principal |

Logs relevantes: `http_request` (método, rota, status, `duration_ms`), `llm_fallback`,
`app_error` (código e detalhe interno) e `audit_event`.

## Alertas sugeridos

| Alerta | Condição | Severidade |
|---|---|---|
| Erros do LLM | `status != ok` > 5% em 5 min | Alta |
| Circuit breaker aberto | Qualquer `circuit_open` | Alta |
| Latência | p95 de `llm_latency_ms` > 2× o baseline por 15 min | Média |
| Custo | `llm_cost_usd_total` diário > 120% da média de 7 dias | Média |
| Fallback | `llm_fallback_total` > 1% das requisições | Média |
| Guardrails | Pico de `injection:*` nos eventos de auditoria | Média (possível ataque) |
| Qualidade | Taxa de aprovação dos evals agendados abaixo do limite | Alta |

## Painel mínimo

1. Requisições por minuto e taxa de erro (HTTP e LLM)
2. Latência p50/p95 (HTTP total vs. LLM)
3. Tokens de entrada e saída por minuto; custo acumulado do dia
4. Estado do circuit breaker e quantidade de fallbacks
5. Distribuição por `prompt_version` e por `model`

## Rastreando uma requisição

1. Pegue o `x-request-id` da resposta (ou peça ao usuário).
2. Filtre os logs por `correlation_id`.
3. No evento `audit_event`, veja `prompt_version`, `prompt_sha`, `model`, tokens, custo e flags.
4. No trace, veja a duração de cada etapa.
