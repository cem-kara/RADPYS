# -*- coding: utf-8 -*-
"""Merkezi logging kurulumu ve yardımcıları."""
from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import LOG_BACKUP_COUNT, LOG_DIR, LOG_MAX_BYTES


APP_LOG_FILE = "app.log"
SYNC_LOG_FILE = "sync.log"
ERROR_LOG_FILE = "errors.log"
UI_LOG_FILE = "ui.log"


class SyncLogFilter(logging.Filter):
    """Sadece senkronizasyon bağlamı içeren kayıtları geçirir."""

    def filter(self, record: logging.LogRecord) -> bool:
        return hasattr(record, "sync_context") or "sync" in record.getMessage().lower()


class ErrorLogFilter(logging.Filter):
    """Yalnızca hata ve üstü kayıtları geçirir."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= logging.ERROR


class UILogFilter(logging.Filter):
    """Yalnızca UI bağlamı olan kayıtları geçirir."""

    def filter(self, record: logging.LogRecord) -> bool:
        return hasattr(record, "ui_context")


class StructuredFormatter(logging.Formatter):
    """Ek bağlam alanlarını standart log satırına ekler."""

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)

        if hasattr(record, "sync_context"):
            ctx = getattr(record, "sync_context", {})
            extra = f" | Tablo: {ctx.get('table', 'N/A')}"
            if "step" in ctx:
                extra += f" | Adim: {ctx['step']}"
            if "count" in ctx:
                extra += f" | Kayit: {ctx['count']}"
            base += extra

        if hasattr(record, "ui_context"):
            ctx = getattr(record, "ui_context", {})
            extra = f" | UI: {ctx.get('action', 'N/A')}"
            if "group" in ctx:
                extra += f" | Grup: {ctx['group']}"
            if "page" in ctx:
                extra += f" | Sayfa: {ctx['page']}"
            base += extra

        return base


logger = logging.getLogger("radpys")


def _rotating_handler(
    file_path: Path,
    level: int,
    fmt: str,
    filters: list[logging.Filter] | None = None,
) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        file_path,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(StructuredFormatter(fmt))
    for log_filter in filters or []:
        handler.addFilter(log_filter)
    return handler


def configure_logging(log_dir: Path | str | None = None) -> Path:
    """Uygulama genelinde rotating file + console logging kurar."""
    dizin = Path(log_dir) if log_dir is not None else Path(LOG_DIR)
    dizin.mkdir(parents=True, exist_ok=True)

    app_log_path = dizin / APP_LOG_FILE
    sync_log_path = dizin / SYNC_LOG_FILE
    error_log_path = dizin / ERROR_LOG_FILE
    ui_log_path = dizin / UI_LOG_FILE

    handlers: list[logging.Handler] = [
        _rotating_handler(
            app_log_path,
            logging.INFO,
            "%(asctime)s - %(levelname)s - %(message)s",
        ),
        _rotating_handler(
            sync_log_path,
            logging.INFO,
            "%(asctime)s - %(message)s",
            filters=[SyncLogFilter()],
        ),
        _rotating_handler(
            error_log_path,
            logging.ERROR,
            "%(asctime)s - %(levelname)s - %(message)s",
            filters=[ErrorLogFilter()],
        ),
        _rotating_handler(
            ui_log_path,
            logging.ERROR,
            "%(asctime)s - %(levelname)s - %(message)s",
            filters=[UILogFilter()],
        ),
        logging.StreamHandler(sys.stdout),
    ]
    handlers[-1].setLevel(logging.INFO)
    handlers[-1].setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        handler.close()

    logging.basicConfig(level=logging.INFO, handlers=handlers, force=True)
    logger.info("RADPYS 2.0 baslatiliyor...")
    return app_log_path


def log_sync_start(table_name: str) -> None:
    extra = {"sync_context": {"table": table_name, "step": "start"}}
    logger.info(f"Sync basladi: {table_name}", extra=extra)


def log_sync_step(table_name: str, step: str, count: int | None = None) -> None:
    ctx = {"table": table_name, "step": step}
    if count is not None:
        ctx["count"] = count
    msg = f"{table_name} - {step}"
    if count is not None:
        msg += f" ({count} kayit)"
    logger.info(msg, extra={"sync_context": ctx})


def log_sync_error(table_name: str, step: str, error: Exception) -> None:
    ctx = {"table": table_name, "step": step}
    logger.error(
        f"{table_name} sync hatasi | {step} | {type(error).__name__}: {error}",
        extra={"sync_context": ctx},
        exc_info=True,
    )


def log_sync_complete(table_name: str, stats: dict | None = None) -> None:
    ctx = {"table": table_name, "step": "complete"}
    if stats:
        ctx.update(stats)
    msg = f"Sync tamamlandi: {table_name}"
    if stats:
        msg += f" | Push: {stats.get('pushed', 0)}, Pull: {stats.get('pulled', 0)}"
    logger.info(msg, extra={"sync_context": ctx})


def log_ui_error(action: str, error: Exception, group: str | None = None, page: str | None = None) -> None:
    ctx = {"action": action}
    if group is not None:
        ctx["group"] = group
    if page is not None:
        ctx["page"] = page
    logger.error(
        f"UI hata: {type(error).__name__}: {error}",
        extra={"ui_context": ctx},
        exc_info=True,
    )


def exc_logla(konum: str, exc: Exception) -> None:
    """Exception'ı tam traceback ile loglar (dialog göstermez)."""
    import traceback
    tb = traceback.format_exc()
    logger.error(f"[{konum}] {type(exc).__name__}: {exc}\n{tb}")


def get_user_friendly_error(error: Exception, table_name: str | None = None) -> tuple[str, str]:
    """Bilinen istisna tiplerini kullanıcı dostu mesaja çevirir."""
    error_type = type(error).__name__
    error_msg = str(error)

    if "ConnectionError" in error_type or "Timeout" in error_type:
        short = "Baglanti hatasi"
        detail = "Internet baglantinizi kontrol edin"
    elif "PermissionError" in error_type or "Forbidden" in error_type:
        short = "Yetki hatasi"
        detail = "Islem yetkilerinizi kontrol edin"
    elif "QuotaExceeded" in error_type or "RateLimitExceeded" in error_type:
        short = "API limit asildi"
        detail = "Bir sure bekleyip tekrar deneyin"
    elif "KeyError" in error_type or "IndexError" in error_type:
        short = "Veri yapisi hatasi"
        detail = f"Beklenmeyen veri yapisi: {error_msg}"
    elif "ValueError" in error_type or "TypeError" in error_type:
        short = "Veri formati hatasi"
        detail = f"Gecersiz veri: {error_msg}"
    else:
        short = f"Islem hatasi ({error_type})"
        detail = error_msg[:100]

    if table_name:
        short = f"{table_name}: {short}"
    return short, detail