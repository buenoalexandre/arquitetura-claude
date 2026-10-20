# Desenvolvimento

## Fluxo diário

1. Atualize a `main` e crie uma branch: `git switch -c feat/42-descricao`.
2. Rode a API com `make run`. O provedor `fake` responde sem custo.
3. Escreva primeiro o teste, depois o código.
4. Rode `make check` antes de cada push.
5. Abra o PR com o template preenchido.

## Trabalhando com o Claude Code

| Recurso | Onde | Quando usar |
|---|---|---|
| `CLAUDE.md` | raiz | Carregado sempre: visão geral e "Padrões que NÃO usamos" |
| Regras | `.claude/rules/` | Convenções detalhadas por domínio |
| Comandos | `.claude/commands/` | Você chama: `/review`, `/fix-issue 42`, `/new-prompt`, `/run-evals`, `/adr` |
| Skills | `.claude/skills/` | O Claude carrega quando o assunto aparece: `new-ai-project`, `security-review` |
| Subagentes | `.claude/agents/` | Tarefas com contexto isolado: `architect`, `code-reviewer`, `security-auditor`, `prompt-engineer`, `performance-optimizer` |
| Hooks | `.claude/hooks/` | Proteções que sempre rodam: bloqueiam comandos perigosos e segredos, formatam Python |
| MCP | `.mcp.json` | Integrações compartilhadas (GitHub, documentação) |
| Memória do time | `memory/` | Decisões e preferências que não estão no código |

Um fluxo que funciona bem com vários agentes: `architect` desenha → você implementa (ou o
agente principal implementa) → `code-reviewer` revisa → `performance-optimizer` otimiza o que
os números mostrarem.

Para sessões paralelas em branches diferentes, use `git worktree add ../proj-feat feat/x`. O
arquivo `.worktreeinclude` copia `.env` e as configurações locais para cada worktree.

## Receitas

### Novo endpoint

1. Modelos de entrada e saída em `src/app/domain/models.py`.
2. Lógica no serviço (`src/app/domain/services/`).
3. Rota fina em `src/app/api/routes/`, com `Depends(require("recurso:acao"))`.
4. Permissão em `ROLE_PERMISSIONS` (`core/security.py`).
5. Testes funcional e de segurança (401, 403, entrada inválida).

### Novo prompt ou nova versão

Use `/new-prompt`. O processo está em [gestão de prompts](../ai/prompt-management.md).

### Novo provedor de LLM

Implemente `LLMProvider` e mapeie os erros. Veja a seção "Como estender" da
[visão geral](../architecture/overview.md).

### Trocar o armazenamento de memória

Implemente `ShortTermStore` ou `LongTermStore` (`src/app/memory/base.py`) e troque a instância
em `container.py`. Os testes de `tests/unit/test_memory.py` servem como testes de contrato:
parametrize-os para rodar contra a nova implementação.
