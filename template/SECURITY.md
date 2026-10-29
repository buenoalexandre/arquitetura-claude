# Política de segurança

## Como reportar uma vulnerabilidade

Não abra issue pública. Use o recurso **Security > Report a vulnerability** do GitHub ou
escreva para `seguranca@example.com` (substitua pelo contato do seu time). Inclua:

- a descrição e o impacto;
- os passos para reproduzir (para injeção de prompt: o payload e a resposta obtida);
- a versão ou commit afetado.

Confirmamos o recebimento em até 2 dias úteis e informamos um prazo de correção conforme a
severidade (crítica: 7 dias; alta: 30 dias).

## Escopo específico de IA

Também consideramos vulnerabilidades: injeção de prompt que contorne guardrails, vazamento do
prompt de sistema ou de dados de outro usuário, envenenamento de memória e abuso de
ferramentas do modelo. Veja o modelo de ameaças em `docs/security/threat-model.md`.
