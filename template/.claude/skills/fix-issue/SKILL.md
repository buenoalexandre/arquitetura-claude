---
name: fix-issue
description: Corrige uma issue com teste de regressão e causa raiz documentada
argument-hint: "<número da issue>"
disable-model-invocation: true
---

Corrija a issue #$ARGUMENTS como um engenheiro sênior de debugging:

1. Leia a issue (`gh issue view $ARGUMENTS`) e reproduza o problema.
2. Escreva um teste que falhe e demonstre o bug.
3. Encontre a causa raiz, não só o sintoma. Considere os casos extremos.
4. Corrija com a menor mudança correta e rode `make check`.
5. Crie a branch `fix/$ARGUMENTS-<descricao>` e prepare uma mensagem de commit
   `fix: ... (#$ARGUMENTS)`. Não faça commit nem push sem pedir.

No final, informe: o que falhava, por quê, a correção aplicada e os casos extremos cobertos.
