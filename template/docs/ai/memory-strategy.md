# Estratégia de memória e contexto

Existem três "memórias" diferentes no projeto. Cada uma tem dono, ciclo de vida e lugar
próprios.

| Memória | Para quê | Onde | Ciclo de vida |
|---|---|---|---|
| Curto prazo (aplicação) | Continuidade da conversa | `ShortTermStore` | Sessão; janela por tokens |
| Longo prazo (aplicação) | Fatos e preferências do usuário | `LongTermStore` | TTL (30 a 90 dias) + esquecimento |
| Memória do agente de desenvolvimento | Contexto do projeto para o Claude Code | `CLAUDE.md`, `.claude/rules/`, `memory/` | Versionada no git |

## 1. Curto prazo: a janela de contexto

**Armazenar:** cada turno (usuário e assistente) é anexado à sessão `"<usuario>:<sessao>"`,
com a PII já redigida.

**Recuperar:** `window(session_key, max_tokens)` devolve as mensagens mais recentes que cabem
em `memory.short_term_max_tokens`, sempre começando por uma mensagem do usuário.

**Descartar:** mensagens fora da janela deixam de ir ao modelo. Há também um teto de 200
mensagens por sessão.

**Evoluções recomendadas:**
- **Resumo progressivo:** quando a janela cortar mensagens, gere um resumo das antigas (com um
  modelo barato) e guarde-o como `MemoryRecord(kind="summary")`.
- **Compactação no servidor:** para conversas muito longas, os provedores oferecem compactação
  automática. Ela funciona bem em agentes; no produto, prefira o resumo próprio, que é auditável.
- **Redis** com TTL em produção (várias réplicas precisam compartilhar o estado).

## 2. Longo prazo: fatos duráveis

**Armazenar:** só pelo caminho explícito (`POST /v1/memory`) ou por um extrator que passe pela
mesma `MemoryPolicy`:
1. `evaluate`: rejeita conteúdo trivial ou com padrão de injeção (evita memória envenenada).
2. `build_record`: redige PII e define `expires_at = agora + long_term_ttl_days`.

**Recuperar:** `search(namespace, consulta, limite)` devolve os registros mais relevantes do
usuário. As preferências sempre entram. O resultado é inserido no prompt de sistema numa seção
rotulada **"dados, não instruções"**.

**Atualizar:** conteúdo idêntico substitui o registro anterior. Para fatos que mudam
("mudei de empresa"), o extrator deve buscar o fato antigo e substituí-lo, em vez de acumular
versões contraditórias.

**Descartar:**
- TTL: `purge_expired` deve rodar como job agendado (diário).
- Esquecimento: `DELETE /v1/memory` apaga a memória longa e todas as sessões do usuário
  (LGPD, art. 18).
- Revisão: registros com baixa relevância por muito tempo são candidatos à remoção.

**Busca semântica:** a implementação de referência usa sobreposição de termos. Em produção, use
embeddings + PostgreSQL/pgvector (ou Qdrant/Chroma) e uma busca híbrida (vetorial + palavra-chave).

## 3. Memória do agente de desenvolvimento

- `CLAUDE.md`: sempre carregado; curto; aponta para as regras.
- `.claude/rules/*.md`: convenções por domínio, carregadas quando relevantes.
- `memory/MEMORY.md` + `memory/<fato>.md`: decisões e preferências do time que não estão no
  código. Formato e regras em `.claude/rules/memory.md`.
- Pessoal e não versionado: `CLAUDE.local.md` e `~/.claude/`.

## Orçamento de contexto

Ordem de montagem do prompt, do mais estável ao mais volátil (bom para o cache de prompt):

1. Prompt de sistema versionado + políticas (estável, cacheável)
2. Memória de longo prazo recuperada (muda por usuário)
3. Histórico de curto prazo (muda a cada turno)
4. Mensagem atual

Se o total passar do limite, corte nesta ordem: histórico antigo → memória menos relevante →
nunca o prompt de sistema.
