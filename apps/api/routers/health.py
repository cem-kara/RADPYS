"""Health and readiness routes."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from config import Settings, get_settings
from schemas.health import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.service_name,
        timestamp=_now_utc(),
    )


@router.get("/ready", response_model=ReadyResponse)
def ready(settings: Settings = Depends(get_settings)) -> ReadyResponse:
    return ReadyResponse(
        status="ready",
        environment=settings.environment,
        timestamp=_now_utc(),
    )
