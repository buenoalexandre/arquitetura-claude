# Testes e qualidade

## Estratégia

```
              ▲  evals live (modelo real, agendado)
             ▲▲▲  performance · segurança
           ▲▲▲▲▲▲  funcionais (API HTTP)
         ▲▲▲▲▲▲▲▲▲  integração (serviço + memória + prompts + fake LLM)
      ▲▲▲▲▲▲▲▲▲▲▲▲▲▲  unitários
```

| Tipo | Comando | Objetivo |
|---|---|---|
| Unitários | `pytest -m unit` | Lógica isolada: config, segurança, resiliência, memória, guardrails, hooks |
| Integração | `pytest -m integration` | Composição dos componentes e contrato do provedor (com cliente dublê) |
| Funcionais | `pytest -m functional` | Contrato HTTP, códigos de erro, propagação do `X-Request-ID` |
| Segurança | `pytest -m security` | Authn/authz, injeção de prompt, vazamento, memória envenenada |
| Desempenho | `pytest -m performance` | p95 da nossa camada abaixo de 100 ms (`PERF_P95_BUDGET_MS`); concorrência sem serialização |
| Evals offline | `make evals` | Datasets e corretores coerentes |
| Evals live | `make evals-live` | Qualidade real do modelo, com taxa mínima de aprovação |

## Testando código de IA sem o modelo

O `FakeProvider` permite:

```python
FakeProvider(responses=["resposta 1", "resposta 2"])  # respostas roteirizadas
FakeProvider(fail_times=2)  # 2 falhas transitórias e depois sucesso
FakeProvider(failing_models={"claude-opus-5-5"})  # força o fallback de modelo
FakeProvider(latency_seconds=0.2)  # força timeout
provider.calls  # inspeciona o que foi enviado
```

Teste o que a **aplicação** controla: o que vai no prompt, o isolamento de memória, as
retentativas, os guardrails e o formato da resposta. A qualidade do texto gerado se mede com
evals.

## Validação das respostas do modelo

Veja [avaliação](../ai/evaluation.md). Resumo: corretores determinísticos primeiro; LLM como
juiz só para critérios subjetivos; datasets versionados; taxa mínima de aprovação no CI
agendado.

## Testes de carga

Os testes de desempenho medem só a sobrecarga da aplicação. Para carga ponta a ponta, use
Locust ou k6 em homologação, com cota de gasto definida e o provedor real ou um mock de rede
com latência realista. Metas sugeridas: p95 < 2 s para respostas curtas, taxa de erro < 1% e
nenhum 5xx por estouro de rate limit interno.

## Cobertura

O mínimo é 80% de linhas e ramos (`--cov-fail-under=80`). Cobertura é um piso, não uma meta: um
teste sem asserções relevantes não conta na revisão.
