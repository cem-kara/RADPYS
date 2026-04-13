# -*- coding: utf-8 -*-
"""ui/pages/yonetim/sabitler_tab.py - DB'de saklanan sabitler icin yonetim sekmesi."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from app.exceptions import AppHatasi
from app.logger import exc_logla
from app.services.sabit_yonetim_service import SabitYonetimService
from ui.components import AlertBar, Card, DataTable, GhostButton, PrimaryButton
from ui.styles import T


class SabitlerTab(QWidget):
    """Lookup ve gorev_yeri tablolari icin CRUD ekrani."""

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self._svc = SabitYonetimService(db)
        self._secili_lookup_id: str | None = None
        self._secili_gorev_id: str | None = None
        self._build()
        self.yenile()

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        self._alert = AlertBar(self)
        lay.addWidget(self._alert)

        info = QLabel(
            "Bu ekranda lookup degerleri ve gorev yeri sabitleri duzenlenir. "
            "Kayitlar DB'de aninda guncellenir."
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
        body.addWidget(self._lookup_karti(), 1)
        body.addWidget(self._gorev_karti(), 1)
        lay.addLayout(body, 1)

    def _lookup_karti(self) -> Card:
        kart = Card(self)
        kl = kart.layout_

        baslik = QLabel("Lookup Sabitleri")
        baslik.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        kl.addWidget(baslik)

        frm = QGridLayout()
        frm.setHorizontalSpacing(8)
        frm.setVerticalSpacing(6)

        frm.addWidget(self._etiket("Kategori"), 0, 0)
        self._cb_lookup_kategori = QComboBox(self)
        self._cb_lookup_kategori.currentIndexChanged.connect(self._lookup_liste_yukle)
        frm.addWidget(self._cb_lookup_kategori, 0, 1)

        frm.addWidget(self._etiket("Yeni Kategori (opsiyonel)"), 1, 0)
        self._inp_yeni_kategori = QLineEdit(self)
        self._inp_yeni_kategori.setPlaceholderText("or: dozimetre_tur")
        frm.addWidget(self._inp_yeni_kategori, 1, 1)

        frm.addWidget(self._etiket("Deger"), 2, 0)
        self._inp_lookup_deger = QLineEdit(self)
        frm.addWidget(self._inp_lookup_deger, 2, 1)

        frm.addWidget(self._etiket("Siralama"), 3, 0)
        self._inp_lookup_sira = QLineEdit(self)
        self._inp_lookup_sira.setPlaceholderText("0")
        frm.addWidget(self._inp_lookup_sira, 3, 1)

        self._chk_lookup_aktif = QCheckBox("Aktif", self)
        self._chk_lookup_aktif.setChecked(True)
        frm.addWidget(self._chk_lookup_aktif, 4, 1)

        kl.addLayout(frm)

        btns = QHBoxLayout()
        self._btn_lookup_ekle = PrimaryButton("Ekle")
        self._btn_lookup_ekle.clicked.connect(self._lookup_ekle)
        self._btn_lookup_guncelle = GhostButton("Guncelle")
        self._btn_lookup_guncelle.clicked.connect(self._lookup_guncelle)
        self._btn_lookup_aktif = GhostButton("Aktif/Pasif")
        self._btn_lookup_aktif.clicked.connect(self._lookup_aktif_degistir)
        btns.addWidget(self._btn_lookup_ekle)
        btns.addWidget(self._btn_lookup_guncelle)
        btns.addWidget(self._btn_lookup_aktif)
        btns.addStretch(1)
        kl.addLayout(btns)

        self._tbl_lookup = DataTable(self)
        self._tbl_lookup.kur_kolonlar(
            [
                ("kategori", "Kategori", 120),
                ("deger", "Deger", 180),
                ("siralama", "Sira", 55),
                ("aktif_txt", "Durum", 70),
                ("id", "ID", 0),
            ],
            geren="deger",
        )
        self._tbl_lookup.clicked.connect(self._lookup_satir_secildi)
        kl.addWidget(self._tbl_lookup, 1)
        return kart

    def _gorev_karti(self) -> Card:
        kart = Card(self)
        kl = kart.layout_

        baslik = QLabel("Gorev Yeri Sabitleri")
        baslik.setStyleSheet(f"color:{T.text}; font-size:14px; font-weight:700;")
        kl.addWidget(baslik)

        frm = QGridLayout()
        frm.setHorizontalSpacing(8)
        frm.setVerticalSpacing(6)

        frm.addWidget(self._etiket("Ad"), 0, 0)
        self._inp_gorev_ad = QLineEdit(self)
        frm.addWidget(self._inp_gorev_ad, 0, 1)

        frm.addWidget(self._etiket("Kisaltma"), 1, 0)
        self._inp_gorev_kis = QLineEdit(self)
        frm.addWidget(self._inp_gorev_kis, 1, 1)

        self._chk_sua_hakki = QCheckBox("SUA Hakki", self)
        frm.addWidget(self._chk_sua_hakki, 2, 1)

        self._chk_gorev_aktif = QCheckBox("Aktif", self)
        self._chk_gorev_aktif.setChecked(True)
        frm.addWidget(self._chk_gorev_aktif, 3, 1)

        kl.addLayout(frm)

        btns = QHBoxLayout()
        self._btn_gorev_ekle = PrimaryButton("Ekle")
        self._btn_gorev_ekle.clicked.connect(self._gorev_ekle)
        self._btn_gorev_guncelle = GhostButton("Guncelle")
        self._btn_gorev_guncelle.clicked.connect(self._gorev_guncelle)
        self._btn_gorev_aktif = GhostButton("Aktif/Pasif")
        self._btn_gorev_aktif.clicked.connect(self._gorev_aktif_degistir)
        btns.addWidget(self._btn_gorev_ekle)
        btns.addWidget(self._btn_gorev_guncelle)
        btns.addWidget(self._btn_gorev_aktif)
        btns.addStretch(1)
        kl.addLayout(btns)

        self._tbl_gorev = DataTable(self)
        self._tbl_gorev.kur_kolonlar(
            [
                ("ad", "Ad", 190),
                ("kisaltma", "Kisaltma", 90),
                ("sua_hakki_txt", "SUA", 60),
                ("aktif_txt", "Durum", 70),
                ("id", "ID", 0),
            ],
            geren="ad",
        )
        self._tbl_gorev.clicked.connect(self._gorev_satir_secildi)
        kl.addWidget(self._tbl_gorev, 1)
        return kart

    @staticmethod
    def _etiket(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color:{T.text2}; font-size:11px; font-weight:600;")
        return lbl

    @staticmethod
    def _to_int(value: str, default: int = 0) -> int:
        try:
            return int(str(value or "").strip())
        except ValueError:
            return default

    def yenile(self) -> None:
        self._kategori_combo_doldur()
        self._lookup_liste_yukle()
        self._gorev_liste_yukle()

    # ── lookup olaylari ────────────────────────────────────────────

    def _kategori_combo_doldur(self) -> None:
        secili = self._cb_lookup_kategori.currentData() if hasattr(self, "_cb_lookup_kategori") else None
        kategoriler = self._svc.lookup_kategoriler()

        self._cb_lookup_kategori.blockSignals(True)
        self._cb_lookup_kategori.clear()
        self._cb_lookup_kategori.addItem("Tum Kategoriler", "")
        for kat in kategoriler:
            self._cb_lookup_kategori.addItem(kat, kat)
        idx = self._cb_lookup_kategori.findData(secili)
        self._cb_lookup_kategori.setCurrentIndex(idx if idx >= 0 else 0)
        self._cb_lookup_kategori.blockSignals(False)

    def _lookup_liste_yukle(self) -> None:
        kategori = str(self._cb_lookup_kategori.currentData() or "").strip() or None
        rows = self._svc.lookup_listele(kategori=kategori, include_pasif=True)
        for r in rows:
            r["aktif_txt"] = "Aktif" if int(r.get("aktif", 0)) else "Pasif"
        self._tbl_lookup.set_veri(rows)

    def _lookup_satir_secildi(self, _index) -> None:
        row = self._tbl_lookup.secili_satir()
        if not row:
            self._secili_lookup_id = None
            return
        self._secili_lookup_id = str(row.get("id") or "")
        self._inp_lookup_deger.setText(str(row.get("deger") or ""))
        self._inp_lookup_sira.setText(str(row.get("siralama") or 0))
        self._chk_lookup_aktif.setChecked(bool(int(row.get("aktif", 0))))

    def _lookup_ekle(self) -> None:
        self._alert.temizle()
        kategori = self._inp_yeni_kategori.text().strip() or str(self._cb_lookup_kategori.currentData() or "").strip()
        try:
            self._svc.lookup_ekle(
                kategori=kategori,
                deger=self._inp_lookup_deger.text(),
                siralama=self._to_int(self._inp_lookup_sira.text(), 0),
                aktif=self._chk_lookup_aktif.isChecked(),
            )
            self._inp_lookup_deger.clear()
            self._inp_lookup_sira.clear()
            self._inp_yeni_kategori.clear()
            self.yenile()
            self._alert.goster("Lookup sabiti eklendi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("SabitlerTab._lookup_ekle", exc)
            self._alert.goster(str(exc), "danger")

    def _lookup_guncelle(self) -> None:
        self._alert.temizle()
        if not self._secili_lookup_id:
            self._alert.goster("Lutfen guncellenecek bir lookup satiri secin.", "warning")
            return
        try:
            self._svc.lookup_guncelle(
                kayit_id=self._secili_lookup_id,
                deger=self._inp_lookup_deger.text(),
                siralama=self._to_int(self._inp_lookup_sira.text(), 0),
                aktif=self._chk_lookup_aktif.isChecked(),
            )
            self.yenile()
            self._alert.goster("Lookup sabiti guncellendi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("SabitlerTab._lookup_guncelle", exc)
            self._alert.goster(str(exc), "danger")

    def _lookup_aktif_degistir(self) -> None:
        self._alert.temizle()
        row = self._tbl_lookup.secili_satir()
        if not row:
            self._alert.goster("Lutfen bir lookup satiri secin.", "warning")
            return
        try:
            yeni = not bool(int(row.get("aktif", 0)))
            self._svc.lookup_aktiflik_degistir(str(row.get("id") or ""), yeni)
            self.yenile()
            self._alert.goster("Lookup durumu guncellendi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("SabitlerTab._lookup_aktif_degistir", exc)
            self._alert.goster(str(exc), "danger")

    # ── gorev yeri olaylari ────────────────────────────────────────

    def _gorev_liste_yukle(self) -> None:
        rows = self._svc.gorev_yeri_listele(include_pasif=True)
        for r in rows:
            r["aktif_txt"] = "Aktif" if int(r.get("aktif", 0)) else "Pasif"
            r["sua_hakki_txt"] = "Var" if int(r.get("sua_hakki", 0)) else "Yok"
        self._tbl_gorev.set_veri(rows)

    def _gorev_satir_secildi(self, _index) -> None:
        row = self._tbl_gorev.secili_satir()
        if not row:
            self._secili_gorev_id = None
            return
        self._secili_gorev_id = str(row.get("id") or "")
        self._inp_gorev_ad.setText(str(row.get("ad") or ""))
        self._inp_gorev_kis.setText(str(row.get("kisaltma") or ""))
        self._chk_sua_hakki.setChecked(bool(int(row.get("sua_hakki", 0))))
        self._chk_gorev_aktif.setChecked(bool(int(row.get("aktif", 0))))

    def _gorev_ekle(self) -> None:
        self._alert.temizle()
        try:
            self._svc.gorev_yeri_ekle(
                ad=self._inp_gorev_ad.text(),
                kisaltma=self._inp_gorev_kis.text(),
                sua_hakki=self._chk_sua_hakki.isChecked(),
                aktif=self._chk_gorev_aktif.isChecked(),
            )
            self._inp_gorev_ad.clear()
            self._inp_gorev_kis.clear()
            self._chk_sua_hakki.setChecked(False)
            self._chk_gorev_aktif.setChecked(True)
            self._gorev_liste_yukle()
            self._alert.goster("Gorev yeri eklendi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("SabitlerTab._gorev_ekle", exc)
            self._alert.goster(str(exc), "danger")

    def _gorev_guncelle(self) -> None:
        self._alert.temizle()
        if not self._secili_gorev_id:
            self._alert.goster("Lutfen guncellenecek bir gorev yeri secin.", "warning")
            return
        try:
            self._svc.gorev_yeri_guncelle(
                kayit_id=self._secili_gorev_id,
                ad=self._inp_gorev_ad.text(),
                kisaltma=self._inp_gorev_kis.text(),
                sua_hakki=self._chk_sua_hakki.isChecked(),
                aktif=self._chk_gorev_aktif.isChecked(),
            )
            self._gorev_liste_yukle()
            self._alert.goster("Gorev yeri guncellendi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("SabitlerTab._gorev_guncelle", exc)
            self._alert.goster(str(exc), "danger")

    def _gorev_aktif_degistir(self) -> None:
        self._alert.temizle()
        row = self._tbl_gorev.secili_satir()
        if not row:
            self._alert.goster("Lutfen bir gorev yeri secin.", "warning")
            return
        try:
            yeni = not bool(int(row.get("aktif", 0)))
            self._svc.gorev_yeri_aktiflik_degistir(str(row.get("id") or ""), yeni)
            self._gorev_liste_yukle()
            self._alert.goster("Gorev yeri durumu guncellendi.", "success")
        except AppHatasi as exc:
            self._alert.goster(str(exc), "warning")
        except Exception as exc:
            exc_logla("SabitlerTab._gorev_aktif_degistir", exc)
            self._alert.goster(str(exc), "danger")
