---
name: prompts-imutaveis
description: Versões de prompt publicadas são imutáveis; mudanças criam vN+1 validada por evals
metadata:
  type: feedback
---

Nunca edite um arquivo `prompts/**/*.vN.md` que já foi publicado. Crie a próxima versão,
registre-a em `prompts/registry.yaml` e só troque `active` depois de os evals passarem.

**Why:** a auditoria registra nome, versão e hash do prompt de cada resposta. Editar uma versão
existente quebra a rastreabilidade e impede comparar a qualidade entre versões.

**How to apply:** use o comando `/new-prompt`. Ver [[provedor-fake-por-padrao]].
