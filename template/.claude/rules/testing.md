# Regras de teste

## Pirâmide e marcas

| Pasta | Marca | O que cobre | Roda no CI |
|---|---|---|---|
| `tests/unit` | `unit` | Funções e classes isoladas | Todo PR |
| `tests/integration` | `integration` | Serviço + memória + prompts + LLM fake | Todo PR |
| `tests/functional` | `functional` | API HTTP ponta a ponta | Todo PR |
| `tests/security` | `security` | Authn/authz, injeção de prompt, vazamentos | Todo PR |
| `tests/performance` | `performance` | Sobrecarga da aplicação (p95) | Todo PR |
| `tests/evals` | `evals` | Qualidade das respostas (datasets JSONL) | Offline em PR; live agendado |
| qualquer | `live` | Chama o provedor real | Só em `evals.yml` |

## Regras

- Todo bug corrigido ganha um teste que falhava antes da correção.
- Testes não acessam rede. Use `FakeProvider` (respostas roteirizadas e injeção de falhas).
- Cobertura mínima: 80% (`--cov-fail-under`). Não baixe o limite para fazer o CI passar.
- Mudou prompt ou modelo? Adicione ou ajuste casos em `tests/evals/datasets/` antes de mudar
  a versão ativa.
- Novo padrão de ataque visto em produção ou red team? Inclua em
  `tests/security/injection_payloads.json`.
- Use fixtures de `tests/conftest.py`. Nunca use dados reais de clientes em fixtures.
