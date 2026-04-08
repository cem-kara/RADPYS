# -*- coding: utf-8 -*-
"""Log dosyalari icin bakim ve izleme yardimcilari."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from app.config import (
    LOG_BACKUP_COUNT,
    LOG_CLEANUP_DAYS,
    LOG_DIR,
    LOG_MAX_BYTES,
    LOG_MAX_TOTAL_MB,
    LOG_WARN_FILE_MB,
    LOG_WARN_TOTAL_MB,
)
from app.logger import logger


class LogStatistics:
    """Log dosyalari istatistiklerini hesaplar."""

    @staticmethod
    def get_log_size(log_file: Path | str) -> float:
        file_path = Path(log_file)
        if not file_path.exists():
            return 0.0
        return file_path.stat().st_size / (1024 * 1024)

    @staticmethod
    def get_total_log_size(log_dir: Path | str | None = None) -> float:
        dizin = Path(log_dir) if log_dir is not None else Path(LOG_DIR)
        total_bytes = sum(file.stat().st_size for file in dizin.glob("*.log*"))
        return total_bytes / (1024 * 1024)

    @staticmethod
    def count_lines(file_path: Path | str) -> int:
        try:
            with Path(file_path).open("rb") as handle:
                return sum(1 for _ in handle)
        except OSError as exc:
            logger.warning(f"Satir sayisi hesaplanamadi ({file_path}): {exc}")
            return 0

    @staticmethod
    def get_log_stats(log_dir: Path | str | None = None) -> dict[str, dict]:
        dizin = Path(log_dir) if log_dir is not None else Path(LOG_DIR)
        stats: dict[str, dict] = {}
        for log_file in dizin.glob("*.log*"):
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            stats[log_file.name] = {
                "size_mb": round(log_file.stat().st_size / (1024 * 1024), 2),
                "lines": LogStatistics.count_lines(log_file),
                "last_modified": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                "path": str(log_file),
            }
        return stats


class LogCleanup:
    """Eski veya fazla log dosyalarini temizler."""

    @staticmethod
    def get_backup_logs(log_dir: Path | str | None = None) -> list[Path]:
        dizin = Path(log_dir) if log_dir is not None else Path(LOG_DIR)
        return sorted(dizin.glob("*.log.*"))

    @staticmethod
    def cleanup_old_logs(days: int = LOG_CLEANUP_DAYS, log_dir: Path | str | None = None) -> tuple[int, int]:
        dizin = Path(log_dir) if log_dir is not None else Path(LOG_DIR)
        cutoff_timestamp = (datetime.now() - timedelta(days=days)).timestamp()
        deleted_count = 0
        freed_space = 0

        for log_file in LogCleanup.get_backup_logs(dizin):
            if log_file.stat().st_mtime >= cutoff_timestamp:
                continue
            try:
                size = log_file.stat().st_size
                log_file.unlink()
                freed_space += size
                deleted_count += 1
                logger.info(f"Eski log silindi: {log_file.name} ({size / 1024:.1f} KB)")
            except OSError as exc:
                logger.error(f"Log silme hatasi ({log_file}): {exc}")

        if deleted_count > 0:
            logger.info(
                f"{deleted_count} eski log silindi, {freed_space / (1024 * 1024):.1f} MB bosaltildi"
            )
        return deleted_count, freed_space

    @staticmethod
    def cleanup_by_space(max_size_mb: int = LOG_MAX_TOTAL_MB, log_dir: Path | str | None = None) -> tuple[int, int]:
        dizin = Path(log_dir) if log_dir is not None else Path(LOG_DIR)
        total_size = LogStatistics.get_total_log_size(dizin)
        if total_size <= max_size_mb:
            logger.debug(f"Log dizini boyutu uygun: {total_size:.1f} MB / {max_size_mb} MB")
            return 0, 0

        backup_logs = sorted(LogCleanup.get_backup_logs(dizin), key=lambda file: file.stat().st_mtime)
        deleted_count = 0
        freed_space = 0

        for log_file in backup_logs:
            if total_size <= max_size_mb:
                break
            try:
                size = log_file.stat().st_size
                log_file.unlink()
                freed_space += size
                total_size -= size / (1024 * 1024)
                deleted_count += 1
                logger.info(f"Alan temizligi: {log_file.name} silindi")
            except OSError as exc:
                logger.error(f"Alan temizligi hatasi ({log_file}): {exc}")

        if deleted_count > 0:
            logger.info(
                f"Alan temizligi tamamlandi: {deleted_count} log silindi, {freed_space / (1024 * 1024):.1f} MB bosaltildi"
            )
        return deleted_count, freed_space


class LogMonitor:
    """Log sagligi kontrollerini yapar."""

    @staticmethod
    def check_log_health(log_dir: Path | str | None = None) -> dict[str, object]:
        dizin = Path(log_dir) if log_dir is not None else Path(LOG_DIR)
        status = "OK"
        messages: list[str] = []

        for file_name in ("app.log", "sync.log", "errors.log", "ui.log"):
            log_file = dizin / file_name
            if not log_file.exists():
                continue
            size_mb = LogStatistics.get_log_size(log_file)
            if size_mb > LOG_WARN_FILE_MB:
                status = "WARNING"
                messages.append(
                    f"{file_name} buyuk: {size_mb:.1f} MB (Limit: {LOG_MAX_BYTES / (1024 * 1024):.0f} MB)"
                )

        total_mb = LogStatistics.get_total_log_size(dizin)
        if total_mb > LOG_WARN_TOTAL_MB:
            status = "WARNING"
            messages.append(f"Toplam log boyutu yuksek: {total_mb:.1f} MB")

        backup_logs = LogCleanup.get_backup_logs(dizin)
        if len(backup_logs) > (LOG_BACKUP_COUNT * 2):
            status = "WARNING"
            messages.append(f"Fazla sayida rotating log var: {len(backup_logs)} dosya")

        return {
            "status": status,
            "total_size_mb": round(total_mb, 2),
            "messages": messages,
        }

    @staticmethod
    def log_health_status(log_dir: Path | str | None = None) -> None:
        health = LogMonitor.check_log_health(log_dir)
        logger.info(f"Log Health: {health['status']} | Total: {health['total_size_mb']:.1f} MB")
        for message in health["messages"]:
            logger.warning(message)


def initialize_log_management(log_dir: Path | str | None = None) -> None:
    """Uygulama acilisinda log temizligi ve saglik kontrolu yapar."""
    dizin = Path(log_dir) if log_dir is not None else Path(LOG_DIR)
    logger.info("=" * 60)
    logger.info("LOG MANAGEMENT BASLATILIYOR")
    logger.info("=" * 60)

    LogCleanup.cleanup_old_logs(log_dir=dizin)
    LogCleanup.cleanup_by_space(log_dir=dizin)

    stats = LogStatistics.get_log_stats(dizin)
    logger.info(f"Log dosyalari ({len(stats)} dosya):")
    for name, info in sorted(stats.items()):
        logger.info(
            f"  {name:20s} | {info['size_mb']:7.2f} MB | {info['lines']:6d} satir | {info['last_modified']}"
        )

    LogMonitor.log_health_status(dizin)
    logger.info("=" * 60)