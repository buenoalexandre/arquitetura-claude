# 0006. OpenTelemetry e logs estruturados

- **Status:** Aceito
- **Data:** 2026-10-20

## Contexto

Falhas em aplicações com IA costumam ser silenciosas: respostas piores, custo crescente,
latência irregular. É preciso correlacionar cada resposta com o prompt, o modelo, os tokens e
o usuário, sem prender o projeto a um fornecedor de observabilidade.

## Decisão

- **Logs:** structlog em JSON, com `correlation_id` em todos os eventos e mascaramento de
  campos sensíveis.
- **Traces:** OpenTelemetry SDK. A exportação é por OTLP, configurável por
  `OTEL_EXPORTER_OTLP_ENDPOINT`.
- **Métricas:** `llm_requests_total`, `llm_latency_ms`, `llm_tokens_total`,
  `llm_cost_usd_total` e `llm_fallback_total`, expostas em `/v1/metrics`. Em produção podem
  migrar para OTel Metrics ou Prometheus mantendo os nomes.
- **Auditoria:** um evento por interação, com hashes no lugar do conteúdo.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| OpenTelemetry (escolhida) | Padrão aberto; aceito por Langfuse, Datadog, Grafana e Jaeger | Mais configuração inicial |
| LangSmith | Ótima visualização de cadeias e prompts | Acoplado ao ecossistema LangChain |
| Langfuse SDK nativo | Feito para LLM, inclui avaliação | Pode ser usado como destino OTLP sem acoplar o código |
| Só logs | Simples | Sem visão de latência distribuída nem de agregados |

## Consequências

- O `docker-compose.yml` sobe o Jaeger para inspecionar traces localmente.

## Critérios de revisão

Quando houver uma convenção semântica estável do OpenTelemetry para GenAI, adote os nomes de
atributos padronizados.
