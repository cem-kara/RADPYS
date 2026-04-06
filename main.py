# -*- coding: utf-8 -*-
"""
main.py
───────
REPYS 2.0 — Uygulama giriş noktası.

Başlatma sırası:
  1. Dizinleri oluştur
  2. Logging kur
  3. Database aç + migration çalıştır
  4. QApplication + tema
  5. Ana pencereyi göster
"""
from __future__ import annotations
import sys
import logging
from pathlib import Path

# Proje kökünü sys.path'e ekle (IDE olmadan çalıştırma için)
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _dizinleri_olustur() -> None:
    from app.config import ZORUNLU_DIZINLER
    for dizin in ZORUNLU_DIZINLER:
        Path(dizin).mkdir(parents=True, exist_ok=True)


def _logging_kur() -> None:
    from app.config import LOG_DIR
    log_dosya = Path(LOG_DIR) / "repys.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_dosya, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logging.getLogger("repys").info("=" * 60)
    logging.getLogger("repys").info("REPYS 2.0 başlatılıyor…")


def main() -> int:
    _dizinleri_olustur()
    _logging_kur()

    # DB
    from app.config import DB_PATH
    from app.db.database import Database
    from app.db.migrations import run as migration_calistir

    db = Database(DB_PATH)
    migration_calistir(db)

    # Qt
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt

    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, True)

    # Tema
    from ui.theme import apply as tema_uygula
    tema_uygula(app)

    # Pencere
    from ui.app_window import AppWindow
    pencere = AppWindow(db)
    pencere.show()

    kod = app.exec()
    db.close()
    return kod


if __name__ == "__main__":
    sys.exit(main())
