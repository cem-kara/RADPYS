# -*- coding: utf-8 -*-
"""tests/test_log_manager.py — logging altyapisi testleri"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.logger import configure_logging, log_sync_step, log_ui_error
from app.log_manager import LogCleanup, LogMonitor, LogStatistics


def _write_bytes(path: Path, size: int) -> None:
    path.write_bytes(b"x" * size)


def test_log_statistics_toplam_boyut_hesaplar(tmp_path):
    _write_bytes(tmp_path / "a.log", 1024)
    _write_bytes(tmp_path / "b.log.1", 2048)

    total_mb = LogStatistics.get_total_log_size(tmp_path)

    assert total_mb > 0


def test_cleanup_old_logs_eski_backup_siler(tmp_path):
    old_backup = tmp_path / "app.log.1"
    old_backup.write_text("old", encoding="utf-8")
    old_timestamp = time.time() - 10
    os.utime(old_backup, (old_timestamp, old_timestamp))

    deleted, freed = LogCleanup.cleanup_old_logs(days=0, log_dir=tmp_path)

    assert deleted == 1
    assert freed > 0
    assert not old_backup.exists()


def test_check_log_health_warning_doner(tmp_path):
    large_log = tmp_path / "app.log"
    _write_bytes(large_log, 9 * 1024 * 1024)

    health = LogMonitor.check_log_health(tmp_path)

    assert health["status"] == "WARNING"
    assert health["messages"]


def test_configure_logging_ve_yardimci_loglar(tmp_path):
    log_path = configure_logging(tmp_path)
    log_sync_step("personel", "pull", count=3)
    log_ui_error("kaydet", ValueError("test"), group="form", page="personel")

    assert log_path == tmp_path / "app.log"
    assert (tmp_path / "sync.log").exists()
    assert (tmp_path / "errors.log").exists()
    assert (tmp_path / "ui.log").exists()