---
name: review
description: Revisa as mudanças atuais (ou um PR) procurando bugs, riscos de IA e desvios de padrão
argument-hint: "[número do PR ou branch]"
disable-model-invocation: true
---

Revise as mudanças de $ARGUMENTS (se vazio, use `git diff main...HEAD`).

1. Delegue a revisão de código ao subagente `code-reviewer` e, se o diff tocar `src/app/core/`,
   `src/app/guardrails/`, `prompts/` ou `.github/`, também ao `security-auditor`.
2. Verifique as regras de `.claude/rules/` relevantes para os arquivos alterados.
3. Confirme que há testes para o comportamento novo e que `make check` passa.
4. Se houver mudança de prompt, confirme que é uma versão nova e que os evals foram atualizados.

Responda no estilo `code-reviewer`: achados ordenados por severidade, cada um com
`arquivo:linha`, o problema, o cenário concreto de falha e a correção sugerida. Se não houver
achados, diga isso explicitamente.
