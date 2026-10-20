# Revisão de código

## Antes de pedir revisão (autor)

- `make check` passa; o PR tem até ~400 linhas e um único assunto.
- O template de PR está preenchido, inclusive o checklist de IA.
- Rode `/review` no Claude Code para uma primeira passada.

## O que o revisor verifica

1. **Correção:** a mudança faz o que promete? Os casos de borda e de erro estão cobertos?
2. **Testes:** um teste falharia sem a mudança? Ele testa comportamento, não implementação?
3. **Arquitetura:** respeita as camadas? Há chamada ao SDK de LLM fora de `llm/`?
4. **Segurança:** rota com permissão, dados filtrados por usuário, guardrails, nada sensível em
   logs (use a skill `security-review` quando aplicável).
5. **IA:** prompt novo é versão nova; evals atualizados; impacto em custo e latência comentado.
6. **Operação:** logs e métricas suficientes para depurar em produção.
7. **Documentação:** `docs/`, `CHANGELOG.md` e ADR quando necessário.

## Etiqueta

- Comentários com prefixo: **[bloqueante]**, **[sugestão]**, **[dúvida]**, **[nit]**.
- Critique o código, não a pessoa; explique o porquê e, se possível, sugira o código.
- Primeira revisão em até 1 dia útil.
- Agentes de IA podem revisar, mas a aprovação final é sempre humana.
