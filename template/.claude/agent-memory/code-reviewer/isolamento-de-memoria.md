---
name: isolamento-de-memoria
description: Toda leitura ou escrita de memória precisa usar o principal.subject como namespace
metadata:
  type: feedback
---

Ao revisar código que acessa `ShortTermStore` ou `LongTermStore`, confirme que a chave ou o
namespace vem de `principal.subject` (ou de `ChatService.session_key`), nunca de um ID enviado
pelo cliente.

**Why:** um ID de sessão vindo do cliente sem o sujeito autenticado permite ler a conversa de
outro usuário (OWASP LLM02).

**How to apply:** marque como achado **alto** qualquer acesso à memória sem o sujeito na chave.
