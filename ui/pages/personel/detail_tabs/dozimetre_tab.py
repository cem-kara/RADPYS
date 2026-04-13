# -*- coding: utf-8 -*-
"""Personel detayinda Dozimetre olcum gecmisi sekmesi (salt-okunur)."""
from __future__ import annotations

from datetime import date

from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt

from app.config import HP10_TEHLIKE, HP10_UYARI, NDK_YILLIK
from app.services.dozimetre_service import DozimetreService
from ui.styles import T


_PERIYOT_ADI = {1: "1. Periyot", 2: "2. Periyot", 3: "3. Periyot", 4: "4. Periyot"}

_DURUM_RENK = {
    "Tehlike": "#e53935",
    "Uyari": "#fb8c00",
    "Normal": "#2e7d32",
}


class PersonelDozimetreTab(QWidget):
    """Personelin dozimetre olcum gecmisini ve ozetini gosterir."""

    def __init__(self, db=None, personel_id_getter=None, parent=None):
        super().__init__(parent)
        self._svc = DozimetreService(db) if db is not None else None
        self._personel_id_getter = personel_id_getter or (lambda: "")
        self._rows: list[dict] = []
        self._secili_yil: int | None = None
        self._build()

    # ─────────────────────────── UI inşa ────────────────────────────

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)

        self._uyari = QLabel("")
        self._uyari.setStyleSheet(f"color:{T.text3};font-size:11px;")
        root.addWidget(self._uyari)

        # Yıl filtresi
        filtre_satiri = QHBoxLayout()
        filtre_satiri.setSpacing(8)
        lbl_yil = QLabel("Yil:")
        lbl_yil.setStyleSheet(f"color:{T.text2};font-size:11px;")
        self._cmb_yil = QComboBox(self)
        self._cmb_yil.currentIndexChanged.connect(self._on_yil_degisti)
        filtre_satiri.addWidget(lbl_yil)
        filtre_satiri.addWidget(self._cmb_yil)
        filtre_satiri.addStretch(1)
        root.addLayout(filtre_satiri)

        # Özet kartlar
        ust = QHBoxLayout()
        ust.setSpacing(10)
        ust.addWidget(self._build_ozet_kart())
        ust.addWidget(self._build_doz_kart())
        ust.addStretch(1)
        root.addLayout(ust)

        # Ölçüm tablosu
        self._table = QTableWidget(self)
        self._table.setColumnCount(8)
        self._table.setHorizontalHeaderLabels(
            ["Yil", "Periyot", "Donem Adi", "Doz. No", "Tur", "Bolge", "Hp(10) mSv", "Hp(0,07) mSv"]
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self._table, 1)

    def _build_ozet_kart(self) -> QGroupBox:
        grp = QGroupBox("Olcum Ozeti", self)
        grp.setStyleSheet(
            f"QGroupBox{{border:1px solid {T.border};border-radius:{T.radius}px;padding-top:12px;}}"
        )
        gl = QGridLayout(grp)
        gl.setContentsMargins(12, 10, 12, 10)
        gl.setHorizontalSpacing(10)
        gl.setVerticalSpacing(6)

        self._lbl_toplam = self._stat_satiri(gl, 0, "Toplam Olcum")
        self._lbl_uyari = self._stat_satiri(gl, 1, "Uyari Durumu")
        self._lbl_tehlike = self._stat_satiri(gl, 2, "Tehlike Durumu")
        self._lbl_normal = self._stat_satiri(gl, 3, "Normal Durum")
        return grp

    def _build_doz_kart(self) -> QGroupBox:
        grp = QGroupBox("Doz Gostergesi", self)
        grp.setStyleSheet(
            f"QGroupBox{{border:1px solid {T.border};border-radius:{T.radius}px;padding-top:12px;}}"
        )
        gl = QGridLayout(grp)
        gl.setContentsMargins(12, 10, 12, 10)
        gl.setHorizontalSpacing(10)
        gl.setVerticalSpacing(6)

        self._lbl_max_hp10 = self._stat_satiri(gl, 0, "Maks Hp(10)")
        self._lbl_kumulatif = self._stat_satiri(gl, 1, "Kumulatif Hp(10)")
        self._lbl_ndk = self._stat_satiri(gl, 2, f"NDK ({NDK_YILLIK:.0f} mSv)")
        self._lbl_rapor = self._stat_satiri(gl, 3, "Rapor Sayisi")
        return grp

    @staticmethod
    def _stat_satiri(gl: QGridLayout, row: int, etiket: str) -> QLabel:
        lbl_e = QLabel(etiket + ":")
        lbl_e.setStyleSheet(f"color:{T.text2};font-size:11px;")
        lbl_v = QLabel("—")
        lbl_v.setStyleSheet(f"color:{T.text};font-size:11px;font-weight:600;")
        gl.addWidget(lbl_e, row, 0)
        gl.addWidget(lbl_v, row, 1)
        return lbl_v

    # ─────────────────────────── Veri yükleme ───────────────────────

    def yenile(self) -> None:
        if self._svc is None:
            return
        pid = self._personel_id_getter()
        if not pid:
            self._uyari.setText("Personel ID bulunamadi.")
            return

        self._uyari.setText("")
        self._rows = self._svc.personel_olcumleri(pid)
        self._doldur_yil_filtresi()
        self._guncelle_gorunum()

    def _doldur_yil_filtresi(self) -> None:
        self._cmb_yil.blockSignals(True)
        try:
            yillar = sorted({r["yil"] for r in self._rows if r.get("yil")}, reverse=True)
            onceki = self._secili_yil

            self._cmb_yil.clear()
            self._cmb_yil.addItem("Tum Yillar", None)
            for y in yillar:
                self._cmb_yil.addItem(str(y), y)

            # Önceki seçimi koru
            if onceki is not None:
                idx = self._cmb_yil.findData(onceki)
                if idx >= 0:
                    self._cmb_yil.setCurrentIndex(idx)
                    return
            # Varsayılan: en son yıl
            if yillar:
                self._cmb_yil.setCurrentIndex(1)
                self._secili_yil = yillar[0]
            else:
                self._secili_yil = None
        finally:
            self._cmb_yil.blockSignals(False)

    def _on_yil_degisti(self) -> None:
        self._secili_yil = self._cmb_yil.currentData()
        self._guncelle_gorunum()

    def _guncelle_gorunum(self) -> None:
        yil = self._secili_yil
        if yil is not None:
            gorunen = [r for r in self._rows if r.get("yil") == yil]
        else:
            gorunen = list(self._rows)

        self._doldur_ozet(gorunen)
        self._doldur_tablo(gorunen)

    # ─────────────────────────── Özet kartlar ───────────────────────

    def _doldur_ozet(self, rows: list[dict]) -> None:
        toplam = len(rows)
        uyari_n = sum(1 for r in rows if r.get("durum") == "Uyari")
        tehlike_n = sum(1 for r in rows if r.get("durum") == "Tehlike")
        normal_n = sum(1 for r in rows if r.get("durum") == "Normal")
        hp10_vals = [r["hp10"] for r in rows if r.get("hp10") is not None]
        max_hp10 = max(hp10_vals) if hp10_vals else None
        kumulatif = sum(hp10_vals) if hp10_vals else None
        raporlar = {r.get("rapor_no") for r in rows if str(r.get("rapor_no") or "").strip()}

        self._lbl_toplam.setText(str(toplam))
        self._lbl_uyari.setText(str(uyari_n))
        self._lbl_uyari.setStyleSheet(
            f"color:{_DURUM_RENK['Uyari'] if uyari_n else T.text};font-size:11px;font-weight:600;"
        )
        self._lbl_tehlike.setText(str(tehlike_n))
        self._lbl_tehlike.setStyleSheet(
            f"color:{_DURUM_RENK['Tehlike'] if tehlike_n else T.text};font-size:11px;font-weight:600;"
        )
        self._lbl_normal.setText(str(normal_n))

        self._lbl_max_hp10.setText(
            f"{max_hp10:.3f} mSv" if max_hp10 is not None else "—"
        )
        self._lbl_max_hp10.setStyleSheet(
            f"color:{self._hp10_renk(max_hp10)};font-size:11px;font-weight:600;"
        )

        self._lbl_kumulatif.setText(
            f"{kumulatif:.3f} mSv" if kumulatif is not None else "—"
        )
        # NDK yıllık durum (sadece tek yıl seçiliyse anlamlı)
        if kumulatif is not None and self._secili_yil is not None:
            asim = kumulatif > NDK_YILLIK
            ndk_text = f"{'ASIM' if asim else 'Iceride'} ({kumulatif:.2f}/{NDK_YILLIK:.0f} mSv)"
            ndk_renk = _DURUM_RENK["Tehlike"] if asim else _DURUM_RENK["Normal"]
        else:
            ndk_text = "—"
            ndk_renk = T.text
        self._lbl_ndk.setText(ndk_text)
        self._lbl_ndk.setStyleSheet(f"color:{ndk_renk};font-size:11px;font-weight:600;")

        self._lbl_rapor.setText(str(len(raporlar)))

    @staticmethod
    def _hp10_renk(val: float | None) -> str:
        if val is None:
              return T.text
        if val >= HP10_TEHLIKE:
            return _DURUM_RENK["Tehlike"]
        if val >= HP10_UYARI:
            return _DURUM_RENK["Uyari"]
        return _DURUM_RENK["Normal"]

    # ─────────────────────────── Tablo ──────────────────────────────

    def _doldur_tablo(self, rows: list[dict]) -> None:
        self._table.setRowCount(0)
        for r in rows:
            row_idx = self._table.rowCount()
            self._table.insertRow(row_idx)

            hp10 = r.get("hp10")
            renk = _DURUM_RENK.get(str(r.get("durum") or ""), None)

            vals = [
                str(r.get("yil") or ""),
                str(r.get("periyot") or ""),
                r.get("periyot_adi") or _PERIYOT_ADI.get(r.get("periyot"), ""),
                str(r.get("dozimetre_no") or ""),
                str(r.get("tur") or ""),
                str(r.get("bolge") or ""),
                f"{hp10:.3f}" if hp10 is not None else "—",
                f"{r['hp007']:.3f}" if r.get("hp007") is not None else "—",
            ]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if renk and col >= 6:
                    item.setForeground(__import__("PySide6.QtGui", fromlist=["QColor"]).QColor(renk))
                self._table.setItem(row_idx, col, item)

        self._table.resizeColumnsToContents()
