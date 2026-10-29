---
name: provedor-fake-por-padrao
description: Desenvolvimento e CI usam o FakeProvider; chamadas reais só com a marca live
metadata:
  type: project
---

O ambiente de desenvolvimento e o CI de PR usam `APP_LLM__PROVIDER=fake`. Testes que chamam o
modelo real levam `@pytest.mark.live` e só rodam no workflow `evals.yml`.

**Why:** testes com modelo real são lentos, custam dinheiro e não são determinísticos, o que
gerava CI instável e gasto inesperado.

**How to apply:** ao escrever testes, use `FakeProvider(responses=..., fail_times=...)`. Para
validar qualidade de verdade, adicione casos em `tests/evals/datasets/`. Ver [[prompts-imutaveis]].
