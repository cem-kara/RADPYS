# -*- coding: utf-8 -*-
"""
ui/pages/personel/personel_detay.py
────────────────────────────────────
Personel detay görünümü — tab container.

Sekmeler:
  Kimlik | İzin | Sağlık | Dozimetre | FHSZ | Belgeler

Sprint 2: Sadece Kimlik sekmesi aktif.
Diğerleri Sprint 3-5'te eklenecek — şu an placeholder gösterir.
"""
from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTabWidget, QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from ui.theme import T
from ui.components.badges import Badge
from ui.pages.personel.panels.kimlik_panel import KimlikPanel


def _placeholder_sekme(baslik: str) -> QWidget:
    """Henüz yazılmamış sekmeler için geçici widget."""
    w   = QWidget()
    lay = QVBoxLayout(w)
    lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl = QLabel(baslik)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(
        f"color:{T.text3}; font-size:18px; font-weight:600;"
    )
    lay.addWidget(lbl)
    alt = QLabel("Bu sekme ilerleyen sprintlerde eklenecek.")
    alt.setAlignment(Qt.AlignmentFlag.AlignCenter)
    alt.setStyleSheet(f"color:{T.text3}; font-size:12px;")
    lay.addWidget(alt)
    return w


class PersonelDetay(QWidget):
    """
    Tek personelin tüm detay bilgilerini gösteren tab container.

    Sinyaller:
        kapandi() — geri/kapat butonuna basılınca

    Kullanım:
        detay = PersonelDetay(svc)
        detay.yukle(personel_id)
    """

    kapandi = Signal()

    def __init__(self, svc, parent=None):
        super().__init__(parent)
        self._svc       = svc
        self._pid: str  = ""
        self._build()

    # ── UI ────────────────────────────────────────────────────────

    def _build(self):
        kok = QVBoxLayout(self)
        kok.setContentsMargins(0, 0, 0, 0)
        kok.setSpacing(0)

        # ── Üst başlık çubuğu ─────────────────────────────────────
        hdr = QFrame()
        hdr.setFixedHeight(52)
        hdr.setStyleSheet(
            f"background:{T.bg1}; border-bottom:1px solid {T.border};"
        )
        hdr_lay = QHBoxLayout(hdr)
        hdr_lay.setContentsMargins(16, 0, 16, 0)

        # Geri butonu
        from ui.components.buttons import GhostButton
        btn_geri = GhostButton("← Listeye Dön")
        btn_geri.setFixedHeight(30)
        btn_geri.clicked.connect(self.kapandi)

        self._lbl_ad   = QLabel("—")
        f = QFont(); f.setPointSize(13); f.setBold(True)
        self._lbl_ad.setFont(f)
        self._lbl_ad.setStyleSheet(f"color:{T.text};")

        self._badge_durum = Badge("aktif")

        hdr_lay.addWidget(btn_geri)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedWidth(1)
        sep.setStyleSheet(f"background:{T.border};")
        hdr_lay.addWidget(sep)

        hdr_lay.addWidget(self._lbl_ad)
        hdr_lay.addWidget(self._badge_durum)
        hdr_lay.addStretch()
        kok.addWidget(hdr)

        # ── Tab widget ────────────────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)
        kok.addWidget(self._tabs, 1)

        # Kimlik sekmesi — aktif
        self._kimlik = KimlikPanel(self._svc)
        self._kimlik.kaydedildi.connect(self._baslik_guncelle)
        self._tabs.addTab(self._kimlik, "👤  Kimlik")

        # Gelecek sekmeler — placeholder
        self._tabs.addTab(_placeholder_sekme("📅  İzin"),       "📅  İzin")
        self._tabs.addTab(_placeholder_sekme("🏥  Sağlık"),     "🏥  Sağlık")
        self._tabs.addTab(_placeholder_sekme("☢  Dozimetre"),   "☢  Dozimetre")
        self._tabs.addTab(_placeholder_sekme("📊  FHSZ"),       "📊  FHSZ")
        self._tabs.addTab(_placeholder_sekme("📁  Belgeler"),   "📁  Belgeler")

    # ── Veri ──────────────────────────────────────────────────────

    def yukle(self, personel_id: str):
        """Personeli yükler, tüm sekmeleri hazırlar."""
        self._pid = personel_id
        self._kimlik.yukle(personel_id)

        # Başlık için hızlı getir
        from ui.components.async_runner import AsyncRunner

        def _cek():
            return self._svc.getir(personel_id)

        def _goster(p: dict):
            self._baslik_guncelle_dict(p)

        AsyncRunner(fn=_cek, on_done=_goster, parent=self).start()

    def _baslik_guncelle(self, personel_id: str):
        """KimlikPanel kaydedildi sinyali → başlığı güncelle."""
        from ui.components.async_runner import AsyncRunner

        def _cek():
            return self._svc.getir(personel_id)

        AsyncRunner(fn=_cek,
                    on_done=self._baslik_guncelle_dict,
                    parent=self).start()

    def _baslik_guncelle_dict(self, p: dict):
        ad_soyad = f"{p.get('ad','')} {p.get('soyad','')}".strip()
        self._lbl_ad.setText(ad_soyad or "—")
        self._badge_durum.set(p.get("durum", "aktif"))
