# Evolução da arquitetura

## Princípios

- **Evolução por evidência:** mudanças de arquitetura respondem a métricas (latência, custo,
  qualidade, incidentes) ou a requisitos novos, não à moda.
- **Decisões reversíveis primeiro:** prefira mudanças por configuração ou atrás de contratos já
  existentes (`LLMProvider`, `ShortTermStore`, `LongTermStore`, `PromptRegistry`).
- **Toda decisão relevante vira ADR**, com critério de revisão.

## Gatilhos de evolução

| Sinal | Evolução típica |
|---|---|
| Mais de uma réplica da API | Memória curta e rate limit em Redis |
| Memória longa > 10 mil registros por usuário, ou busca imprecisa | pgvector + busca híbrida |
| Respostas precisam de documentos da empresa | Módulo `retrieval/` (RAG) com contrato próprio |
| Ações no mundo real (enviar, agendar, pagar) | Tool use com allowlist, confirmação humana e idempotência |
| Tarefas longas e abertas | Fluxo agêntico com orçamento de tokens e limites de passos |
| Várias equipes ou produtos | Gateway de IA central (cota, cache, roteamento de modelo) |
| Custo crescente | Cache de prompt, batch, roteamento por complexidade |
| Requisito regulatório de região | Provedor regional (Bedrock, Vertex) via novo `LLMProvider` |

## Escada de complexidade para funcionalidades de IA

Suba um degrau só quando o anterior não atender, comprovado por evals:

1. Chamada única com um bom prompt
2. Saída estruturada (schema) + validação
3. Fluxo determinístico com várias chamadas (pipeline controlado pelo código)
4. Recuperação de contexto (RAG)
5. Ferramentas (tool use) com loop controlado
6. Agente autônomo ou multiagente (arquiteto, engenheiro, revisor, otimizador)

## Critérios para sair do template

Um projeto pode divergir do template quando o requisito não cabe nos contratos atuais. Nesse
caso: registre um ADR, mantenha os controles de segurança e observabilidade equivalentes e
proponha a melhoria de volta ao template, se ela for útil a outros projetos.
