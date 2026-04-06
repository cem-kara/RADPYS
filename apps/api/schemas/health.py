"""Schemas for health and readiness endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    timestamp: datetime


class ReadyResponse(BaseModel):
    status: Literal["ready"]
    environment: str
    timestamp: datetime
