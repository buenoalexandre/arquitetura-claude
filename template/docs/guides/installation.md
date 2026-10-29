# Instalação

## Pré-requisitos

| Ferramenta | Versão | Observação |
|---|---|---|
| Python | 3.11+ | 3.12 é o recomendado |
| uv | 0.5+ | `pip install uv`, `winget install astral-sh.uv` ou o instalador oficial |
| Git | 2.40+ | |
| Docker | 24+ | Opcional, para `make docker` |
| make | qualquer | Opcional no Windows (use Git Bash, WSL ou os comandos `uv run` direto) |

## Passo a passo

```bash
git clone git@github.com:<org>/<projeto>.git
cd <projeto>
./scripts/bootstrap.sh          # Windows: .\scripts\bootstrap.ps1
```

O bootstrap cria o `.env` e o `CLAUDE.local.md` a partir dos exemplos, instala as
dependências e os hooks de pre-commit e roda a validação do template.

Sem os scripts:

```bash
uv sync --group dev
cp .env.example .env
uv run pre-commit install --hook-type pre-commit --hook-type commit-msg
```

Sem uv (somente pip):

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e . --group dev    # requer pip 25.1+
```

## Verificação

```bash
make check                      # lint, tipos, testes e checklist
make run                        # abre http://localhost:8000/docs
curl localhost:8000/health      # {"status":"ok"}
```

## Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| `ValidationError: APP_SECURITY__JWT_SECRET precisa ser definido` | `APP_ENV` está em staging ou produção | Defina o segredo ou use `APP_ENV=development` |
| `401` em todas as rotas | Cabeçalho `X-API-Key` ausente | Use uma chave de `APP_SECURITY__API_KEYS` |
| Testes lentos ou com custo | `APP_LLM__PROVIDER=anthropic` no ambiente | Testes usam `fake`; rode o modelo real só com `-m live` |
| `make: command not found` no Windows | make não instalado | Rode os comandos `uv run ...` do Makefile |
