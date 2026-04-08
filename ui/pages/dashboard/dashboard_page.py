# -*- coding: utf-8 -*-
"""
ui/pages/dashboard/dashboard_page.py
─────────────────────────────────────
Dashboard ana sayfası — Sprint 6'da detaylandırılacak.
"""
from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QFrame, QScrollArea,
)
from PySide6.QtCore import Qt
from ui.theme import T
from app.db.database import Database


class _StatKart(QFrame):
    def __init__(self, ikon: str, baslik: str,
                 deger: str, alt: str, renk: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"QFrame{{background:{T.bg1};"
            f"border:1px solid rgba(90,130,200,0.10);"
            f"border-radius:10px;}}"
            f"QFrame:hover{{border-color:rgba(90,130,200,0.22);}}"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(4)

        baslik_lay = QHBoxLayout()
        b = QLabel(baslik.upper())
        b.setStyleSheet(
            f"color:{T.text3};font-size:9px;font-weight:700;"
            f"letter-spacing:0.1em;font-family:'Consolas','Courier New',monospace;"
        )
        from ui.icons import Icon as _Ico
        ikon_lbl = _Ico.label(ikon, renk, 20)
        ikon_lbl.setFixedSize(22, 22)
        baslik_lay.addWidget(b)
        baslik_lay.addStretch()
        baslik_lay.addWidget(ikon_lbl)
        lay.addLayout(baslik_lay)

        d = QLabel(deger)
        d.setStyleSheet(
            f"color:{renk};font-size:30px;font-weight:800;"
            f"letter-spacing:-0.5px;font-family:'Segoe UI',system-ui,sans-serif;"
        )
        lay.addWidget(d)

        # İnce progress çizgisi
        prog_track = QFrame()
        prog_track.setFixedHeight(2)
        prog_track.setStyleSheet(
            f"background:rgba(90,130,200,0.10);border-radius:1px;"
        )
        lay.addWidget(prog_track)

        a = QLabel(alt)
        a.setStyleSheet(f"color:{T.text3};font-size:10px;")
        lay.addWidget(a)


class DashboardPage(QWidget):
    def __init__(self, db: Database = None, parent=None):
        super().__init__(parent)
        self._db = db
        self.setStyleSheet(f"background:{T.bg0};")
        self._build()
        if db:
            self._yukle()

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background:transparent;")
        scroll.setGeometry(self.rect())

        ic = QWidget()
        ic.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(ic)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(16)

        # Başlık
        hdr = QHBoxLayout()
        tit = QLabel("Dashboard")
        tit.setStyleSheet(
            f"color:{T.text};font-size:20px;font-weight:800;letter-spacing:-0.3px;"
        )
        hdr.addWidget(tit)
        hdr.addStretch()
        lay.addLayout(hdr)

        # Stat kartları grid
        grid = QGridLayout()
        grid.setSpacing(10)

        self._kartlar = [
            _StatKart("personel", "Aktif Personel",   "—", "yükleniyor...", T.accent2),
            _StatKart("izin",     "Bugün İzinli",     "—", "aktif izin",   T.amber),
            _StatKart("saglik",   "Yaklaşan Muayene", "—", "30 gün içinde", T.teal2),
            _StatKart("dozimetre","Doz Aşımı",        "—", "son periyot",  T.red2),
        ]
        for i, k in enumerate(self._kartlar):
            grid.addWidget(k, 0, i)

        lay.addLayout(grid)
        lay.addStretch()
        scroll.setWidget(ic)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        for child in self.children():
            if isinstance(child, QScrollArea):
                child.setGeometry(self.rect())

    def _yukle(self):
        try:
            aktif = self._db.fetchval(
                "SELECT COUNT(*) FROM personel WHERE durum='aktif'"
            ) or 0
            self._kartlar[0].findChild(QLabel, "").setText(str(aktif))
        except Exception:
            pass
