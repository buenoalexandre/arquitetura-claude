# 0002. Python e FastAPI como stack de referência

- **Status:** Aceito
- **Data:** 2026-10-20

## Contexto

O template precisa de uma implementação executável para servir de exemplo e para validar o CI.
A arquitetura deve continuar independente de linguagem, mas a implementação de referência
precisa estar onde fica a maior parte do ecossistema de IA (SDKs, avaliação, RAG, dados).

## Decisão

- **Linguagem:** Python 3.11+ com tipagem estrita (mypy `--strict`).
- **API:** FastAPI + Pydantic v2 (validação, OpenAPI automático, async nativo).
- **Configuração:** pydantic-settings, com camadas YAML por ambiente e variáveis de ambiente.
- **Pacotes:** uv + `pyproject.toml` (PEP 621 e dependency groups da PEP 735).
- **Qualidade:** ruff (lint e formatação), pytest, bandit e pip-audit.

## Alternativas consideradas

| Tema | Alternativa | Por que não foi a escolhida |
|---|---|---|
| Linguagem | TypeScript/Node (Fastify/Hono + Zod + Vitest) | Ótima para produtos web; ecossistema de evals e dados menor. É a alternativa recomendada para times full-stack JS |
| API | Litestar | Tecnicamente sólido, comunidade menor |
| API | Flask | Sem async nativo nem validação integrada |
| Pacotes | Poetry | Mais lento; padrão próprio de lockfile |
| Pacotes | pip-tools | Bom, mas exige mais ferramentas em volta |
| Lint | black + flake8 + isort | Três ferramentas onde uma (ruff) resolve |
| Tipos | pyright | Também é excelente; mypy tem o plugin do Pydantic |

## Consequências

- Os conceitos (camadas, contratos, registro de prompts, políticas de memória, guardrails,
  evals) se aplicam a qualquer stack. Um projeto em TypeScript mantém a estrutura de pastas e
  troca apenas `src/`, `tests/` e as ferramentas.
- `uv.lock` deve ser gerado (`uv lock`) e versionado no primeiro commit do projeto derivado.
  A partir daí, o CI pode usar `uv sync --locked`.

## Critérios de revisão

Se mais da metade dos projetos derivados forem em outra linguagem, mantenha um segundo
template de referência para ela.
