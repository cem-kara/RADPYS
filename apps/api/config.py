"""API settings management.

This module keeps configuration in one place and exposes a cached helper
for FastAPI dependency injection.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True)
class Settings:
    service_name: str
    environment: str
    log_level: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        service_name=os.getenv("API_SERVICE_NAME", "repys-next-api"),
        environment=os.getenv("API_ENV", "local"),
        log_level=os.getenv("API_LOG_LEVEL", "info"),
    )
