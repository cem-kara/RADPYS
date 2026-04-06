"""FastAPI entrypoint for REPYS Next API."""

from __future__ import annotations

from fastapi import FastAPI

from config import get_settings
from routers.health import router as health_router

settings = get_settings()

app = FastAPI(title=settings.service_name, version="0.1.0")
app.include_router(health_router)
