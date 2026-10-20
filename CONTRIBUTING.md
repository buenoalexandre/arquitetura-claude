# Como contribuir

1. Abra ou escolha uma issue e combine a abordagem antes de mudanças grandes.
2. Crie uma branch a partir da `main`: `feat/<issue>-<descricao>`.
3. Prepare o ambiente: `make install` (instala dependências e os hooks de pre-commit).
4. Desenvolva com testes. Antes de abrir o PR, rode `make check`.
5. Use Conventional Commits (`feat: ...`, `fix: ...`, `prompt: ...`).
6. Abra o PR usando o template e marque os itens do checklist de IA que se aplicam.

Leitura obrigatória:

- [Fluxo de Git](docs/process/git-workflow.md)
- [Revisão de código](docs/process/code-review.md)
- [Gestão de prompts](docs/ai/prompt-management.md)
- [Regras de código](.claude/rules/code-style.md)

## Usando o Claude Code neste repositório

O `CLAUDE.md` e a pasta `.claude/` já configuram o agente. Comandos úteis: `/review`,
`/fix-issue <n>`, `/new-prompt`, `/run-evals` e `/adr`. Preferências pessoais vão em
`CLAUDE.local.md` e `.claude/settings.local.json`, que não são versionados.
