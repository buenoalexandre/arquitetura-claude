"""Ponto de entrada da API (app factory).

Execute com: ``uvicorn app.main:create_app --factory --app-dir src``
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from app.api.routes import admin, chat, health, memory
from app.container import build_container
from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.core.logging import bind_correlation_id, configure_logging, get_logger
from app.llm.provider import LLMProvider
from app.observability.tracing import configure_tracing

log = get_logger(__name__)


def create_app(settings: Settings | None = None, provider: LLMProvider | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.observability.log_level, settings.observability.log_json)
    configure_tracing(settings.observability.service_name, settings.observability.trace_enabled)

    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.state.container = build_container(settings, provider)

    @app.middleware("http")
    async def correlation_middleware(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        correlation_id = request.headers.get("x-request-id") or uuid.uuid4().hex
        bind_correlation_id(correlation_id)
        started = time.perf_counter()
        response = await call_next(request)
        response.headers["x-request-id"] = correlation_id
        log.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
        )
        return response

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        log.warning("app_error", code=exc.code, detail=exc.message)
        # Erros 4xx explicam ao cliente o que corrigir; 5xx nunca expõem detalhes internos.
        message = exc.message if exc.status_code < 500 else exc.public_message
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": message}},
        )

    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(memory.router)
    app.include_router(admin.router)
    return app
