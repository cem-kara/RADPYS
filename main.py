# -*- coding: utf-8 -*-
"""main.py — REPYS 2.0 giriş noktası."""
from __future__ import annotations
import sys, logging
from pathlib import Path

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _dizinleri_olustur():
    from app.config import ZORUNLU_DIZINLER
    for d in ZORUNLU_DIZINLER:
        Path(d).mkdir(parents=True, exist_ok=True)


def _logging_kur():
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
    logging.getLogger("repys").info("REPYS 2.0 başlatılıyor…")


def main() -> int:
    _dizinleri_olustur()
    _logging_kur()

    from app.config import DB_PATH
    from app.db.database import Database
    from app.db.migrations import run as migrate
    db = Database(DB_PATH)
    migrate(db)

    import app.rbac as rbac
    rbac.init_dari_db(db)

    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, True)

    from ui.theme import apply as tema_uygula
    tema_uygula(app)

    from ui.pages.kullanici.login_dialog import LoginDialog
    login = LoginDialog(db)
    if login.exec() != login.DialogCode.Accepted or login.oturum is None:
        return 0

    from ui.app_window import AppWindow
    pencere = AppWindow(db, oturum=login.oturum)
    pencere.show()

    kod = app.exec()
    db.close()
    return kod


if __name__ == "__main__":
    sys.exit(main())
