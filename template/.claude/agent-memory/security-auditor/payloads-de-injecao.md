---
name: payloads-de-injecao
description: Todo padrão novo de injeção de prompt vira caso em tests/security/injection_payloads.json
metadata:
  type: project
---

Os padrões de ataque observados em produção, em red teaming ou em auditorias são registrados
em `tests/security/injection_payloads.json`: em `blocked` os que devem ser barrados e em
`allowed` os falsos positivos que não podem ser barrados.

**Why:** heurísticas de guardrail regridem em silêncio quando alguém ajusta uma regex; os
payloads versionados transformam cada ataque conhecido em teste.

**How to apply:** ao recomendar uma mitigação, inclua os payloads correspondentes no achado.
