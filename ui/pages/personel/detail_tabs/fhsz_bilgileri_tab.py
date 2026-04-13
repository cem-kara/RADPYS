# -*- coding: utf-8 -*-
"""Personel detayinda Fiili Hizmet bilgi sekmesi (salt-okunur)."""
from __future__ import annotations

from collections import defaultdict

from PySide6.QtCore import Qt
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

from app.services.fhsz_service import FhszService
from ui.styles import T


_AYLAR = {
    1: "Ocak",
    2: "Subat",
    3: "Mart",
    4: "Nisan",
    5: "Mayis",
    6: "Haziran",
    7: "Temmuz",
    8: "Agustos",
    9: "Eylul",
    10: "Ekim",
    11: "Kasim",
    12: "Aralik",
}

class PersonelFhszBilgileriTab(QWidget):
    """Personelin FHSZ kayitlarini bilgi paneli olarak gosterir."""

    def __init__(self, db=None, personel_id_getter=None, parent=None):
        super().__init__(parent)
        self._svc = FhszService(db) if db is not None else None
        self._personel_id_getter = personel_id_getter or (lambda: "")
        self._rows: list[dict] = []
        self._yil_map: dict[int, dict] = {}
        self._secili_yil_tercihi: int | None = None
        self._gorunum_modu_tercihi: str = "yil"

        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(10)

        self._uyari = QLabel("")
        self._uyari.setStyleSheet(f"color:{T.text3};font-size:11px;")
        root.addWidget(self._uyari)

        filtre_satiri = QHBoxLayout()
        filtre_satiri.setSpacing(8)
        lbl_mod = QLabel("Gorunum")
        lbl_mod.setStyleSheet(f"color:{T.text2};font-size:11px;")
        self._gorunum_modu = QComboBox(self)
        self._gorunum_modu.addItem("Yil Toplam", "yil")
        self._gorunum_modu.addItem("Yil + Donem", "donem")
        self._gorunum_modu.currentIndexChanged.connect(self._on_gorunum_modu_degisti)
        filtre_satiri.addWidget(lbl_mod)
        filtre_satiri.addWidget(self._gorunum_modu)
        filtre_satiri.addStretch(1)
        root.addLayout(filtre_satiri)

        ust = QHBoxLayout()
        ust.setSpacing(10)
        ust.addWidget(self._build_ozet_kart())
        ust.addWidget(self._build_son_yil_kart())
        ust.addStretch(1)
        root.addLayout(ust)

        self._table = QTableWidget(self)
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels(
            ["Yil", "Donem", "Top. Gun", "Top. Izin", "Fiili Saat", "Kumulatif", "Hak Edilen Sua"]
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self._table, 1)

    def _build_ozet_kart(self) -> QGroupBox:
        grp = QGroupBox("FHSZ Puantaj Ozeti", self)
        grp.setStyleSheet(
            f"QGroupBox{{border:1px solid {T.border};border-radius:{T.radius}px;padding-top:12px;}}"
        )
        gl = QGridLayout(grp)
        gl.setContentsMargins(12, 10, 12, 10)
        gl.setHorizontalSpacing(10)
        gl.setVerticalSpacing(6)

        self._lbl_toplam_kayit = self._stat_satiri(gl, 0, "Toplam Kayit")
        self._lbl_toplam_gun = self._stat_satiri(gl, 1, "Toplam Aylik Gun")
        self._lbl_toplam_izin = self._stat_satiri(gl, 2, "Toplam Kullanilan Izin")
        self._lbl_toplam_saat = self._stat_satiri(gl, 3, "Toplam Fiili Calisma")
        return grp

    def _build_son_yil_kart(self) -> QGroupBox:
        grp = QGroupBox("Yil Bazli Gosterge", self)
        grp.setStyleSheet(
            f"QGroupBox{{border:1px solid {T.border};border-radius:{T.radius}px;padding-top:12px;}}"
        )
        gl = QGridLayout(grp)
        gl.setContentsMargins(12, 10, 12, 10)
        gl.setHorizontalSpacing(10)
        gl.setVerticalSpacing(6)

        yil_lbl = QLabel("Yil Filtresi")
        yil_lbl.setStyleSheet(f"color:{T.text2};font-size:11px;")
        self._yil_filter = QComboBox(self)
        self._yil_filter.currentIndexChanged.connect(self._apply_filter)
        gl.addWidget(yil_lbl, 0, 0)
        gl.addWidget(self._yil_filter, 0, 1)

        self._lbl_yil_sayisi = self._stat_satiri(gl, 1, "Toplam Yil")
        self._lbl_son_yil = self._stat_satiri(gl, 2, "Son Kayit Yili")
        self._lbl_son_yil_saat = self._stat_satiri(gl, 3, "Son Yil Fiili Saat")
        self._lbl_son_yil_sua = self._stat_satiri(gl, 4, "Son Yil Hak Edilen Sua")
        self._lbl_ort_saat = self._stat_satiri(gl, 5, "Yillik Ortalama Fiili Saat")
        self._lbl_fark_saat = self._stat_satiri(gl, 6, "Saat Farki (Onceki Yil)")
        self._lbl_fark_sua = self._stat_satiri(gl, 7, "Sua Farki (Onceki Yil)")
        return grp

    def _stat_satiri(self, grid: QGridLayout, row: int, etiket: str) -> QLabel:
        k = QLabel(etiket)
        k.setStyleSheet(f"color:{T.text2};font-size:11px;")
        v = QLabel("-")
        v.setStyleSheet(f"color:{T.text};font-size:12px;font-weight:700;")
        v.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(k, row, 0)
        grid.addWidget(v, row, 1)
        return v

    def _to_int(self, val) -> int:
        try:
            return int(float(str(val or 0).replace(",", ".")))
        except (TypeError, ValueError):
            return 0

    def _to_float(self, val) -> float:
        try:
            return float(str(val or 0).replace(",", "."))
        except (TypeError, ValueError):
            return 0.0

    def _clear(self) -> None:
        for lbl in (
            self._lbl_toplam_kayit,
            self._lbl_toplam_gun,
            self._lbl_toplam_izin,
            self._lbl_toplam_saat,
            self._lbl_yil_sayisi,
            self._lbl_son_yil,
            self._lbl_son_yil_saat,
            self._lbl_son_yil_sua,
            self._lbl_ort_saat,
            self._lbl_fark_saat,
            self._lbl_fark_sua,
        ):
            lbl.setText("-")
        self._yil_filter.blockSignals(True)
        self._yil_filter.clear()
        self._yil_filter.addItem("Tumu", None)
        self._yil_filter.blockSignals(False)
        self._table.setRowCount(0)

    def _on_gorunum_modu_degisti(self) -> None:
        self._gorunum_modu_tercihi = str(self._gorunum_modu.currentData() or "yil")
        self._apply_filter()

    @staticmethod
    def _fark_metin(deger: float) -> str:
        if deger > 0:
            return f"+{deger:.0f}"
        if deger < 0:
            return f"{deger:.0f}"
        return "0"

    def _set_fark_etiket(self, lbl: QLabel, deger: float) -> None:
        lbl.setText(self._fark_metin(deger))
        if deger > 0:
            lbl.setStyleSheet(f"color:{T.green2};font-size:12px;font-weight:700;")
        elif deger < 0:
            lbl.setStyleSheet(f"color:{T.red};font-size:12px;font-weight:700;")
        else:
            lbl.setStyleSheet(f"color:{T.text2};font-size:12px;font-weight:700;")

    def _yil_filtrele(self) -> tuple[list[int], dict[int, dict]]:
        secili = self._yil_filter.currentData()
        if secili is None:
            yillar = sorted(self._yil_map.keys(), reverse=True)
            return yillar, self._yil_map
        yil = int(secili)
        if yil not in self._yil_map:
            return [], {}
        return [yil], {yil: self._yil_map[yil]}

    def _detay_satirlari(self, yillar: list[int]) -> list[dict]:
        secili_set = set(yillar)
        rows = []
        yil_kum = defaultdict(float)
        for r in sorted(self._rows, key=lambda x: (self._to_int(x.get("yil")), self._to_int(x.get("donem")))):
            yil = self._to_int(r.get("yil"))
            if yil not in secili_set:
                continue
            donem = self._to_int(r.get("donem"))
            saat = self._to_float(r.get("fiili_saat"))
            yil_kum[yil] += saat
            rows.append(
                {
                    "yil": yil,
                    "donem": _AYLAR.get(donem, str(donem) if donem else "-"),
                    "gun": self._to_int(r.get("aylik_gun")),
                    "izin": self._to_int(r.get("izin_gun")),
                    "saat": saat,
                    "kumulatif": yil_kum[yil],
                    "sua": self._svc.sua_hak_edis_hesapla(yil_kum[yil]),
                }
            )
        return list(reversed(rows))

    def _apply_filter(self) -> None:
        yillar, filt_map = self._yil_filtrele()
        self._secili_yil_tercihi = self._yil_filter.currentData()

        toplam_kayit = len(yillar)
        toplam_gun = sum(v["gun"] for v in filt_map.values())
        toplam_izin = sum(v["izin"] for v in filt_map.values())
        toplam_saat = sum(v["saat"] for v in filt_map.values())

        self._lbl_toplam_kayit.setText(str(toplam_kayit))
        self._lbl_toplam_gun.setText(str(toplam_gun))
        self._lbl_toplam_izin.setText(str(toplam_izin))
        self._lbl_toplam_saat.setText(f"{toplam_saat:.0f}")

        if yillar:
            son_yil = yillar[0]
            son_yil_saat = float(filt_map[son_yil]["saat"])
            son_yil_sua = self._svc.sua_hak_edis_hesapla(son_yil_saat)
            ort = toplam_saat / toplam_kayit if toplam_kayit else 0.0
            self._lbl_yil_sayisi.setText(str(toplam_kayit))
            self._lbl_son_yil.setText(str(son_yil))
            self._lbl_son_yil_saat.setText(f"{son_yil_saat:.0f}")
            self._lbl_son_yil_sua.setText(str(son_yil_sua))
            self._lbl_ort_saat.setText(f"{ort:.1f}")

            prev_candidates = [y for y in self._yil_map.keys() if y < son_yil]
            if prev_candidates:
                prev_yil = max(prev_candidates)
                prev_saat = float(self._yil_map[prev_yil]["saat"])
                prev_sua = self._svc.sua_hak_edis_hesapla(prev_saat)
                self._set_fark_etiket(self._lbl_fark_saat, son_yil_saat - prev_saat)
                self._set_fark_etiket(self._lbl_fark_sua, float(son_yil_sua - prev_sua))
            else:
                self._lbl_fark_saat.setText("-")
                self._lbl_fark_sua.setText("-")
        else:
            self._lbl_yil_sayisi.setText("0")
            self._lbl_son_yil.setText("-")
            self._lbl_son_yil_saat.setText("0")
            self._lbl_son_yil_sua.setText("0")
            self._lbl_ort_saat.setText("0.0")
            self._lbl_fark_saat.setText("-")
            self._lbl_fark_sua.setText("-")

        mod = str(self._gorunum_modu.currentData() or "yil")
        if mod == "donem":
            satirlar = self._detay_satirlari(yillar)
        else:
            satirlar = []
            for yil in yillar:
                gun = filt_map[yil]["gun"]
                izin = filt_map[yil]["izin"]
                saat = float(filt_map[yil]["saat"])
                sua = self._svc.sua_hak_edis_hesapla(saat)
                satirlar.append(
                    {
                        "yil": yil,
                        "donem": "Toplam",
                        "gun": gun,
                        "izin": izin,
                        "saat": saat,
                        "kumulatif": saat,
                        "sua": sua,
                    }
                )

        self._table.setRowCount(len(satirlar))
        for i, row in enumerate(satirlar):
            row_vals = [
                str(row["yil"]),
                str(row["donem"]),
                str(row["gun"]),
                str(row["izin"]),
                f"{float(row['saat']):.0f}",
                f"{float(row['kumulatif']):.0f}",
                str(row["sua"]),
            ]
            for c, v in enumerate(row_vals):
                item = QTableWidgetItem(v)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._table.setItem(i, c, item)

        if not satirlar:
            self._uyari.setText(
                "Bu personel icin FHSZ kaydi bulunamadi. Fiili Hizmet ekranindan donem kaydi olusturabilirsiniz."
            )
        elif len(yillar) == 0:
            self._uyari.setText("Secili filtre icin kayit bulunamadi.")
        else:
            self._uyari.setText("")

    def _populate_filter(self, yillar: list[int]) -> None:
        self._yil_filter.blockSignals(True)
        self._yil_filter.clear()
        self._yil_filter.addItem("Tumu", None)
        for yil in yillar:
            self._yil_filter.addItem(str(yil), yil)

        if self._secili_yil_tercihi is not None:
            idx = self._yil_filter.findData(self._secili_yil_tercihi)
            if idx >= 0:
                self._yil_filter.setCurrentIndex(idx)
        self._yil_filter.blockSignals(False)

    def yenile(self) -> None:
        pid = str(self._personel_id_getter() or "").strip()
        if not pid or self._svc is None:
            self._uyari.setText("Personel secimi bulunamadi.")
            self._clear()
            return

        self._uyari.setText("")
        self._rows = self._svc.personel_kayitlari_listele(pid)

        yil_map: dict[int, dict] = defaultdict(lambda: {"gun": 0, "izin": 0, "saat": 0.0})
        for r in self._rows:
            yil = self._to_int(r.get("yil"))
            yil_map[yil]["gun"] += self._to_int(r.get("aylik_gun"))
            yil_map[yil]["izin"] += self._to_int(r.get("izin_gun"))
            yil_map[yil]["saat"] += self._to_float(r.get("fiili_saat"))

        self._yil_map = {y: yil_map[y] for y in yil_map.keys() if y > 0}
        yillar = sorted(self._yil_map.keys(), reverse=True)
        idx = self._gorunum_modu.findData(self._gorunum_modu_tercihi)
        if idx >= 0:
            self._gorunum_modu.blockSignals(True)
            self._gorunum_modu.setCurrentIndex(idx)
            self._gorunum_modu.blockSignals(False)
        self._populate_filter(yillar)
        self._apply_filter()
