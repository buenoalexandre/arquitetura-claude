# 0005. Memória em dois níveis com políticas explícitas

- **Status:** Aceito
- **Data:** 2026-10-20

## Contexto

Modelos não guardam estado entre chamadas. A aplicação precisa lembrar o histórico da conversa
e fatos duráveis sobre o usuário, sem estourar a janela de contexto, sem misturar dados entre
usuários e respeitando a LGPD (retenção mínima e direito ao esquecimento).

## Decisão

- **Curto prazo:** histórico por sessão (`ShortTermStore`), recortado por orçamento de tokens.
- **Longo prazo:** fatos e preferências por usuário (`LongTermStore`), com TTL e busca por
  relevância.
- **Políticas:** `MemoryPolicy` decide o que pode ser guardado (bloqueia injeção, redige PII) e
  por quanto tempo.
- Implementações de referência em memória, atrás de contratos `Protocol`.

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| Contratos próprios + armazenamento trocável (escolhida) | Testável e portátil | Busca semântica fica por conta da implementação |
| Mem0 / Zep / Letta | Extração e consolidação automáticas | Dependência externa; menos controle de PII e retenção |
| Mandar o histórico completo sempre | Simples | Custo e latência crescem; estoura o contexto |
| Compactação no servidor do provedor | Sem código para resumir | Amarra a um provedor; não substitui a memória de longo prazo |

Implementações recomendadas para produção: **Redis** (curto prazo, com TTL nativo) e
**PostgreSQL + pgvector** (longo prazo; um banco a menos para operar). Alternativas: Qdrant,
Chroma ou Pinecone quando o volume vetorial for grande.

## Consequências

- Toda memória tem namespace igual ao usuário autenticado; não existe consulta entre usuários.
- A memória é tratada como dado não confiável ao voltar para o prompt.

## Critérios de revisão

Se o produto precisar de memória compartilhada (por equipe ou organização), revise o modelo de
namespaces e a autorização.
