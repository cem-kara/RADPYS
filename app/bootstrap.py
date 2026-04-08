# -*- coding: utf-8 -*-
"""app/bootstrap.py — Uygulama baslatma yardimcilari."""
from __future__ import annotations

from pathlib import Path

from app.config import DB_PATH, LOG_DIR, ZORUNLU_DIZINLER
from app.db.database import Database
from app.db.migrations import run as migrate
import sys
import threading
import traceback

from app.log_manager import initialize_log_management
from app.logger import configure_logging, logger


def dizinleri_olustur(dizinler: list[Path] | None = None) -> None:
    """Uygulama icin gereken klasorleri olusturur."""
    for dizin in (dizinler or ZORUNLU_DIZINLER):
        Path(dizin).mkdir(parents=True, exist_ok=True)


def logging_kur(log_dir: Path | str | None = None) -> Path:
    """Merkezi logging altyapisini kurar ve ana log dosyasini dondurur."""
    dizin = Path(log_dir) if log_dir is not None else Path(LOG_DIR)
    log_dosya = configure_logging(dizin)
    initialize_log_management(dizin)
    return log_dosya


def veri_katmanini_hazirla(db_path: Path | str | None = None) -> Database:
    """DB baglantisini acip migration ve RBAC policy yuklemesini yapar."""
    db = Database(db_path or DB_PATH)
    migrate(db)

    import app.rbac as rbac

    rbac.init_dari_db(db)
    return db


def qt_uygulamasini_hazirla(argv: list[str]):
    """QApplication olusturur ve tema ayarlarini uygular."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    from ui.styles import ThemeManager

    app = QApplication(argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, True)

    ThemeManager.apply_dark(app)
    return app


def global_exception_hook_kur() -> None:
    """Ana is parcacigindaki yakalanmayan istisnalari loglar."""

    def _hook(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        logger.critical(
            f"[YAKALANMAYAN ISTISNA]\n"
            f"Tur  : {exc_type.__name__}\n"
            f"Mesaj: {exc_value}\n"
            f"{tb_str}"
        )
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = _hook
    logger.info("Global exception hook kuruldu.")


def threading_exception_hook_kur() -> None:
    """threading.Thread ve QThread icindeki istisnalari loglar."""

    def _thread_hook(args: threading.ExceptHookArgs) -> None:
        if args.exc_type is SystemExit:
            return
        tb_str = "".join(
            traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)
        )
        thread_adi = getattr(args.thread, "name", "Bilinmeyen Thread")
        logger.error(
            f"[THREAD ISTISNASI — {thread_adi}]\n"
            f"Tur  : {args.exc_type.__name__}\n"
            f"Mesaj: {args.exc_value}\n"
            f"{tb_str}"
        )

    threading.excepthook = _thread_hook
    logger.info("Threading exception hook kuruldu.")


def temel_baslatma_hazirligi() -> Path:
    """Dizin + logging hazirligini tek noktada toplar."""
    dizinleri_olustur()
    log_dosya = logging_kur()
    global_exception_hook_kur()
    threading_exception_hook_kur()
    return log_dosya
