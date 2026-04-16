# -*- coding: utf-8 -*-
"""ui/pages/personel/dozimetre_import_page.py - RADAT PDF iceri aktarma."""
from __future__ import annotations

import re
import unicodedata
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.dozimetre_service import DozimetreService
from ui.components import AlertBar, AsyncRunner
from ui.styles import T


PREVIEW_COLS = [
    "Ad Soyad",
    "TC/ID",
    "Birim",
    "Dozimetre No",
    "Hp10",
    "Hp007",
    "Durum",
    "Eslesme",
]


def _norm_text(v: str) -> str:
    s = unicodedata.normalize("NFKD", str(v or "").upper())
    return s.encode("ascii", "ignore").decode()


def _match_tc(masked: str, real: str) -> bool:
    m = re.match(r"^([0-9]+)(\*+)([0-9]+)$", str(masked or "").strip())
    if not m:
        return False
    prefix, stars, suffix = m.group(1), m.group(2), m.group(3)
    expected = len(prefix) + len(stars) + len(suffix)
    return len(real) == expected and real.startswith(prefix) and real.endswith(suffix)


def _name_score(pdf_name: str, real_name: str) -> int:
    p_parts = [x for x in _norm_text(pdf_name).split() if x]
    r_parts = [x for x in _norm_text(real_name).split() if x]
    if not p_parts or not r_parts:
        return 0
    score = 0
    for pp in p_parts:
        segs = [s for s in pp.split("*") if s]
        for seg in segs:
            for rp in r_parts:
                if rp.startswith(seg):
                    score += len(seg)
                    break
    return score


def match_personel(row: dict, personel_list: list[dict]) -> Optional[dict]:
    tc_masked = str(row.get("PersonelID") or "")
    pdf_name = str(row.get("AdSoyad") or "")
    candidates = [
        p
        for p in personel_list
        if _match_tc(tc_masked, str(p.get("KimlikNo") or ""))
    ]
    if not candidates:
        return None

    best = None
    best_score = 0
    for c in candidates:
        score = _name_score(pdf_name, str(c.get("AdSoyad") or ""))
        if score > best_score:
            best_score = score
            best = c
    return best if best_score > 0 else None


def _parse_hp(raw) -> Optional[float]:
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    if "0,05" in s or "altinda" in _norm_text(s).lower():
        return 0.05
    s = s.replace(",", ".")
    try:
        v = float(s)
        return v if 0 <= v <= 500 else None
    except ValueError:
        return None


def _is_tc_masked(s: str) -> bool:
    return bool(re.match(r"^\d+\*+\d+$", str(s or "").strip()))


def _smart_parse_row(row: list) -> dict:
    birim = ""
    bolge = ""
    dzm_no = ""
    durum = ""
    hp10 = None
    hp007 = None

    r1 = str((row[1] if len(row) > 1 else "") or "").strip().replace("\n", " ")
    r2 = str((row[2] if len(row) > 2 else "") or "").strip().replace("\n", " ")

    if _is_tc_masked(r1.split()[0] if r1.split() else ""):
        tc_raw = r1.split()[0]
        ad_soyad = r2
    else:
        ad_soyad = r1
        tc_raw = r2.split()[0] if r2.split() else r2

    for i in range(3, len(row)):
        v = row[i]
        if not v:
            continue
        s = str(v).strip()
        s_norm = _norm_text(s).lower()

        if "radyoloji" in s_norm and not birim:
            birim = "Radyoloji"
        elif any(k in s_norm for k in ("vucut", "onluk", "bilek", "yaka")) and not bolge:
            bolge = s.replace("\n", " ")
        elif s.isdigit() and not dzm_no:
            dzm_no = s
        elif "sinirin" in s_norm or "asim" in s_norm:
            durum = s
        elif _parse_hp(s) is not None:
            if hp10 is None:
                hp10 = _parse_hp(s)
            elif hp007 is None:
                hp007 = _parse_hp(s)

    return {
        "AdSoyad": ad_soyad,
        "PersonelID": tc_raw,
        "CalistiBirim": birim or "Radyoloji",
        "VucutBolgesi": bolge,
        "DozimetreNo": dzm_no,
        "Hp10": hp10,
        "Hp007": hp007,
        "Durum": durum or "Sinirin Altinda",
    }


def parse_radat_pdf(pdf_path: str) -> tuple[dict, list[dict]]:
    try:
        import pdfplumber
    except Exception as exc:
        raise RuntimeError("pdfplumber paketi bulunamadi. requirements kurulumu gerekli.") from exc

    header: dict = {}
    rows: list[dict] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            text_norm = _norm_text(text)

            if "RaporNo" not in header:
                m = re.search(r"Rapor\s*(?:No|Numarasi)\s*[:\s]+([0-9]{3,12})", text_norm, re.IGNORECASE)
                if m:
                    header["RaporNo"] = m.group(1).strip()

            if "Periyot" not in header:
                m = re.search(
                    r"Periyot\s*/\s*Yil\s*[:\s]+(\d+)\s*\(([^)]+)\)\s*/\s*(\d{4})",
                    text_norm,
                    re.IGNORECASE,
                )
                if m:
                    header["Periyot"] = int(m.group(1))
                    header["PeriyotAdi"] = m.group(2).strip()
                    header["Yil"] = int(m.group(3))
                else:
                    # Alternatif format: "1. Periyot / 2026"
                    m2 = re.search(r"(\d+)\.?\s*Periyot\s*/\s*(\d{4})", text_norm, re.IGNORECASE)
                    if m2:
                        header["Periyot"] = int(m2.group(1))
                        header["Yil"] = int(m2.group(2))
                        header.setdefault("PeriyotAdi", f"{m2.group(1)}. Periyot")

            if "DozimetriTipi" not in header:
                m = re.search(r"Dozimetri\s+Tipi\s*[:\s]+([A-Za-z0-9]+)", text_norm, re.IGNORECASE)
                if m:
                    header["DozimetriTipi"] = m.group(1).strip()

            for table in page.extract_tables() or []:
                for row in table:
                    if not row or not row[0]:
                        continue
                    if not str(row[0]).strip().isdigit():
                        continue
                    rows.append(_smart_parse_row(row))

    return header, rows


class DozimetreImportPage(QWidget):
    """RADAT PDF import/preview/save sayfasi."""

    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self._svc = DozimetreService(db) if db is not None else None
        self._header: dict = {}
        self._rows: list[dict] = []
        self._load_runner: AsyncRunner | None = None
        self._save_runner: AsyncRunner | None = None
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        top = QHBoxLayout()
        ttl = QLabel("RADAT PDF Ice Aktarma")
        ttl.setStyleSheet(f"color:{T.text}; font-size:16px; font-weight:700;")
        top.addWidget(ttl)
        top.addStretch(1)
        self._btn_sec = QPushButton("PDF Sec")
        self._btn_sec.clicked.connect(self._pick_file)
        self._btn_kaydet = QPushButton("Veritabanina Kaydet")
        self._btn_kaydet.clicked.connect(self._save)
        self._btn_kaydet.setEnabled(False)
        top.addWidget(self._btn_sec)
        top.addWidget(self._btn_kaydet)
        root.addLayout(top)

        self._alert = AlertBar(self)
        root.addWidget(self._alert)

        self._info = QFrame(self)
        self._info.setStyleSheet(
            f"QFrame{{background:{T.bg1}; border:1px solid {T.border}; border-radius:{T.radius}px;}}"
        )
        info_l = QHBoxLayout(self._info)
        info_l.setContentsMargins(10, 8, 10, 8)
        self._lbl_info = QLabel("Dosya secilmedi")
        self._lbl_info.setStyleSheet(f"color:{T.text2};")
        info_l.addWidget(self._lbl_info)
        root.addWidget(self._info)

        self._bar = QProgressBar(self)
        self._bar.setRange(0, 0)
        self._bar.hide()
        root.addWidget(self._bar)

        self._table = QTableWidget(self)
        self._table.setColumnCount(len(PREVIEW_COLS))
        self._table.setHorizontalHeaderLabels(PREVIEW_COLS)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self._table, 1)

    def _pick_file(self) -> None:
        fp, _ = QFileDialog.getOpenFileName(self, "RADAT PDF Sec", "", "PDF Dosyalari (*.pdf)")
        if not fp:
            return
        self._load_pdf(fp)

    def _load_pdf(self, path: str) -> None:
        if self._load_runner and self._load_runner.isRunning():
            return

        self._btn_sec.setEnabled(False)
        self._btn_kaydet.setEnabled(False)
        self._bar.show()
        self._lbl_info.setText("PDF okunuyor...")

        def _fn():
            header, rows = parse_radat_pdf(path)
            personeller = self._svc.personel_listesi() if self._svc else []
            eslesen = eslesmez = 0
            for r in rows:
                p = match_personel(r, personeller)
                if p:
                    r["_personel_id"] = str(p["id"])
                    r["PersonelID"] = str(p["KimlikNo"])
                    r["AdSoyad"] = str(p["AdSoyad"])
                    r["_eslesti"] = True
                    eslesen += 1
                else:
                    r["_personel_id"] = ""
                    r["_eslesti"] = False
                    eslesmez += 1
            return header, rows, eslesen, eslesmez

        self._load_runner = AsyncRunner(fn=_fn, on_done=self._on_loaded, on_error=self._on_load_error, parent=self)
        self._load_runner.start()

    def _on_loaded(self, result) -> None:
        self._btn_sec.setEnabled(True)
        self._bar.hide()

        header, rows, eslesen, eslesmez = result
        self._header = header
        self._rows = rows
        self._btn_kaydet.setEnabled(bool(rows))

        self._lbl_info.setText(
            f"RaporNo: {header.get('RaporNo', '-')} | Yil: {header.get('Yil', '-')} | "
            f"Periyot: {header.get('Periyot', '-')} | Satir: {len(rows)} | Eslesen: {eslesen} | Eslesmeyen: {eslesmez}"
        )

        self._table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            vals = [
                str(r.get("AdSoyad") or ""),
                str(r.get("PersonelID") or ""),
                str(r.get("CalistiBirim") or ""),
                str(r.get("DozimetreNo") or ""),
                "" if r.get("Hp10") is None else f"{float(r.get('Hp10')):.3f}",
                "" if r.get("Hp007") is None else f"{float(r.get('Hp007')):.3f}",
                str(r.get("Durum") or ""),
                "Eslesti" if r.get("_eslesti") else "Bulunamadi",
            ]
            for c, v in enumerate(vals):
                it = QTableWidgetItem(v)
                it.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                if c >= 3:
                    it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if c == 7:
                    it.setForeground(QColor(T.teal2 if r.get("_eslesti") else (T.warning if hasattr(T, "warning") else "#e8a020")))
                self._table.setItem(i, c, it)

    def _on_load_error(self, msg: str) -> None:
        self._btn_sec.setEnabled(True)
        self._bar.hide()
        self._alert.goster(f"PDF okunamadi: {msg}", "danger")

    def _save(self) -> None:
        if not self._svc or not self._rows:
            return

        yil = self._header.get("Yil")
        periyot = self._header.get("Periyot")
        if not isinstance(yil, int) or yil <= 0:
            self._alert.goster("PDF basligindan yil bilgisi okunamadi. Kayit durduruldu.", "danger")
            return
        if not isinstance(periyot, int) or periyot < 1:
            self._alert.goster("PDF basligindan periyot bilgisi okunamadi (>=1). Kayit durduruldu.", "danger")
            return

        rapor_no = str(self._header.get("RaporNo") or "").strip()
        mevcut = len(self._svc.rapor_olcumleri(rapor_no)) if rapor_no else 0

        if mevcut >= len(self._rows) and len(self._rows) > 0:
            QMessageBox.information(self, "Zaten Kayitli", "Bu raporun tum satirlari zaten kayitli.")
            return

        if mevcut > 0:
            reply = QMessageBox.question(
                self,
                "Mukerrer Uyarisi",
                f"{mevcut} satir zaten kayitli. Kalan satirlar eklensin mi?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self._btn_kaydet.setEnabled(False)
        self._btn_sec.setEnabled(False)
        self._bar.show()

        def _save_fn():
            yeni = atlanan = eslesmeyen = 0
            for r in self._rows:
                pid = str(r.get("_personel_id") or "").strip()
                if not pid:
                    eslesmeyen += 1
                    continue

                ok = self._svc.olcum_ekle(
                    {
                        "personel_id": pid,
                        "rapor_no": rapor_no,
                        "yil": yil,
                        "periyot": periyot,
                        "periyot_adi": self._header.get("PeriyotAdi"),
                        "dozimetre_no": r.get("DozimetreNo"),
                        "tur": self._header.get("DozimetriTipi") or "RADAT",
                        "bolge": r.get("VucutBolgesi"),
                        "hp10": r.get("Hp10"),
                        "hp007": r.get("Hp007"),
                        "durum": r.get("Durum"),
                    }
                )
                if ok:
                    yeni += 1
                else:
                    atlanan += 1
            return yeni, atlanan, eslesmeyen

        self._save_runner = AsyncRunner(fn=_save_fn, on_done=self._on_saved, on_error=self._on_save_error, parent=self)
        self._save_runner.start()

    def _on_saved(self, result) -> None:
        yeni, atlanan, eslesmeyen = result
        self._bar.hide()
        self._btn_kaydet.setEnabled(True)
        self._btn_sec.setEnabled(True)

        self._alert.goster(
            f"Kayit tamamlandi. Yeni: {yeni}, Atlanan: {atlanan}, Eslesmeyen: {eslesmeyen}",
            "success",
        )

    def _on_save_error(self, msg: str) -> None:
        self._bar.hide()
        self._btn_kaydet.setEnabled(True)
        self._btn_sec.setEnabled(True)
        self._alert.goster(f"Kaydetme hatasi: {msg}", "danger")
