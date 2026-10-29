---
name: new-prompt
description: Cria uma nova versão de prompt seguindo o processo de versionamento
argument-hint: "<nome-do-prompt> <objetivo da mudança>"
disable-model-invocation: true
---

Crie uma nova versão do prompt descrito em: $ARGUMENTS

1. Leia `prompts/registry.yaml` e a versão ativa atual. Se o prompt não existir, crie a `v1`.
2. Crie `prompts/<pasta>/<nome>.v<N+1>.md`. **Não edite a versão anterior.**
3. Registre a versão no `registry.yaml` com `variables`, `policies` e `changelog`. Mantenha
   `active` na versão anterior.
4. Adicione ou ajuste casos em `tests/evals/datasets/<nome>.jsonl` cobrindo o objetivo.
5. Rode `make evals`. Se houver chave disponível e o usuário autorizar o custo, rode
   `make evals-live`.
6. Apresente a comparação entre as versões e pergunte se deve trocar `active`.

Siga `.claude/rules/prompts.md` (use o subagente `prompt-engineer` para revisar o texto).
