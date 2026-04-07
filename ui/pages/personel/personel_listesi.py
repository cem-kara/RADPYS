# -*- coding: utf-8 -*-
"""
ui/pages/personel/personel_listesi.py
───────────────────────────────────────
Sol panel: arama + filtre + personel tablosu.
"""
from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QFrame,
)
from PySide6.QtCore import Qt, Signal
from ui.theme import T
from ui.components.buttons import PrimaryButton, GhostButton
from ui.components.forms import SearchBar
from ui.components.tables import DataTable, _TableModel
from ui.components.async_runner import AsyncRunner
from ui.components.alerts import AlertBar
from PySide6.QtGui import QColor


# ── Renklendirilmiş tablo modeli ──────────────────────────────────

class _PersonelModel(_TableModel):
    """Durum sütununu renklendirir."""

    def _foreground(self, key: str, deger, row: dict):
        if key == "durum":
            return {
                "aktif":   T.green2,
                "pasif":   T.text3,
                "ayrildi": T.red,
            }.get(str(deger or ""), None)
        return None

    def _display(self, key: str, deger, row: dict) -> str:
        if key == "durum":
            return {"aktif": "Aktif", "pasif": "Pasif",
                    "ayrildi": "Ayrıldı"}.get(str(deger or ""), str(deger or ""))
        if key == "ad_soyad":
            return f"{row.get('ad','')} {row.get('soyad','')}".strip()
        return str(deger or "")


# ── Ana widget ────────────────────────────────────────────────────

class PersonelListesi(QWidget):
    """
    Personel listesi paneli.

    Sinyaller:
        secildi(personel_id) — tabloda bir satıra tıklanınca
        yeni_istendi()       — "+" butonuna basılınca
    """

    secildi      = Signal(str)
    yeni_istendi = Signal()

    _KOLONLAR = [
        ("ad_soyad",      "Ad Soyad",    0),    # 0 = stretch
        ("tc_kimlik",     "TC",        110),
        ("kadro_unvani",  "Unvan",     130),
        ("gorev_yeri_ad", "Görev Yeri",120),
        ("durum",         "Durum",      72),
    ]

    def __init__(self, svc, parent=None):
        super().__init__(parent)
        self._svc   = svc
        self._tumveri: list[dict] = []
        self._build()
        self._yukle()

    # ── UI ────────────────────────────────────────────────────────

    def _build(self):
        kok = QVBoxLayout(self)
        kok.setContentsMargins(0, 0, 0, 0)
        kok.setSpacing(0)

        # Üst araç çubuğu
        ara_frame = QFrame()
        ara_frame.setStyleSheet(
            f"background:{T.bg1}; border-bottom:1px solid {T.border};"
        )
        ara_lay = QVBoxLayout(ara_frame)
        ara_lay.setContentsMargins(12, 10, 12, 10)
        ara_lay.setSpacing(8)

        ust = QHBoxLayout()
        lbl = QLabel("Personel")
        lbl.setStyleSheet(
            f"color:{T.text}; font-size:15px; font-weight:600;"
        )
        self._lbl_sayac = QLabel("0 kayıt")
        self._lbl_sayac.setStyleSheet(f"color:{T.text3}; font-size:11px;")
        btn_yeni = PrimaryButton("+ Yeni")
        btn_yeni.setFixedHeight(30)
        btn_yeni.clicked.connect(self.yeni_istendi)
        ust.addWidget(lbl)
        ust.addWidget(self._lbl_sayac)
        ust.addStretch()
        ust.addWidget(btn_yeni)
        ara_lay.addLayout(ust)

        # Arama + filtre satırı
        filtre_lay = QHBoxLayout()
        filtre_lay.setSpacing(8)
        self._arama = SearchBar("İsim, TC, unvan ara…")
        self._arama.textChanged.connect(self._filtrele)

        self._cb_durum = QComboBox()
        self._cb_durum.setFixedWidth(110)
        self._cb_durum.addItems(["Tümü", "Aktif", "Ayrıldı"])
        self._cb_durum.currentTextChanged.connect(self._filtrele)

        btn_yenile = GhostButton("↻")
        btn_yenile.setFixedSize(32, 32)
        btn_yenile.setToolTip("Yenile")
        btn_yenile.clicked.connect(self._yukle)

        filtre_lay.addWidget(self._arama, 1)
        filtre_lay.addWidget(self._cb_durum)
        filtre_lay.addWidget(btn_yenile)
        ara_lay.addLayout(filtre_lay)

        kok.addWidget(ara_frame)

        # Uyarı bandı
        self._alert = AlertBar(self)
        kok.addWidget(self._alert)

        # Tablo
        self._tablo = DataTable()
        self._model = _PersonelModel(self._KOLONLAR)
        self._tablo._model = self._model
        self._tablo._proxy.setSourceModel(self._model)
        self._tablo.kur_kolonlar(self._KOLONLAR, geren="ad_soyad")
        self._tablo.clicked.connect(self._satir_secildi)
        kok.addWidget(self._tablo, 1)

    # ── Veri ──────────────────────────────────────────────────────

    def _yukle(self):
        def _cek():
            return self._svc.listele(aktif_only=False)

        def _goster(veri: list[dict]):
            self._tumveri = veri
            self._filtrele()
            self._alert.temizle()

        def _hata(msg: str):
            self._alert.goster(msg)

        AsyncRunner(fn=_cek, on_done=_goster, on_error=_hata, parent=self).start()

    def _filtrele(self):
        metin  = self._arama.text().strip().lower()
        durum  = self._cb_durum.currentText()

        filtrelenmis = []
        for p in self._tumveri:
            # Durum filtresi
            if durum == "Aktif"   and p.get("durum") != "aktif":
                continue
            if durum == "Ayrıldı" and p.get("durum") != "ayrildi":
                continue

            # Metin araması
            if metin:
                aralik = " ".join([
                    p.get("ad", ""), p.get("soyad", ""),
                    p.get("tc_kimlik", ""), p.get("kadro_unvani", ""),
                    p.get("gorev_yeri_ad", ""),
                ]).lower()
                if metin not in aralik:
                    continue

            filtrelenmis.append(p)

        self._model.set_veri(filtrelenmis)
        self._lbl_sayac.setText(f"{len(filtrelenmis)} kayıt")

    def _satir_secildi(self, index):
        kaynak = self._tablo._proxy.mapToSource(index)
        satir  = self._model.get_satir(kaynak.row())
        if satir:
            self.secildi.emit(satir["id"])

    # ── Dışarıdan Kontrol ─────────────────────────────────────────

    def yenile(self):
        """Listeyi yeniden yükler."""
        self._yukle()

    def sec(self, personel_id: str):
        """Belirtilen personeli tabloda seçili yapar."""
        for r in range(self._model.rowCount()):
            satir = self._model.get_satir(r)
            if satir and satir["id"] == personel_id:
                proxy_idx = self._tablo._proxy.mapFromSource(
                    self._model.index(r, 0)
                )
                self._tablo.setCurrentIndex(proxy_idx)
                self._tablo.scrollTo(proxy_idx)
                break
