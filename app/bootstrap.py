# -*- coding: utf-8 -*-
"""app/bootstrap.py — Uygulama baslatma yardimcilari."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from app.config import DB_PATH, LOG_DIR, ZORUNLU_DIZINLER
from app.db.database import Database
from app.db.migrations import run as migrate


def dizinleri_olustur(dizinler: list[Path] | None = None) -> None:
    """Uygulama icin gereken klasorleri olusturur."""
    for dizin in (dizinler or ZORUNLU_DIZINLER):
        Path(dizin).mkdir(parents=True, exist_ok=True)


def logging_kur(log_dir: Path | str | None = None) -> Path:
    """Dosya + konsol logging ayarini yapar ve log yolunu dondurur."""
    dizin = Path(log_dir) if log_dir is not None else Path(LOG_DIR)
    dizin.mkdir(parents=True, exist_ok=True)
    log_dosya = dizin / "repys.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_dosya, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )
    logging.getLogger("repys").info("REPYS 2.0 baslatiliyor...")
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

    app = QApplication(argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, True)

    from ui.theme import apply as tema_uygula

    tema_uygula(app)
    return app


def temel_baslatma_hazirligi() -> Path:
    """Dizin + logging hazirligini tek noktada toplar."""
    dizinleri_olustur()
    return logging_kur()
