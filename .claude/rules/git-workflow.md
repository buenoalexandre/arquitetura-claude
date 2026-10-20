# Git e Pull Requests

O processo completo está em `docs/process/git-workflow.md`.

- Fluxo: GitHub Flow. A `main` é protegida e sempre implantável; o trabalho acontece em
  branches curtas.
- Nome da branch: `<tipo>/<issue>-<descricao-curta>` (ex.: `feat/42-memoria-redis`).
- Commits no padrão Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`,
  `chore:`, `ci:`, `perf:`, `prompt:` (mudança de prompt). Mudança incompatível: `feat!:` ou o
  rodapé `BREAKING CHANGE:`.
- Um PR resolve um assunto, com até ~400 linhas alteradas, e usa o template de PR.
- Merge por squash, depois de CI verde e de 1 aprovação (2 para `src/app/core/security.py`,
  `prompts/` e `.github/`, conforme `CODEOWNERS`).
- O agente só faz commit ou push quando o usuário pede. Nunca reescreve histórico publicado.
