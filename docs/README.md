# Documentação técnica

Índice da documentação do template. Cada documento tem um dono e é revisado a cada mudança
relevante (ver [manutenção](guides/maintenance.md)).

## Arquitetura

- [Mapa da estrutura do template](../ARQUITETURA.md): cada arquivo e pasta, com o que é,
  quando usar e um exemplo.
- [Visão geral da arquitetura](architecture/overview.md): camadas, fluxo de uma requisição e
  onde fica cada responsabilidade.
- [Decisões de arquitetura (ADRs)](architecture/adr/): por que cada escolha foi feita e
  quais alternativas foram descartadas.

## Guias

| Guia | Para quem |
|---|---|
| [Instalação](guides/installation.md) | Quem vai rodar o projeto pela primeira vez |
| [Configuração e ambientes](guides/configuration.md) | Dev, homologação e produção |
| [Desenvolvimento](guides/development.md) | Fluxo diário e como estender o template |
| [Testes e qualidade](guides/testing.md) | Estratégia de testes, evals e desempenho |
| [Implantação](guides/deployment.md) | CI/CD, releases e rollback |
| [Manutenção](guides/maintenance.md) | Rotinas preventivas |

## IA

- [Estratégia de memória](ai/memory-strategy.md)
- [Gestão de prompts, regras e instruções](ai/prompt-management.md)
- [Avaliação de respostas (evals)](ai/evaluation.md)
- [Guardrails](ai/guardrails.md)

## Segurança e governança

- [Modelo de ameaças (OWASP LLM Top 10)](security/threat-model.md)
- [Governança de IA](security/governance.md)
- [Proteção de dados e LGPD](security/data-protection.md)

## Operação

- [Observabilidade](operations/observability.md)
- [Resiliência e tratamento de erros](operations/resilience.md)
- [Gestão de custos](operations/cost-management.md)
- [Runbook de incidentes](operations/runbook.md)

## Processo

- [Fluxo de Git, branches e commits](process/git-workflow.md)
- [Revisão de código](process/code-review.md)
- [Gestão de dependências](process/dependency-management.md)
- [Evolução da arquitetura](process/architecture-evolution.md)

## Validação

- [Checklist de validação de projeto](checklist/project-validation-checklist.md)
