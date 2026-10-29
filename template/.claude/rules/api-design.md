# Design de API

- Versão no caminho: `/v1/...`. Mudanças incompatíveis exigem `/v2` e um período de transição
  documentado no `CHANGELOG.md`.
- Rotas finas: validam a entrada (Pydantic), resolvem dependências e delegam ao serviço.
- Toda rota, exceto `/health` e `/ready`, exige autenticação e uma permissão explícita via
  `Depends(require("recurso:acao"))`.
- Envelope de erro único: `{"error": {"code": "<estavel>", "message": "<texto>"}}`.
  - 4xx: mensagem acionável para o cliente.
  - 5xx: mensagem genérica. O detalhe vai para o log, com `correlation_id`.
- Cabeçalho `X-Request-ID` é aceito e devolvido em toda resposta.
- Nomes de campos em snake_case. Datas em ISO 8601 UTC.
- Respostas de IA sempre informam `model`, `prompt_version` e `usage` (tokens e custo).
- Paginação por cursor (`?cursor=&limit=`), com `limit` máximo de 100.
