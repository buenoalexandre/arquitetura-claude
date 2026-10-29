# Regras de memória

Há dois tipos de memória, que não devem ser confundidos:

1. **Memória da aplicação** (`src/app/memory/`): o que o produto lembra dos usuários finais.
   Estratégia em `docs/ai/memory-strategy.md`.
2. **Memória do Claude Code** (`memory/`): o que o agente de desenvolvimento lembra sobre o
   projeto e o time.

## Memória da aplicação

- Curto prazo: janela por orçamento de tokens. Longo prazo: fatos e preferências com TTL.
- Todo registro passa por `MemoryPolicy` (rejeita injeção e redige PII).
- O namespace é sempre o usuário autenticado. Nenhuma consulta cruza namespaces.
- O direito ao esquecimento (`DELETE /v1/memory`) apaga a memória curta e a longa.

## Memória do Claude Code (`memory/`)

- `memory/MEMORY.md` é o índice, com uma linha por fato. Cada fato fica em
  `memory/<slug>.md`, com frontmatter `name`, `description` e `metadata.type` (`user`,
  `feedback`, `project` ou `reference`).
- Registre decisões e preferências que **não** estão no código nem no git: o motivo de uma
  escolha, restrições externas, acordos do time.
- Fatos de `feedback` e `project` levam as linhas **Why:** e **How to apply:**.
- Atualize o fato existente em vez de criar um duplicado. Apague memórias que ficaram falsas.
- Memória pessoal fica fora do repositório (`~/.claude/`), não em `memory/`.

## Memória por subagente (`.claude/agent-memory/<agente>/`)

- Subagentes com `memory: project` no frontmatter (`code-reviewer`, `security-auditor`)
  guardam o que aprendem em `.claude/agent-memory/<agente>/MEMORY.md` + um arquivo por fato,
  no mesmo formato de `memory/`.
- Use para conhecimento que só interessa àquele especialista (padrões recorrentes de achados,
  falsos positivos conhecidos). Conhecimento do time inteiro vai para `memory/`.
