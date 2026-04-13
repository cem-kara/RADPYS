# -*- coding: utf-8 -*-
"""ui/pages/yonetim/tatiller_tab.py - Resmi ve dini tatil yonetim sekmesi."""
from __future__ import annotations

from datetime import date

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from app.exceptions import AppHatasi
from app.logger import exc_logla
from app.services.tatil_yonetim_service import TatilYonetimService
from ui.components import AlertBar, Card, DataTable, GhostButton, PrimaryButton
from ui.styles import T

_TUR_SECENEKLER = [
    ("Tumu", ""),
    ("Resmi Tatil", "resmi"),
    ("Dini Tatil", "dini"),
]

_TUR_ETIKET = {
    "resmi": "Resmi",
    "dini": "Dini",
}


class TatillerTab(QWidget):
    """tatil tablosu icin CRUD yonetim sekmesi."""

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self._svc = TatilYonetimService(db)
        self._secili_tarih: str | None = None
        self._build()
        self.yenile()

    # ── insa ─────────────────────────────────────────────────────────

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        self._alert = AlertBar(self)
        lay.addWidget(self._alert)

        info = QLabel(
            "Resmi ve dini tatil gunleri buradan eklenir, duzenlenir veya silinir. "
            "Tarih formati: YYYY-AA-GG (ornek: 2025-01-01)."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            f"color:{T.text2}; font-size:11px; padding:8px 12px;"
            f"background:{T.bg4}; border-radius:{T.radius_sm}px;"
            f"border-left:3px solid {T.accent};"
        )
        lay.addWidget(info)

        body = QHBoxLayout()
        body.setSpacing(14)
        body.addWidget(self._form_karti(), 0)
        body.addWidget(self._liste_karti(), 1)
        lay.addLayout(body, 1)

    def _form_karti(self) -> Card:
        kart = Card(self)
        kart.setFixedWidth(280)
        kl = kart.layout_

        baslik = QLabel("Tatil Ekle / Duzenle")
        baslik.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        kl.addWidget(baslik)

        frm = QGridLayout()
        frm.setHorizontalSpacing(8)
        frm.setVerticalSpacing(8)

        frm.addWidget(self._etiket("Tarih (YYYY-AA-GG)"), 0, 0, 1, 2)
        self._inp_tarih = QLineEdit(self)
        self._inp_tarih.setPlaceholderText("2025-01-01")
        self._inp_tarih.setMinimumHeight(32)
        frm.addWidget(self._inp_tarih, 1, 0, 1, 2)

        frm.addWidget(self._etiket("Tatil Adi"), 2, 0, 1, 2)
        self._inp_ad = QLineEdit(self)
        self._inp_ad.setPlaceholderText("Yilbasi, Kurban Bayrami...")
        self._inp_ad.setMinimumHeight(32)
        frm.addWidget(self._inp_ad, 3, 0, 1, 2)

        frm.addWidget(self._etiket("Tur"), 4, 0)
        self._cb_tur = QComboBox(self)
        self._cb_tur.addItem("Resmi Tatil", "resmi")
        self._cb_tur.addItem("Dini Tatil", "dini")
        self._cb_tur.setMinimumHeight(32)
        frm.addWidget(self._cb_tur, 4, 1)

        self._chk_yarim_gun = QCheckBox("Yarim Gun Mesai", self)
        frm.addWidget(self._chk_yarim_gun, 5, 1)

        kl.addLayout(frm)

        kl.addWidget(self._ayrac())

        self._btn_ekle = PrimaryButton("Ekle")
        self._btn_ekle.clicked.connect(self._tatil_ekle)
        kl.addWidget(self._btn_ekle)

        self._btn_guncelle = GhostButton("Guncelle")
        self._btn_guncelle.clicked.connect(self._tatil_guncelle)
        kl.addWidget(self._btn_guncelle)

        self._btn_sil = GhostButton("Sil")
        self._btn_sil.clicked.connect(self._tatil_sil)
        kl.addWidget(self._btn_sil)

        kl.addStretch(1)

        # sekilde bugunku yili varsayilan olarak ayarla
        self._inp_tarih.setText(str(date.today().year) + "-")

        return kart

    def _liste_karti(self) -> Card:
        kart = Card(self)
        kl = kart.layout_

        ust = QHBoxLayout()
        ust.setSpacing(10)

        baslik = QLabel("Kayitli Tatiller")
        baslik.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        ust.addWidget(baslik, 1)

        ust.addWidget(self._etiket("Yil:"))
        self._cb_yil = QComboBox(self)
        self._cb_yil.setMinimumHeight(30)
        self._cb_yil.setMinimumWidth(80)
        self._cb_yil.currentIndexChanged.connect(self._liste_yukle)
        ust.addWidget(self._cb_yil)

        ust.addWidget(self._etiket("Tur:"))
        self._cb_filtre_tur = QComboBox(self)
        self._cb_filtre_tur.setMinimumHeight(30)
        for etiket, deger in _TUR_SECENEKLER:
            self._cb_filtre_tur.addItem(etiket, deger)
        self._cb_filtre_tur.currentIndexChanged.connect(self._liste_yukle)
        ust.addWidget(self._cb_filtre_tur)

        kl.addLayout(ust)

        self._tbl = DataTable(self)
        self._tbl.kur_kolonlar(
            [
                ("tarih", "Tarih", 110),
                ("ad", "Tatil Adi", 220),
                ("tur_txt", "Tur", 90),
                ("mesai_txt", "Mesai", 95),
            ],
            geren="ad",
        )
        self._tbl.clicked.connect(self._satir_secildi)
        kl.addWidget(self._tbl, 1)
        return kart

    # ── yardimcilar ──────────────────────────────────────────────────

    @staticmethod
    def _etiket(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{T.text2}; font-size:11px; font-weight:600;")
        return lbl

    @staticmethod
    def _ayrac() -> QWidget:
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background:{T.border};")
        return line

    def _formu_temizle(self) -> None:
        self._secili_tarih = None
        self._inp_tarih.setText(str(date.today().year) + "-")
        self._inp_ad.clear()
        self._cb_tur.setCurrentIndex(0)
        self._chk_yarim_gun.setChecked(False)

    # ── yenile / yukle ───────────────────────────────────────────────

    def yenile(self) -> None:
        self._doldur_yil_filtresi()
        self._liste_yukle()

    def _doldur_yil_filtresi(self) -> None:
        secili = self._cb_yil.currentData() if self._cb_yil.count() > 0 else None
        yillar = self._svc.mevcut_yillar()
        bugunun_yili = date.today().year
        if bugunun_yili not in yillar:
            yillar = [bugunun_yili] + yillar

        self._cb_yil.blockSignals(True)
        self._cb_yil.clear()
        self._cb_yil.addItem("Tum Yillar", None)
        for y in yillar:
            self._cb_yil.addItem(str(y), y)
        idx = self._cb_yil.findData(secili)
        self._cb_yil.setCurrentIndex(idx if idx >= 0 else 0)
        self._cb_yil.blockSignals(False)

    def _liste_yukle(self) -> None:
        yil = self._cb_yil.currentData()
        tur = str(self._cb_filtre_tur.currentData() or "").strip() or None
        rows = self._svc.listele(yil=yil, tur=tur)
        for r in rows:
            r["tur_txt"] = _TUR_ETIKET.get(str(r.get("tur") or ""), str(r.get("tur") or ""))
            r["mesai_txt"] = "Yarim Gun" if int(r.get("yarim_gun") or 0) == 1 else "Tam Tatil"
        self._tbl.set_veri(rows)

    def _satir_secildi(self, _index) -> None:
        row = self._tbl.secili_satir()
        if not row:
            self._secili_tarih = None
            return
        self._secili_tarih = str(row.get("tarih") or "")
        self._inp_tarih.setText(self._secili_tarih)
        self._inp_ad.setText(str(row.get("ad") or ""))
        tur_val = str(row.get("tur") or "resmi")
        idx = self._cb_tur.findData(tur_val)
        self._cb_tur.setCurrentIndex(idx if idx >= 0 else 0)
        self._chk_yarim_gun.setChecked(bool(int(row.get("yarim_gun") or 0)))

    # ── eylemler ─────────────────────────────────────────────────────

    def _tatil_ekle(self) -> None:
        self._alert.temizle()
        try:
            self._svc.ekle(
                tarih=self._inp_tarih.text(),
                ad=self._inp_ad.text(),
                tur=str(self._cb_tur.currentData() or "resmi"),
                yarim_gun=self._chk_yarim_gun.isChecked(),
            )
            self._formu_temizle()
            self.yenile()
            self._alert.goster("Tatil kaydedildi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("TatillerTab._tatil_ekle", exc)
            self._alert.goster("Beklenmeyen hata olustu.", "error")

    def _tatil_guncelle(self) -> None:
        self._alert.temizle()
        if not self._secili_tarih:
            self._alert.goster("Guncellemek icin listeden bir kayit secin.", "warning")
            return
        try:
            self._svc.guncelle(
                tarih=self._secili_tarih,
                ad=self._inp_ad.text(),
                tur=str(self._cb_tur.currentData() or "resmi"),
                yarim_gun=self._chk_yarim_gun.isChecked(),
            )
            self._formu_temizle()
            self.yenile()
            self._alert.goster("Tatil guncellendi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("TatillerTab._tatil_guncelle", exc)
            self._alert.goster("Beklenmeyen hata olustu.", "error")

    def _tatil_sil(self) -> None:
        self._alert.temizle()
        if not self._secili_tarih:
            self._alert.goster("Silmek icin listeden bir kayit secin.", "warning")
            return
        try:
            self._svc.sil(self._secili_tarih)
            self._formu_temizle()
            self.yenile()
            self._alert.goster("Tatil silindi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("TatillerTab._tatil_sil", exc)
            self._alert.goster("Beklenmeyen hata olustu.", "error")
