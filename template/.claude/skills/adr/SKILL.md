---
name: adr
description: Registra uma decisão de arquitetura (ADR)
argument-hint: "<título da decisão>"
disable-model-invocation: true
---

Crie um ADR para: $ARGUMENTS

1. Liste `docs/architecture/adr/` e use o próximo número livre (`NNNN-titulo-em-kebab-case.md`).
2. Copie a estrutura de `docs/architecture/adr/0000-template.md`.
3. Preencha contexto, decisão, alternativas consideradas (com prós e contras), consequências e
   critérios de revisão. Use como apoio o subagente `architect`.
4. Status inicial: `Proposto`. Se substituir um ADR anterior, marque o antigo como
   `Substituído por NNNN`.
5. Adicione o ADR ao índice em `docs/architecture/overview.md`.
