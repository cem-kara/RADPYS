# -*- coding: utf-8 -*-
"""
ui/pages/personel/personel_page.py
ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?
Personel modÃ¼lÃ¼nÃ¼n ana sayfasÄ±.

GÃ¶rÃ¼nÃ¼m:
  ï¿½"Oï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"ï¿½ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"ï¿½
  ï¿½",  PersonelListesi ï¿½",     PersonelDetay (tab'lar)     ï¿½",
  ï¿½",    (sol panel)   ï¿½",     veya boï¿½Y karï¿½YÄ±lama ekranÄ±   ï¿½",
  ï¿½""ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"ï¿½ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"~

Routing:
  - Listede satÄ±ra tÄ±klanÄ±nca ï¿½?' saï¿½Yda PersonelDetay aÃ§Ä±lÄ±r
  - "Geri" butonuna basÄ±nca   ï¿½?' saï¿½Yda karï¿½YÄ±lama ekranÄ±
  - "Yeni" butonuna basÄ±nca   ï¿½?' PersonelForm dialog
"""
from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QSplitter,
    QVBoxLayout, QLabel, QFrame,
)
from PySide6.QtCore import Qt
from ui.styles import T
from ui.components.async_runner import AsyncRunner
from ui.pages.personel.personel_listesi import PersonelListesi
from ui.pages.personel.personel_detay import PersonelDetay
from ui.pages.personel.personel_form import PersonelForm
from app.services.personel_service import PersonelService
from app.db.database import Database


class _KarsilamaEkrani(QWidget):
    """HenÃ¼z personel seÃ§ilmemiï¿½Yken gÃ¶sterilen ekran."""

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.setSpacing(12)

        from ui.styles.icons import Icons as _Icon
        ikon = _Icon.label("personel", T.text3, 48)
        ikon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ikon.setFixedSize(64, 64)
        lay.addWidget(ikon)

        lbl = QLabel("Personel seÃ§in")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(
            f"color:{T.text3}; font-size:18px; font-weight:600;"
        )
        lay.addWidget(lbl)

        alt = QLabel("Soldan bir personel seÃ§erek\nbilgilerini gÃ¶rÃ¼ntÃ¼leyebilirsiniz.")
        alt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        alt.setStyleSheet(f"color:{T.text3}; font-size:12px;")
        lay.addWidget(alt)


class PersonelPage(QWidget):
    """
    Personel modÃ¼lÃ¼ ana sayfasÄ±.

    KullanÄ±m:
        page = PersonelPage(db)
        # AppWindow'un stack'ine ekle
    """

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self._db  = db
        self._svc = PersonelService(db)
        self._build()

    # ï¿½"?ï¿½"? UI ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?

    def _build(self):
        kok = QHBoxLayout(self)
        kok.setContentsMargins(0, 0, 0, 0)
        kok.setSpacing(0)

        # Splitter: sol liste | saï¿½Y detay
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setHandleWidth(1)
        self._splitter.setStyleSheet(
            f"QSplitter::handle {{ background:{T.border}; }}"
        )

        # Sol panel ï¿½?" liste
        self._liste = PersonelListesi(self._svc)
        self._liste.setMinimumWidth(280)
        self._liste.secildi.connect(self._personel_sec)
        self._liste.yeni_istendi.connect(self._yeni_dialog)
        self._splitter.addWidget(self._liste)

        # Saï¿½Y panel ï¿½?" baï¿½YlangÄ±Ã§ta karï¿½YÄ±lama, tÄ±klanÄ±nca detay
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

        # Baï¿½YlangÄ±Ã§ oranÄ±: %28 liste, %72 detay
        self._splitter.setSizes([300, 900])
        kok.addWidget(self._splitter)

    # ï¿½"?ï¿½"? Routing ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?ï¿½"?

    def _personel_sec(self, personel_id: str):
        """Listeden personel seÃ§ildi ï¿½?' detayÄ± gÃ¶ster."""
        self._karsilama.setVisible(False)
        self._detay.setVisible(True)
        self._detay.yukle(personel_id)

    def _detay_kapat(self):
        """Geri butonuna basÄ±ldÄ± ï¿½?' karï¿½YÄ±lama ekranÄ±nÄ± gÃ¶ster."""
        self._detay.setVisible(False)
        self._karsilama.setVisible(True)

    def _yeni_dialog(self):
        """Yeni personel formu aÃ§."""
        dlg = PersonelForm(self._svc, parent=self)
        dlg.kaydedildi.connect(self._yeni_personel_eklendi)
        dlg.exec()

    def _yeni_personel_eklendi(self, personel_id: str):
        """Form kaydedildi ï¿½?' listeyi yenile + yeni kaydÄ± seÃ§."""
        self._liste.yenile()
        # Listenin yÃ¼klenmesi async ï¿½?" kÃ¼Ã§Ã¼k gecikme sonrasÄ± seÃ§
        from PySide6.QtCore import QTimer
        QTimer.singleShot(400, lambda: self._liste.sec(personel_id))
        self._personel_sec(personel_id)


