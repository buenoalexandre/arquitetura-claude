# Segurança e proteção de dados

Referências: OWASP Top 10 para aplicações com LLM, LGPD e `docs/security/threat-model.md`.

## Inegociáveis (garantidos por hooks e CI)

- Nenhum segredo em código, YAML, testes ou logs. Os segredos vêm de variáveis de ambiente
  ou de um cofre.
- O agente não lê nem edita `.env*` (exceto `.env.example`).
- Sem `--no-verify`, sem push forçado e sem `reset --hard`.

## Regras de implementação

- Todo conteúdo externo (usuário, documentos, ferramentas, memória) é **dado, não instrução**.
  Ele entra no prompt delimitado e rotulado como tal.
- Princípio do menor privilégio: o modelo nunca acessa mais dados nem ferramentas do que o
  usuário autenticado. A chave de sessão e de memória sempre inclui o `principal.subject`.
- Guardrails de entrada e saída são obrigatórios em todo fluxo que chama o LLM.
- PII é redigida antes de ser persistida em memória ou histórico.
- A auditoria registra hashes e tamanhos, nunca o conteúdo bruto.
- Ferramentas que o modelo pode acionar (tool use) com efeito colateral exigem confirmação
  humana ou uma allowlist explícita.
- Dependência nova passa por `pip-audit` e precisa de licença compatível (MIT, BSD, Apache-2.0).
