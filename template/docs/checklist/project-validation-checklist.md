# Checklist de validação de projeto

Use este checklist ao criar um projeto a partir do template, antes do primeiro deploy em
produção e em auditorias periódicas. Os itens marcados com 🤖 são verificados por
`python scripts/check_template.py`. Os demais exigem evidência: um arquivo, um teste, um
workflow ou uma configuração.

Legenda: ✅ atende · ⚠️ parcial (com plano) · ❌ não atende · N/A (justificar em ADR)

## 1. Arquitetura e organização

| # | Item | Evidência esperada |
|---|---|---|
| 1.1 | 🤖 Estrutura de pastas do template presente | `check_template.py` |
| 1.2 | Domínio não importa framework web nem SDK de LLM | `grep -r "import anthropic\|fastapi" src/app/domain` vazio |
| 1.3 | Implementações concretas só em `container.py` | Revisão |
| 1.4 | Desvios do template registrados em ADR | `docs/architecture/adr/` |

## 2. Memória

| # | Item | Evidência esperada |
|---|---|---|
| 2.1 | Memória curta com orçamento de tokens | `memory.short_term_max_tokens` |
| 2.2 | Memória longa com TTL e job de expiração | Config + job agendado |
| 2.3 | Namespace por usuário autenticado | Teste de isolamento |
| 2.4 | Direito ao esquecimento implementado | `DELETE /v1/memory` + teste |
| 2.5 | Política bloqueia memória envenenada e redige PII | `test_policy_*` |

## 3. Regras e instruções

| # | Item | Evidência esperada |
|---|---|---|
| 3.1 | 🤖 Registro de prompts válido, com dono e versões | `prompts/registry.yaml` |
| 3.2 | Nenhum prompt hardcoded no código | Revisão / grep |
| 3.3 | Políticas de comportamento e segurança compostas | `prompts/policies/` |
| 3.4 | 🤖 `CLAUDE.md` enxuto com "Padrões que NÃO usamos" | `check_template.py` |
| 3.5 | Regras do agente em `.claude/rules/` | Pasta presente e atualizada |

## 4. Segurança e governança

| # | Item | Evidência esperada |
|---|---|---|
| 4.1 | Toda rota (exceto health) exige autenticação e permissão | Testes 401/403 |
| 4.2 | 🤖 Nenhum `.env` versionado; `.gitignore` correto | `check_template.py` |
| 4.3 | Segredos em cofre por ambiente; rotação definida | Documento de operação |
| 4.4 | Guardrails de entrada e saída ativos | Testes de segurança |
| 4.5 | Modelo de ameaças revisado para o caso de uso | `docs/security/threat-model.md` |
| 4.6 | Auditoria sem conteúdo bruto, com destino imutável | Config de logs |
| 4.7 | Contrato com o provedor de LLM cobre retenção e treinamento | Jurídico |
| 4.8 | Hooks do Claude Code ativos | `.claude/settings.json` + `test_hooks.py` |

## 5. Testes e qualidade

| # | Item | Evidência esperada |
|---|---|---|
| 5.1 | Cobertura ≥ 80% | CI |
| 5.2 | Testes unitários, de integração, funcionais, de segurança e de desempenho | `tests/` |
| 5.3 | 🤖 Datasets de eval válidos | `check_template.py` |
| 5.4 | Pelo menos 20 casos de eval por prompt em produção | `tests/evals/datasets/` |
| 5.5 | Evals live agendados com taxa mínima | `evals.yml` + `EVAL_MIN_PASS_RATE` |

## 6. Versionamento e colaboração

| # | Item | Evidência esperada |
|---|---|---|
| 6.1 | `main` protegida com checks obrigatórios | Configuração do GitHub |
| 6.2 | 🤖 CODEOWNERS e template de PR | `.github/` |
| 6.3 | Conventional Commits validados | pre-commit + CI |
| 6.4 | `CHANGELOG.md` mantido e releases por tag SemVer | Histórico |

## 7. Documentação

| # | Item | Evidência esperada |
|---|---|---|
| 7.1 | 🤖 README, CONTRIBUTING, SECURITY e docs mínimos | `check_template.py` |
| 7.2 | Guia de instalação testado por alguém novo no time | Feedback registrado |
| 7.3 | Runbook com os cenários do produto | `docs/operations/runbook.md` |

## 8. Configuração e ambientes

| # | Item | Evidência esperada |
|---|---|---|
| 8.1 | 🤖 Configs de development, staging e production | `config/` |
| 8.2 | Validação impede `fake` e segredos padrão fora de dev | `test_config.py` |
| 8.3 | Chaves de LLM separadas por ambiente, com limite de gasto | Console do provedor |

## 9. Integração e automação

| # | Item | Evidência esperada |
|---|---|---|
| 9.1 | 🤖 Workflows de CI, segurança e evals | `.github/workflows/` |
| 9.2 | Análise estática (ruff, mypy, bandit, semgrep, CodeQL) obrigatória | CI |
| 9.3 | Deploy em staging automático; produção com aprovação | `release.yml` + environments |

## 10. Observabilidade

| # | Item | Evidência esperada |
|---|---|---|
| 10.1 | Logs JSON com `correlation_id` | Amostra de log |
| 10.2 | Métricas de latência, erros, tokens e custo | `/v1/metrics` ou painel |
| 10.3 | Traces exportados | `OTEL_EXPORTER_OTLP_ENDPOINT` |
| 10.4 | Alertas configurados | Ferramenta de alertas |

## 11. Tratamento de erros e resiliência

| # | Item | Evidência esperada |
|---|---|---|
| 11.1 | Timeout, retentativas com jitter e circuit breaker | `test_resilience.py` |
| 11.2 | Fallback de modelo validado por evals | Relatório de eval |
| 11.3 | Rate limit por usuário ou tenant em produção | Gateway ou Redis |
| 11.4 | Erros 5xx genéricos, sem detalhes internos | `test_errors_do_not_leak_secrets` |

## 12. Dependências e evolução

| # | Item | Evidência esperada |
|---|---|---|
| 12.1 | `uv.lock` versionado | Repositório |
| 12.2 | Dependabot e `pip-audit` ativos | `.github/` |
| 12.3 | Revisão trimestral de modelos, preços e ADRs | Registro da rotina |

---

**Critério de aprovação para produção:** nenhum ❌ nas seções 4, 5 e 11; no máximo três ⚠️ no
total, cada um com responsável e prazo.
