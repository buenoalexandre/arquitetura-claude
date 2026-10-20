# Template de projetos com IA

Template de referência para iniciar projetos com Inteligência Artificial. Ele já vem com
arquitetura em camadas, gerenciamento de memória, prompts versionados, segurança,
observabilidade, resiliência, testes (incluindo avaliação de respostas do modelo), CI/CD e
toda a configuração do Claude Code.

A arquitetura e a documentação não dependem de uma tecnologia específica. A implementação de
referência usa **Python 3.11+ e FastAPI**. As decisões estão justificadas em
[`docs/architecture/adr/`](docs/architecture/adr/).

## Início rápido

```bash
# 1. Crie um novo projeto a partir do template
python scripts/new_project.py ../meu-projeto --name meu-projeto

# 2. Instale as dependências (uv recomendado; pip também funciona)
cd ../meu-projeto
uv sync                      # ou: python -m venv .venv && pip install -e . --group dev
cp .env.example .env

# 3. Rode os testes e a API (por padrão usa o provedor fake, offline)
make check
make run                     # http://localhost:8000/docs
```

Teste uma conversa:

```bash
curl -s localhost:8000/v1/chat \
  -H "X-API-Key: dev-key-change-me" -H "Content-Type: application/json" \
  -d '{"session_id": "demo", "message": "Olá!"}'
```

Para usar o Claude de verdade, defina `APP_LLM__PROVIDER=anthropic` e `ANTHROPIC_API_KEY` no `.env`.

## Estrutura e finalidade de cada componente

```
.
├── ARQUITETURA.md            Mapa de cada arquivo e pasta: o que é, quando usar, exemplo
├── CLAUDE.md                 Regras gerais do projeto para o Claude Code (versionado)
├── CLAUDE.local.md.example   Modelo de overrides pessoais (o .local.md não é versionado)
├── .mcp.json                 Servidores MCP compartilhados pelo time
├── .worktreeinclude          Arquivos locais copiados para cada git worktree
├── .claude/                  Configuração do Claude Code
│   ├── settings.json         Permissões e hooks do time
│   ├── rules/                Regras por domínio (estilo, testes, API, segurança, prompts...)
│   ├── commands/             Slash commands (/review, /fix-issue, /run-evals, /adr...)
│   ├── skills/               Capacidades sob demanda (new-ai-project, security-review)
│   ├── agents/               Subagentes (architect, code-reviewer, security-auditor...)
│   ├── output-styles/        Estilos de resposta alternativos
│   ├── hooks/                Proteções que sempre rodam (pre_tool_use.py, post_tool_use.py)
│   ├── workflows/            Orquestração multiagente (review-changes.js)
│   └── agent-memory/         Memória própria de cada subagente (<agente>/MEMORY.md)
├── memory/                   Memória do time para o Claude (índice MEMORY.md + fatos)
├── config/                   Configuração não secreta por ambiente (base, dev, staging, prod)
├── prompts/                  Prompts versionados, políticas e registro central
├── src/app/
│   ├── api/                  Camada HTTP: rotas, autenticação e autorização
│   ├── core/                 Config, logs, erros e segurança
│   ├── domain/               Modelos e casos de uso (não dependem de provedor)
│   ├── llm/                  Provedores de LLM, resiliência e custo
│   ├── prompts/              Carregador do registro de prompts
│   ├── memory/               Memória de curto e longo prazo e suas políticas
│   ├── guardrails/           Verificações de entrada e saída (injeção, PII, vazamento)
│   ├── observability/        Métricas, tracing (OpenTelemetry) e auditoria
│   └── container.py          Composição de dependências
├── tests/                    unit, integration, functional, security, performance, evals
├── docs/                     Documentação técnica completa (ver docs/README.md)
├── scripts/                  bootstrap, criação de projeto e validação do checklist
└── .github/                  CI/CD, segurança, evals, Dependabot e templates de PR e issue
```

## Comandos principais

| Comando | O que faz |
|---|---|
| `make install` | Instala dependências e hooks de pre-commit |
| `make lint` | Ruff (lint + formatação) e mypy strict |
| `make test` | Testes offline com cobertura mínima de 80% |
| `make evals` | Evals offline; `make evals-live` usa o modelo real |
| `make security` | bandit, pip-audit e testes de segurança |
| `make check` | lint, testes e validação do template (o mesmo gate do CI) |
| `make run` | API local com recarga automática |

## Documentação

[`ARQUITETURA.md`](ARQUITETURA.md) descreve cada arquivo e pasta do template: o que é, quando
usar e um exemplo. Para os guias, comece por [`docs/README.md`](docs/README.md). Para validar se um projeto segue o padrão,
use o [checklist de validação](docs/checklist/project-validation-checklist.md) e rode
`python scripts/check_template.py`.

## Contribuição e segurança

Veja [CONTRIBUTING.md](CONTRIBUTING.md) e [SECURITY.md](SECURITY.md).
