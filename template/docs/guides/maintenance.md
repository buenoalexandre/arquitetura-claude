# Manutenção

## Rotinas

| Frequência | Atividade | Responsável |
|---|---|---|
| Contínua | Revisar PRs do Dependabot (grupo minor/patch) | Time dev |
| Semanal | Ver o resultado do `security.yml` agendado e tratar CVEs | Plantão |
| Semanal | Revisar métricas de custo, latência, fallback e recusas | Tech lead |
| Mensal | Rodar evals live completos e comparar com o mês anterior | Time IA |
| Mensal | Revisar logs de guardrails para achar novos padrões de ataque e atualizar payloads | Segurança |
| Trimestral | Avaliar modelos novos (evals + custo) e atualizar a tabela de preços em `llm/cost.py` | Time IA |
| Trimestral | Rotacionar segredos e revisar permissões e CODEOWNERS | Plataforma |
| Trimestral | Revisar ADRs com critério de revisão vencido | Arquiteto |
| Semestral | Atualizar dependências major (Python, FastAPI, SDK) | Time dev |

## Atualizando o modelo

1. Leia o guia de migração do provedor: modelos novos podem mudar parâmetros aceitos.
2. Rode `make evals-live` com `APP_LLM__MODEL=<novo>` e compare a taxa de aprovação, o custo e
   a latência.
3. Atualize os preços em `src/app/llm/cost.py`.
4. Faça a mudança por configuração em staging, observe por alguns dias e então promova.

## Atualizando projetos derivados

Projetos criados a partir do template não recebem atualizações automaticamente. Para
incorporar melhorias:

1. Acompanhe o `CHANGELOG.md` do template.
2. Use `python scripts/check_template.py` no projeto derivado para achar lacunas estruturais.
3. Traga as mudanças por PR, com a skill `new-ai-project` no modo de validação.
