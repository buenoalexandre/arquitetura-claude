"""Hierarquia de erros da aplicação.

Toda exceção de domínio herda de ``AppError`` e carrega um código estável e o status HTTP,
para que a API devolva um envelope consistente sem vazar detalhes internos.
"""

from __future__ import annotations


class AppError(Exception):
    code = "internal_error"
    status_code = 500
    public_message = "Erro interno."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.public_message)
        self.message = message or self.public_message


class AuthenticationError(AppError):
    code = "unauthenticated"
    status_code = 401
    public_message = "Credenciais ausentes ou inválidas."


class AuthorizationError(AppError):
    code = "forbidden"
    status_code = 403
    public_message = "Permissão insuficiente para esta operação."


class GuardrailViolationError(AppError):
    code = "guardrail_violation"
    status_code = 400
    public_message = "A entrada viola as políticas de uso."


class RateLimitExceededError(AppError):
    code = "rate_limited"
    status_code = 429
    public_message = "Limite de requisições excedido. Tente novamente em instantes."


class LLMUnavailableError(AppError):
    code = "llm_unavailable"
    status_code = 503
    public_message = "O serviço de IA está temporariamente indisponível."


class LLMRefusalError(AppError):
    code = "llm_refusal"
    status_code = 422
    public_message = "O modelo recusou a solicitação."


class PromptError(AppError):
    code = "prompt_error"
    status_code = 500
    public_message = "Falha ao montar o prompt."
