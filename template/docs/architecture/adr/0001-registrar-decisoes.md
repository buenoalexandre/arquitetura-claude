# 0001. Registrar decisões de arquitetura em ADRs

- **Status:** Aceito
- **Data:** 2026-10-20

## Contexto

Os projetos com IA mudam rápido: modelos, provedores e técnicas mudam a cada trimestre. Sem
registro, o motivo das escolhas se perde, e tanto pessoas quanto agentes de código acabam
revertendo decisões ou repetindo discussões.

## Decisão

Toda decisão que afete a estrutura, a stack, a segurança ou o custo é registrada como ADR em
`docs/architecture/adr/`, no formato de `0000-template.md`, por meio do comando `/adr`.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| ADRs em Markdown no repositório (escolhida) | Versionados com o código, revisados em PR, lidos pelo agente | Exige disciplina |
| Wiki externa | Fácil de editar | Desatualiza, fica fora do PR e o agente não lê |
| Sem registro formal | Zero esforço | Perda de contexto |

## Consequências

- O agente consulta os ADRs antes de propor mudanças (ver `.claude/agents/architect.md`).
- Desvios do template em projetos derivados precisam de um ADR próprio.

## Critérios de revisão

Se o volume de ADRs passar de ~50, considere agrupar por domínio.
