# Visão geral da arquitetura

## Objetivos

1. **Independência de provedor**: o domínio não sabe qual LLM está sendo usado.
2. **Segurança por padrão**: autenticação, guardrails, isolamento de dados e auditoria estão
   no caminho principal, não são opcionais.
3. **Testabilidade**: tudo roda offline com um provedor fake determinístico.
4. **Operabilidade**: cada chamada ao modelo produz logs, métricas, traces e registro de custo.
5. **Evolução segura**: prompts e decisões são versionados; mudanças passam por evals e ADRs.

## Camadas

```
┌──────────────────────────────────────────────────────────────────┐
│ api/          HTTP · validação · autenticação · RBAC · erros     │
├──────────────────────────────────────────────────────────────────┤
│ domain/       modelos · casos de uso (ChatService)               │
├───────────┬───────────┬────────────┬────────────┬────────────────┤
│ llm/      │ memory/   │ prompts/   │ guardrails/│ observability/ │
│ provedor  │ curto e   │ registro   │ entrada e  │ logs, métricas │
│ resiliên. │ longo     │ versionado │ saída      │ traces, audit. │
│ custo     │ prazo     │            │            │                │
├───────────┴───────────┴────────────┴────────────┴────────────────┤
│ core/         configuração · logging · erros · segurança         │
└──────────────────────────────────────────────────────────────────┘
          container.py: monta as implementações concretas
```

**Regra de dependência:** as setas apontam para baixo. `domain` não importa `fastapi` nem SDKs
de LLM. Somente `container.py` instancia classes concretas. Isso permite trocar o provedor, o
armazenamento de memória ou o framework web sem tocar nos casos de uso.

## Fluxo de uma requisição `POST /v1/chat`

```
Cliente
  │  X-API-Key ou Bearer JWT, X-Request-ID
  ▼
Middleware ── correlation_id nos logs e no cabeçalho de resposta
  ▼
require("chat:write") ── autenticação + RBAC                        → 401/403
  ▼
ChatService.chat
  1. check_input ── tamanho, injeção de prompt, PII                 → 400
  2. PromptRegistry.render ── prompt ativo + políticas + hash
  3. LongTermStore.search ── fatos do usuário, rotulados como dados
  4. ShortTermStore.window ── histórico dentro do orçamento de tokens
  5. ResilientLLMClient.complete
       rate limit → circuit breaker → timeout → retry c/ jitter      → 429/503
       → fallback de modelo (local) / fallback no servidor (recusas)
  6. check_output ── vazamento de prompt e PII não fornecida
  7. memória curta atualizada (com PII redigida)
  8. custo estimado, métricas e evento de auditoria (sem conteúdo bruto)
  ▼
ChatResponse { reply, model, prompt_version, usage, guardrail_flags }
```

## Componentes e responsabilidades

| Componente | Arquivo | Responsabilidade | Ponto de extensão |
|---|---|---|---|
| Configuração | `core/config.py` | Camadas YAML + env, validação por ambiente | Novos blocos de settings |
| Segurança | `core/security.py` | API key, JWT, papéis e permissões | Integração com IdP (OIDC) |
| Provedor LLM | `llm/provider.py` | Contrato `LLMProvider` | Novas implementações |
| Resiliência | `llm/resilience.py` | Retry, timeout, breaker, rate limit, fallback | Limites por rota ou tenant |
| Prompts | `prompts/loader.py` | Registro versionado, renderização, hash | Prompts por tenant ou idioma |
| Memória | `memory/` | Curto prazo, longo prazo, políticas | Redis, pgvector, Qdrant |
| Guardrails | `guardrails/` | Injeção, PII, vazamento | Classificadores dedicados |
| Observabilidade | `observability/` | Métricas, traces (OTel), auditoria | Exportadores OTLP ou Prometheus |

## Como estender

- **Novo provedor:** implemente `LLMProvider.complete` em `llm/<nome>_provider.py`, mapeando os
  erros para `TransientLLMError`, `PermanentLLMError` e `RefusalError`, e registre-o em
  `container.build_provider`. Escreva testes de contrato como em
  `tests/integration/test_anthropic_provider.py`.
- **RAG:** crie `src/app/retrieval/` com um contrato `Retriever` e injete-o no `ChatService`.
  Os documentos recuperados entram no prompt delimitados e rotulados como dados.
- **Ferramentas (tool use):** cada ferramenta tem schema estrito, allowlist por papel e, se
  houver efeito colateral, confirmação humana. Veja `docs/security/threat-model.md` (LLM06).

## Índice de ADRs

| ADR | Decisão | Status |
|---|---|---|
| [0001](adr/0001-registrar-decisoes.md) | Registrar decisões em ADRs | Aceito |
| [0002](adr/0002-stack-python-fastapi.md) | Python + FastAPI como stack de referência | Aceito |
| [0003](adr/0003-abstracao-provedor-llm.md) | Abstração própria de provedor, sem framework de orquestração | Aceito |
| [0004](adr/0004-prompts-versionados.md) | Prompts versionados em arquivos com registro central | Aceito |
| [0005](adr/0005-memory-strategy.md) | Memória em dois níveis com políticas explícitas | Aceito |
| [0006](adr/0006-observabilidade-opentelemetry.md) | OpenTelemetry e logs estruturados | Aceito |
