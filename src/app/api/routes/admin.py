"""Endpoints administrativos (somente papel admin)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import ContainerDep, require
from app.core.security import Principal

router = APIRouter(prefix="/v1", tags=["admin"])


@router.get("/metrics")
async def metrics(
    container: ContainerDep,
    _principal: Annotated[Principal, Depends(require("metrics:read"))],
) -> dict[str, list[dict[str, object]]]:
    return container.metrics.snapshot()
