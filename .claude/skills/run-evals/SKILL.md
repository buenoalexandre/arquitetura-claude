---
name: run-evals
description: Roda os evals de qualidade e resume regressões
argument-hint: "[offline|live]"
disable-model-invocation: true
---

Rode os evals no modo `$ARGUMENTS` (padrão: offline).

- offline: `make evals`. Valida os datasets e os corretores, sem custo.
- live: confirme com o usuário antes de rodar, porque gasta tokens. Depois rode
  `make evals-live`; o relatório fica em `tests/evals/reports/`.

Resuma a taxa de aprovação, os casos que falharam (id, critério violado e trecho da saída) e
a comparação com o relatório anterior, se houver. Sugira se a falha é do prompt, do dataset ou
do corretor. Não altere os datasets só para fazer os testes passarem.
