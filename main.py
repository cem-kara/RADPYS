# -*- coding: utf-8 -*-
"""main.py — REPYS 2.0 giriş noktası."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    from app.bootstrap import (
        qt_uygulamasini_hazirla,
        temel_baslatma_hazirligi,
        veri_katmanini_hazirla,
    )

    temel_baslatma_hazirligi()
    db = veri_katmanini_hazirla()
    app = qt_uygulamasini_hazirla(sys.argv)

    from ui.pages.kullanici.login_dialog import LoginDialog
    try:
        login = LoginDialog(db)
        if login.exec() != login.DialogCode.Accepted or login.oturum is None:
            return 0

        from ui.app_window import AppWindow

        pencere = AppWindow(db, oturum=login.oturum)
        pencere.show()

        return app.exec()
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
