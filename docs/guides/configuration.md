# Configuração e ambientes

## Modelo de camadas

```
config/base.yaml              valores comuns (versionado)
  └─ config/<APP_ENV>.yaml    diferenças por ambiente (versionado)
       └─ .env                 valores locais (NÃO versionado)
            └─ variáveis APP_*  definidas pela plataforma (maior precedência)
```

A classe `Settings` (`src/app/core/config.py`) valida tudo na inicialização: a aplicação não
sobe com configuração inválida. Para chaves aninhadas, use `__`:
`APP_LLM__MODEL=claude-sonnet-5-5` sobrescreve `llm.model`.

## Ambientes

| | development | test | staging (homologação) | production |
|---|---|---|---|---|
| Provedor LLM | `fake` | `fake` | `anthropic` | `anthropic` |
| Logs | texto, DEBUG | — | JSON, INFO | JSON, WARNING |
| Rate limit (req/min) | 600 | definido nos testes | 120 | 600 |
| Retenção de memória | 90 dias | — | 90 dias | 30 dias |
| Segredos | `.env` local | fixtures | cofre | cofre |
| Validações extras | — | — | proíbe `fake` e segredo padrão | proíbe `fake` e segredo padrão |

## Segredos

- **Nunca** coloque segredos em `config/*.yaml`, no código ou em testes. O hook
  `block_secrets.py`, o gitleaks e o pre-commit bloqueiam isso.
- Em produção, injete-os como variáveis de ambiente a partir de um cofre: AWS Secrets
  Manager, GCP Secret Manager, Azure Key Vault, HashiCorp Vault ou os secrets do GitHub
  Environments.
- Faça a rotação de `ANTHROPIC_API_KEY`, `APP_SECURITY__JWT_SECRET` e das API keys pelo menos a
  cada 90 dias, e imediatamente em caso de suspeita de vazamento.
- Use chaves de LLM diferentes por ambiente, com limites de gasto configurados no provedor.

## Variáveis principais

| Variável | Descrição | Exemplo |
|---|---|---|
| `APP_ENV` | Ambiente ativo | `staging` |
| `APP_LLM__PROVIDER` | `fake` ou `anthropic` | `anthropic` |
| `APP_LLM__MODEL` | Modelo principal | `claude-opus-5-5` |
| `APP_LLM__FALLBACK_MODEL` | Modelo usado quando o principal se esgota | `claude-sonnet-5-5` |
| `APP_LLM__EFFORT` | Esforço de raciocínio (`low` a `max`) | `medium` |
| `ANTHROPIC_API_KEY` | Chave do provedor | (cofre) |
| `APP_SECURITY__API_KEYS` | `chave:papel` separados por vírgula | (cofre) |
| `APP_SECURITY__JWT_SECRET` | Segredo de assinatura dos JWT | (cofre) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Destino dos traces | `http://otel-collector:4318/v1/traces` |

## Adicionando uma configuração

1. Crie o campo no bloco certo de `Settings`, com tipo e valor padrão seguro.
2. Se varia por ambiente, coloque o valor em `config/<env>.yaml`.
3. Se é segredo, adicione-o somente ao `.env.example` (vazio) e documente-o nesta página.
4. Adicione um teste em `tests/unit/test_config.py`.
