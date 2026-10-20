# CLAUDE.md

Este arquivo é carregado no início de toda sessão do Claude Code. Ele traz a visão geral do
projeto e aponta para as regras detalhadas, sem duplicá-las. Mantenha-o curto: se uma seção
passar de ~15 linhas, mova o conteúdo para `.claude/rules/`.

## Projeto

API de referência para aplicações com IA (FastAPI + Python 3.11+). O domínio não conhece o
provedor de LLM. Toda chamada ao modelo passa por guardrails, resiliência, memória,
auditoria e métricas. A arquitetura está em `docs/architecture/overview.md`.

## Comandos

- Instalar: `make install`
- Validar tudo (o mesmo gate do CI): `make check`
- Testes: `make test` · Evals offline: `make evals` · Evals com o modelo real: `make evals-live`
- Lint e tipos: `make lint`
- Rodar a API: `make run` (provedor `fake` por padrão, não gasta tokens)

## Mapa do código

- `src/app/api/`: HTTP, autenticação e RBAC. Rotas finas: delegam para `domain/services`.
- `src/app/domain/`: modelos e casos de uso. Não importa `fastapi` nem SDKs de LLM.
- `src/app/llm/`: `LLMProvider` (contrato), implementações, resiliência e custo.
- `src/app/memory/`, `src/app/guardrails/`, `src/app/prompts/`, `src/app/observability/`
- `src/app/container.py`: o único lugar que instancia implementações concretas.
- `prompts/`: prompts versionados. Nunca coloque prompt de sistema dentro do código Python.

## Regras detalhadas

- Estilo de código: `.claude/rules/code-style.md`
- Testes e evals: `.claude/rules/testing.md`
- Design de API: `.claude/rules/api-conventions.md`
- Segurança e dados: `.claude/rules/security.md`
- Prompts: `.claude/rules/prompts.md`
- Memória: `.claude/rules/memory.md`
- Git e PRs: `.claude/rules/git-workflow.md`

## Padrões que NÃO usamos

Agentes tendem a preencher lacunas com o padrão mais comum. Aqui, explicitamente, **não**:

- LangChain ou outros frameworks de orquestração no caminho principal (decisão em ADR 0003).
- Chamadas diretas ao SDK do provedor fora de `src/app/llm/`.
- Prompts como strings no código, f-strings montando prompts ou edição de versão publicada.
- `print()` para logs: use `get_logger(__name__)` e logs estruturados.
- Retentativas manuais com `while`/`sleep`: use `ResilientLLMClient`.
- Segredos em YAML, código ou testes. Também não lemos nem editamos `.env`.
- Testes que chamam o modelo real sem a marca `@pytest.mark.live`.
- `except Exception: pass` ou erros 5xx que expõem detalhes internos.

## Antes de concluir uma tarefa

1. `make check` passa.
2. Mudou prompt? Criou nova versão e rodou `make evals` (ver `/run-evals`).
3. Mudou arquitetura? Registrou um ADR (`/adr`).
4. Atualizou `docs/` e `CHANGELOG.md` quando o comportamento mudou.
