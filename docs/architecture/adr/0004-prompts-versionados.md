# 0004. Prompts versionados em arquivos com registro central

- **Status:** Aceito
- **Data:** 2026-10-20

## Contexto

Prompts são lógica de negócio: mudam o comportamento do produto tanto quanto o código. Prompts
espalhados como strings no código não podem ser revisados por quem não programa, não têm
histórico de qualidade e impedem saber qual texto gerou cada resposta.

## Decisão

- Prompts em `prompts/**/*.vN.md`, declarados em `prompts/registry.yaml` com dono, variáveis,
  políticas compostas e changelog.
- Versões publicadas são imutáveis. A troca de `active` exige evals no mesmo PR.
- Toda renderização gera um hash SHA-256, registrado na auditoria com nome e versão.
- Políticas de comportamento e de segurança ficam em `prompts/policies/` e são reaproveitadas.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Arquivos + registro no repositório (escolhida) | Revisão em PR, histórico git, funciona offline | Exige deploy para mudar o prompt |
| Plataforma de gestão de prompts (Langfuse, PromptLayer) | Edição sem deploy, testes A/B | Dependência externa e risco de mudar produção sem revisão |
| Strings no código | Simples | Sem governança nem rastreabilidade |

## Consequências

- Para editar prompts sem deploy, o `PromptRegistry` pode ganhar uma implementação remota com o
  mesmo contrato, mantendo versões imutáveis e auditoria.

## Critérios de revisão

Se o time de produto precisar iterar prompts várias vezes por dia, adote uma plataforma de
gestão de prompts integrada ao mesmo processo de evals.
