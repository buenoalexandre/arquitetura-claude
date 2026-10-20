# Modelo de ameaças

Baseado no OWASP Top 10 para aplicações com LLM (2025) e no STRIDE para a parte web.

## Ativos

Dados pessoais dos usuários (conversas e memória), prompts de sistema (propriedade
intelectual), chaves de provedor e de API, disponibilidade do serviço e orçamento de tokens.

## Fronteiras de confiança

```
[Usuário] ─HTTP─► [API: authn/authz] ─► [ChatService] ─► [Provedor LLM externo]
                                            │
                                 [Memória] [Prompts] [Logs/Auditoria]
```

Tudo que cruza a seta para dentro (entrada do usuário, documentos, respostas do modelo,
resultados de ferramentas) é **não confiável**.

## Riscos e mitigações

| OWASP LLM | Ameaça | Mitigação no template | Evidência |
|---|---|---|---|
| LLM01 Injeção de prompt | Usuário ou documento manipula instruções | Heurísticas de entrada, conteúdo rotulado como dado, política de segurança no prompt | `guardrails/input.py`, `tests/security/` |
| LLM02 Divulgação de informação sensível | Vazamento de PII ou de dados de outro usuário | Namespace por usuário, redação de PII, guardrail de saída, auditoria sem conteúdo | `chat_service.py`, `test_sessions_are_isolated_between_users` |
| LLM03 Cadeia de suprimentos | Dependência ou action comprometida | pip-audit, Dependabot, CodeQL, actions com versão fixa | `security.yml` |
| LLM04 Envenenamento de dados ou modelo | Memória envenenada com instruções | `MemoryPolicy` bloqueia padrões de injeção | `test_poisoned_memory_is_rejected` |
| LLM05 Tratamento inadequado da saída | Saída usada como código, SQL ou HTML | A saída é texto; quem consome deve escapar. Saída estruturada validada por schema | `api-conventions.md` |
| LLM06 Agência excessiva | Modelo aciona ação destrutiva | Sem ferramentas por padrão; regra de allowlist e confirmação humana | `rules/security.md` |
| LLM07 Vazamento do prompt de sistema | Extração de instruções internas | Política no prompt + detecção na saída | `test_model_echoing_system_prompt_is_masked` |
| LLM08 Fragilidades de vetores e embeddings | Recuperação cruzada entre tenants | Filtro obrigatório por namespace no `LongTermStore` | `memory/long_term.py` |
| LLM09 Desinformação | Alucinação apresentada como fato | Política de honestidade, evals de honestidade e fidelidade | `datasets/*.jsonl` |
| LLM10 Consumo sem limites | DoS de custo | Rate limit, `max_tokens`, tamanho de entrada, circuit breaker | `llm/resilience.py` |

## Riscos web (STRIDE resumido)

| Ameaça | Mitigação |
|---|---|
| Spoofing | API key com comparação em tempo constante; JWT com expiração obrigatória |
| Tampering | JWT assinado; validação Pydantic de toda entrada |
| Repudiation | Auditoria por ator, ação e recurso, com `correlation_id` |
| Information disclosure | Erros 5xx genéricos; mascaramento de campos sensíveis nos logs |
| Denial of service | Rate limit, timeouts, limites de tamanho |
| Elevation of privilege | RBAC com permissões explícitas por rota |

## Riscos residuais aceitos

- Heurísticas de injeção não pegam tudo → classificador dedicado recomendado para dados
  sensíveis.
- O rate limit em memória vale por réplica → em produção, use rate limit no gateway ou em Redis.
- A detecção de PII por regex é imperfeita → Presidio recomendado para dados regulados.

Revise este documento a cada nova capacidade (RAG, ferramentas, multiagente) e no mínimo a
cada seis meses.
