# -*- coding: utf-8 -*-
"""
ui/pages/personel/personel_page.py
────────────────────────────────────
Personel modülünün ana sayfası.

Görünüm:
  ┌──────────────────┬────────────────────────────────┐
  │  PersonelListesi │     PersonelDetay (tab'lar)     │
  │    (sol panel)   │     veya boş karşılama ekranı   │
  └──────────────────┴────────────────────────────────┘

Routing:
  - Listede satıra tıklanınca → sağda PersonelDetay açılır
  - "Geri" butonuna basınca   → sağda karşılama ekranı
  - "Yeni" butonuna basınca   → PersonelForm dialog
"""
from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QSplitter,
    QVBoxLayout, QLabel, QFrame,
)
from PySide6.QtCore import Qt
from ui.theme import T
from ui.components.async_runner import AsyncRunner
from ui.pages.personel.personel_listesi import PersonelListesi
from ui.pages.personel.personel_detay import PersonelDetay
from ui.pages.personel.personel_form import PersonelForm
from app.services.personel_service import PersonelService
from app.db.database import Database


class _KarsilamaEkrani(QWidget):
    """Henüz personel seçilmemişken gösterilen ekran."""

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(12)

        from ui.icons import Icon as _Icon
        ikon = _Icon.label("personel", T.text3, 48)
        ikon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ikon.setFixedSize(64, 64)
        lay.addWidget(ikon)

        lbl = QLabel("Personel seçin")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(
            f"color:{T.text3}; font-size:18px; font-weight:600;"
        )
        lay.addWidget(lbl)

        alt = QLabel("Soldan bir personel seçerek\nbilgilerini görüntüleyebilirsiniz.")
        alt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        alt.setStyleSheet(f"color:{T.text3}; font-size:12px;")
        lay.addWidget(alt)


class PersonelPage(QWidget):
    """
    Personel modülü ana sayfası.

    Kullanım:
        page = PersonelPage(db)
        # AppWindow'un stack'ine ekle
    """

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self._db  = db
        self._svc = PersonelService(db)
        self._build()

    # ── UI ────────────────────────────────────────────────────────

    def _build(self):
        kok = QHBoxLayout(self)
        kok.setContentsMargins(0, 0, 0, 0)
        kok.setSpacing(0)

        # Splitter: sol liste | sağ detay
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setHandleWidth(1)
        self._splitter.setStyleSheet(
            f"QSplitter::handle {{ background:{T.border}; }}"
        )

        # Sol panel — liste
        self._liste = PersonelListesi(self._svc)
        self._liste.setMinimumWidth(280)
        self._liste.secildi.connect(self._personel_sec)
        self._liste.yeni_istendi.connect(self._yeni_dialog)
        self._splitter.addWidget(self._liste)

        # Sağ panel — başlangıçta karşılama, tıklanınca detay
        self._sag = QFrame()
        self._sag_lay = QVBoxLayout(self._sag)
        self._sag_lay.setContentsMargins(0, 0, 0, 0)
        self._sag_lay.setSpacing(0)

        self._karsilama = _KarsilamaEkrani()
        self._detay     = PersonelDetay(self._svc)
        self._detay.kapandi.connect(self._detay_kapat)
        self._detay.setVisible(False)

        self._sag_lay.addWidget(self._karsilama)
        self._sag_lay.addWidget(self._detay)
        self._splitter.addWidget(self._sag)

        # Başlangıç oranı: %28 liste, %72 detay
        self._splitter.setSizes([300, 900])
        kok.addWidget(self._splitter)

    # ── Routing ───────────────────────────────────────────────────

    def _personel_sec(self, personel_id: str):
        """Listeden personel seçildi → detayı göster."""
        self._karsilama.setVisible(False)
        self._detay.setVisible(True)
        self._detay.yukle(personel_id)

    def _detay_kapat(self):
        """Geri butonuna basıldı → karşılama ekranını göster."""
        self._detay.setVisible(False)
        self._karsilama.setVisible(True)

    def _yeni_dialog(self):
        """Yeni personel formu aç."""
        dlg = PersonelForm(self._svc, parent=self)
        dlg.kaydedildi.connect(self._yeni_personel_eklendi)
        dlg.exec()

    def _yeni_personel_eklendi(self, personel_id: str):
        """Form kaydedildi → listeyi yenile + yeni kaydı seç."""
        self._liste.yenile()
        # Listenin yüklenmesi async — küçük gecikme sonrası seç
        from PySide6.QtCore import QTimer
        QTimer.singleShot(400, lambda: self._liste.sec(personel_id))
        self._personel_sec(personel_id)
