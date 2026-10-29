arp# Arquitetura de um Projeto Claude Code — Modelo de Referência

Este documento é um **template genérico e reutilizável** que descreve toda a estrutura de
arquivos/pastas que um projeto usando Claude Code pode ter, o propósito de cada item e um exemplo
mínimo de conteúdo. Use-o como checklist ao iniciar um novo projeto ou ao organizar um existente.

Nem todo projeto precisa de todos os itens — comece pelo essencial (`CLAUDE.md`,
`.claude/settings.json`) e adicione o resto conforme a necessidade aparecer.

## Visão geral da árvore

```
projeto/
├── CLAUDE.md                     # regras gerais do projeto + memória entre sessões
├── .mcp.json                     # servidores MCP do projeto
├── .worktreeinclude               # arquivos compartilhados entre worktrees/sessões paralelas
├── .gitignore                     # ignora o que é local/pessoal
│
└── .claude/
    ├── settings.json               # permissões e config compartilhadas (versionado)
    ├── settings.local.json         # overrides pessoais (não versionado)
    │
    ├── rules/                      # regras por domínio, referenciadas pelo CLAUDE.md
    │   ├── testing.md
    │   └── api-design.md
    │
    ├── skills/                     # capacidades reutilizáveis invocáveis sob demanda
    │   ├── security-review/
    │   │   ├── SKILL.md
    │   │   └── checklist.md
    │   └── fix-issue/              # skill manual (/fix-issue), com disable-model-invocation
    │       └── SKILL.md
    │
    ├── agents/                     # definições de subagentes especializados
    │   └── code-reviewer.md
    │
    ├── output-styles/              # estilos de saída alternativos
    │   └── code-reviewer.md
    │
    ├── hooks/                      # scripts acionados em eventos do ciclo de vida
    │   └── pre-tool-use.sh
    │
    └── workflows/                  # scripts de orquestração multi-agente
        └── review-changes.js

memory/  (ou agent-memory/<agent>/)
├── MEMORY.md                       # índice: uma linha por fato, carregado toda sessão
└── <fato>.md                       # um arquivo por memória, com frontmatter
```

---

## Raiz do projeto

### `CLAUDE.md`
**O que é:** o arquivo central de instruções do projeto. É carregado automaticamente no início de
toda sessão e funciona como a "memória de longo prazo" e o manual de regras gerais que o Claude
deve seguir ali.

**Quando usar:** sempre. É o primeiro lugar que o Claude lê para entender convenções do projeto,
comandos de build/test, estilo de código e onde encontrar mais contexto (apontando para
`rules/*.md` em vez de duplicar conteúdo).

**Exemplo:**
```markdown
# Projeto X

## Comandos
- Build: `npm run build`
- Testes: `npm test`

## Convenções
- Ver [[rules/api-design]] para padrões de API.
- Ver [[rules/testing]] para como escrever testes.

## Notas
- O banco de dev usa dados fake, nunca produção.
```

### `.mcp.json`
**O que é:** arquivo de configuração dos servidores **MCP (Model Context Protocol)** vinculados ao
projeto — a forma padrão de conectar a LLM a ferramentas/serviços de terceiros (bancos de dados,
APIs internas, Jira, Slack etc.).

**Quando usar:** quando o projeto depende de integrações externas que devem estar disponíveis para
qualquer pessoa que abrir o projeto (diferente de servidores MCP pessoais, configurados fora do
repo).

**Exemplo:**
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
    }
  }
}
```

### `.worktreeinclude`
**O que é:** lista de arquivos/pastas que devem ser compartilhados entre `git worktree`s distintos,
permitindo que múltiplas sessões do Claude trabalhem em paralelo (branches diferentes) mas
enxerguem certos arquivos em comum (ex.: `.env`, configs locais, `node_modules` symlinkado).

**Quando usar:** em projetos onde você roda sessões paralelas em worktrees separadas e quer evitar
duplicar setup/config em cada uma.

**Exemplo:**
```
.env
.claude/settings.local.json
```

### `.gitignore` (recomendado)
**O que é:** garante que arquivos pessoais/locais não vão parar no repositório compartilhado.

**Exemplo de entradas relevantes:**
```
.claude/settings.local.json
memory/
*.local.json
```

---

## `.claude/`

### `settings.json`
**O que é:** configurações **compartilhadas** do projeto — permissões de ferramentas (o que pode
rodar sem perguntar), hooks ativos, modelo padrão, etc. Fica versionado no git, então vale para
todo mundo que clona o projeto.

**Quando usar:** para padronizar permissões seguras do time (ex.: permitir `git status`, `npm test`
sem prompt) e configurar hooks do projeto.

**Exemplo:**
```json
{
  "permissions": {
    "allow": ["Bash(git status)", "Bash(npm test)"]
  }
}
```

### `settings.local.json`
**O que é:** faz **override** do `settings.json` com preferências pessoais da máquina/usuário atual.
Não deve ser versionado (cada dev tem o seu).

**Quando usar:** para permissões ou configs que só fazem sentido para você (ex.: um allowlist mais
permissivo na sua máquina de dev).

---

### `rules/`
**O que é:** arquivos markdown com regras específicas por domínio/tópico, referenciados a partir do
`CLAUDE.md` em vez de inflar um único arquivo gigante.

**Quando usar:** quando uma regra é longa ou específica demais para caber direto no `CLAUDE.md`
(ex.: convenções de teste, padrões de design de API, guia de estilo).

**Exemplo — `rules/testing.md`:**
```markdown
# Regras de Teste

- Todo endpoint novo precisa de teste de integração.
- Use fixtures em `tests/fixtures/`, nunca dados de produção.
```

### `skills/`
**O que é:** capacidades empacotadas e reutilizáveis, invocadas sob demanda quando a tarefa casa com
a descrição da skill (ou explicitamente via `/nome-da-skill`). Cada skill vive em sua própria pasta
com um `SKILL.md` (instruções) e arquivos de apoio opcionais (checklists, scripts, templates).

**Quando usar:** para empacotar um processo repetível e complexo (ex.: checklist de revisão de
segurança, fluxo de deploy) que deve ser carregado só quando relevante — mantendo o `CLAUDE.md`
enxuto.

**Exemplo — `skills/security-review/SKILL.md`:**
```markdown
---
name: security-review
description: Checklist de revisão de segurança para PRs que tocam autenticação ou dados sensíveis.
---

Ao revisar mudanças de segurança, siga o checklist em `checklist.md` e reporte achados por
severidade.
```

#### Skills acionadas manualmente (antigos slash commands)
**O que é:** skills com `disable-model-invocation: true` no frontmatter — atalhos que o usuário
digita (`/fix-issue`) para disparar um prompt/fluxo pré-definido. Substituem a antiga pasta
`commands/`.

**Quando usar:** para ações que o usuário aciona manualmente e com frequência (ex.: `/fix-issue`,
`/release-notes`), diferente das skills sem essa flag, que o Claude carrega sozinho conforme o
contexto da tarefa.

**Exemplo — `skills/fix-issue/SKILL.md`:**
```markdown
---
name: fix-issue
description: Corrige uma issue com teste de regressão
disable-model-invocation: true
---

Corrija a issue #$ARGUMENTS: leia a issue, reproduza o bug, escreva um teste que falhe, corrija o
código e rode a suíte de testes antes de finalizar.
```

### `agents/`
**O que é:** definições de **subagentes** especializados (usados pela ferramenta `Agent`/`Task`),
com prompt de sistema, ferramentas permitidas e critérios de quando usar cada um.

**Quando usar:** quando você quer delegar um tipo de tarefa recorrente a um agente com contexto e
restrições próprias (ex.: um `code-reviewer` que só lê código e reporta achados, sem editar
arquivos).

**Exemplo — `agents/code-reviewer.md`:**
```markdown
---
name: code-reviewer
description: Revisa diffs em busca de bugs de correção e oportunidades de simplificação.
tools: Read, Grep, Glob
---

Você é um revisor de código sênior. Foque em bugs reais, não em estilo.
```

### `output-styles/`
**O que é:** define formatos alternativos de como o Claude formata suas respostas (tom, estrutura),
selecionáveis por comando/config.

**Quando usar:** quando diferentes contextos de uso (ex.: revisão de código vs. pair programming)
pedem um estilo de resposta diferente do padrão.

### `hooks/`
**O que é:** scripts acionados automaticamente em eventos do ciclo de vida de uma sessão/ferramenta
(`PreToolUse`, `PostToolUse`, `Stop`, etc.), configurados via `settings.json`.

**Quando usar:** para automatizar validações ou ações obrigatórias (ex.: rodar linter antes de todo
`Edit`, bloquear certos comandos, notificar ao final de uma tarefa).

### `workflows/`
**O que é:** scripts de orquestração multi-agente (usados pela ferramenta `Workflow`) que coordenam
vários subagentes de forma determinística — fan-out, pipelines, verificação adversarial.

**Quando usar:** para tarefas grandes que se beneficiam de paralelismo estruturado (ex.: revisão de
segurança abrangente, migração em massa) — normalmente só quando o usuário pede explicitamente
orquestração multi-agente.

---

## Memória (`memory/` ou `agent-memory/<agent-name>/`)

### `MEMORY.md`
**O que é:** índice de todas as memórias persistentes, uma linha por fato, carregado a cada sessão
para dar contexto rápido sem precisar ler todos os arquivos de memória.

**Exemplo:**
```markdown
- [Preferência de testes](prefere-testes-unitarios.md) — sempre unitário antes de integração.
```

### `<fato>.md`
**O que é:** um arquivo por fato memorizado (preferência do usuário, decisão de projeto, referência
externa), com frontmatter padronizado.

**Exemplo:**
```markdown
---
name: prefere-testes-unitarios
description: Usuário prefere testes unitários antes de integração.
metadata:
  type: feedback
---

O usuário prefere que testes unitários sejam escritos antes dos de integração.
**Why:** feedback dado após PR onde só havia testes de integração.
**How to apply:** ao adicionar testes, priorizar cobertura unitária primeiro.
```

---

## Boas práticas

- **O que versionar vs. manter local:** `settings.json`, `rules/`, `skills/`,
  `agents/` e `CLAUDE.md` vão para o git (são conhecimento do time). `settings.local.json` e
  memórias pessoais ficam fora do controle de versão — são específicos de cada desenvolvedor/máquina.
- **Convenção de nomes:** use kebab-case em todos os arquivos e slugs (`security-review`,
  `fix-issue`, `prefere-testes-unitarios`).
- **`CLAUDE.md` enxuto:** ele deve **referenciar** `rules/*.md` (via link ou `[[nome]]`) em vez de
  duplicar o conteúdo — isso evita que o arquivo principal cresça demais e fique difícil de manter.
- **`skills/` vs. `agents/`:**
  - **skills** → descobertas automaticamente pelo Claude quando a tarefa casa com a descrição;
    ideal para processos complexos e reutilizáveis.
  - **skills com `disable-model-invocation: true`** (antigos `commands/`) → disparadas
    manualmente pelo usuário via `/nome`; ideal para ações pontuais e frequentes.
  - **agents** → subagentes com prompt/ferramentas próprias, usados para delegar partes de uma
    tarefa maior (via `Agent`/`Task`), mantendo contexto isolado.
