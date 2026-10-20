"""Sondas de liveness e readiness para orquestradores (Kubernetes, ECS, Cloud Run)."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import ContainerDep

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready(container: ContainerDep) -> dict[str, str]:
    breaker = container.llm.breaker(container.settings.llm.model)
    return {"status": "ready", "llm_circuit": breaker.state.value}
