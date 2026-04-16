# -*- coding: utf-8 -*-
"""ui/pages/personel/fhsz_yonetim_page.py - FHSZ donem yonetim ekrani."""
from __future__ import annotations

from datetime import date, timedelta

from PySide6.QtCore import QPersistentModelIndex, Qt
from PySide6.QtGui import QColor, QFont, QPainterPath, QPen, QBrush, QPainter
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QStyledItemDelegate,
    QListView,
    QStyle,
)

from app.logger import exc_logla
from app.services.fhsz_service import FhszService
from ui.components import AlertBar, PrimaryButton
from ui.styles import T


C_PID = 0
C_TC = 1
C_AD = 2
C_BIRIM = 3
C_KOSUL = 4
C_GUN = 5
C_IZIN = 6
C_SAAT = 7
C_NOT = 8

# ─── Koşul Delegate için Renk Paletleri ───
_KOSUL_ITEMS = ["Koşul A", "Koşul B"]
_K_A = {
    "badge_bg": QColor(30, 90, 40, 200),
    "badge_brd": QColor("#4caf50"),
    "text": QColor("#c8f7c5"),
}
_K_B = {
    "badge_bg": QColor(20, 70, 150, 200),
    "badge_brd": QColor("#42a5f5"),
    "text": QColor("#bbdefb"),
}


class KosulDelegate(QStyledItemDelegate):
    """Çalışma Koşulu A / B seçici delegate.
    
    Badge olarak gösterilir; tıklama ile büyük combo açılır.
    """

    def paint(self, painter, option, index):
        text = str(index.data(Qt.ItemDataRole.DisplayRole) or "Koşul B")
        is_a = "A" in text.upper()
        clr = _K_A if is_a else _K_B

        # Satır seçili arka plan
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, QColor(29, 117, 254, 50))
        else:
            painter.fillRect(option.rect, QColor("transparent"))

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Badge alanı
        r = option.rect.adjusted(8, 6, -8, -6)
        path = QPainterPath()
        path.addRoundedRect(r, 6, 6)
        painter.setBrush(QBrush(clr["badge_bg"]))
        painter.setPen(QPen(clr["badge_brd"], 1.5))
        painter.drawPath(path)

        # Badge metni
        painter.setPen(clr["text"])
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(r, Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(_KOSUL_ITEMS)
        model_index = QPersistentModelIndex(index)
        # Büyük popup için özel view
        view = QListView()
        view.setStyleSheet(f"""
            QListView {{
                background-color: {T.bg1};
                color: {T.text};
                border: 1.5px solid {T.accent};
                font-size: 12px;
                font-weight: 700;
                outline: none;
            }}
            QListView::item {{
                min-height: 40px;
                padding: 0 12px;
            }}
            QListView::item:selected {{
                background-color: rgba(29,117,254,0.2);
                color: {T.accent};
            }}
        """)
        editor.setView(view)
        editor.currentTextChanged.connect(
            lambda text, m=index.model(), idx=model_index: m.setData(idx, text, Qt.ItemDataRole.DisplayRole)
        )
        editor.currentIndexChanged.connect(lambda _=0, e=editor: self._commit_and_close_editor(e))
        return editor

    def setEditorData(self, editor, index):
        text = str(index.data(Qt.ItemDataRole.DisplayRole) or "Koşul B")
        secili = text if text in _KOSUL_ITEMS else "Koşul B"
        editor.blockSignals(True)
        editor.setCurrentText(secili)
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.ItemDataRole.DisplayRole)

    def _commit_and_close_editor(self, editor: QComboBox) -> None:
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, QStyledItemDelegate.EndEditHint.NoHint)


class FhszYonetimPage(QWidget):
    """Donem bazli FHSZ puantaj kayitlarini gosterir ve kaydeder."""

    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self._svc = FhszService(db)

        self.setStyleSheet(f"background:{T.bg0};")
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(10)

        self._alert = AlertBar(self)
        root.addWidget(self._alert)

        filt = QFrame(self)
        filt.setStyleSheet(
            f"QFrame{{background:{T.bg1}; border:1px solid {T.border}; border-radius:{T.radius}px;}}"
        )
        fl = QHBoxLayout(filt)
        fl.setContentsMargins(10, 8, 10, 8)
        fl.setSpacing(8)

        yl = QLabel("Yil")
        yl.setStyleSheet(f"color:{T.text2}; font-size:11px;")
        self._yil = QComboBox(self)
        bugun = date.today()
        for y in range(2021, bugun.year + 3):
            self._yil.addItem(str(y), y)
        self._yil.setCurrentText(str(bugun.year))
        self._yil.currentIndexChanged.connect(self._donem_guncelle)

        ay = QLabel("Ay")
        ay.setStyleSheet(f"color:{T.text2}; font-size:11px;")
        self._ay = QComboBox(self)
        ay_adlari = [
            "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
            "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
        ]
        for i, ay_adi in enumerate(ay_adlari, 1):
            self._ay.addItem(ay_adi, i)
        self._ay.setCurrentIndex(bugun.month - 1)
        self._ay.currentIndexChanged.connect(self._donem_guncelle)

        self._lbl_donem = QLabel("Dönem: —")
        self._lbl_donem.setStyleSheet(f"color:{T.text}; font-size:10px;")
        
        self._lbl_aylik_gun = QLabel("Aylik Gun: 0")
        self._lbl_aylik_gun.setStyleSheet(f"color:{T.text2}; font-size:10px;")

        self._btn_hesapla = PrimaryButton("Hesapla")
        self._btn_hesapla.clicked.connect(self._hesapla)
        self._btn_kaydet = PrimaryButton("Kaydet / Guncelle")
        self._btn_kaydet.clicked.connect(self._kaydet)

        fl.addWidget(yl)
        fl.addWidget(self._yil)
        fl.addSpacing(12)
        fl.addWidget(ay)
        fl.addWidget(self._ay)
        fl.addSpacing(12)
        fl.addWidget(self._lbl_donem)
        fl.addSpacing(8)
        fl.addWidget(self._lbl_aylik_gun)
        fl.addStretch(1)
        fl.addWidget(self._btn_hesapla)
        fl.addWidget(self._btn_kaydet)

        root.addWidget(filt)

        self._tablo = QTableWidget(self)
        self._tablo.setColumnCount(9)
        self._tablo.setHorizontalHeaderLabels(
            [
                "personel_id",
                "TC",
                "Ad Soyad",
                "Birim",
                "Kosul",
                "Aylik Gun",
                "Izin Gun",
                "Fiili Saat",
                "Not",
            ]
        )
        self._tablo.setColumnHidden(C_PID, True)
        self._tablo.verticalHeader().setVisible(False)
        self._tablo.horizontalHeader().setStretchLastSection(True)
        self._tablo.verticalHeader().setDefaultSectionSize(34)
        self._tablo.setItemDelegateForColumn(C_KOSUL, KosulDelegate(self))
        self._tablo.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tablo.customContextMenuRequested.connect(self._kosul_sag_tik_menu)
        self._tablo.itemChanged.connect(self._satir_saat_guncelle)
        root.addWidget(self._tablo, 1)

    def load_data(self):
        self._donem_guncelle()
        self._hesapla()

    def _get_donem_aralik(self) -> tuple[date, date]:
        """Dönem başlangıcı (15) ve bitişi (sonraki ay 14)."""
        try:
            yil = int(self._yil.currentData())
            ay_idx = self._ay.currentIndex() + 1
            return self._svc.donem_tarih_araligi(yil, ay_idx)
        except Exception:
            return None, None

    def _donem_guncelle(self) -> None:
        """Dönem tarih aralığını ve gün sayısını güncelleyin."""
        donem_bas, donem_bit = self._get_donem_aralik()
        if donem_bas and donem_bit:
            bas_str = donem_bas.strftime("%d.%m.%Y")
            bit_str = donem_bit.strftime("%d.%m.%Y")
            self._lbl_donem.setText(f"Dönem: {bas_str} — {bit_str}")
            gun_sayisi = (donem_bit - donem_bas).days + 1
            is_gun = sum(
                1
                for i in range(gun_sayisi)
                if (donem_bas + timedelta(days=i)).weekday() < 5
            )
            self._lbl_aylik_gun.setText(f"Aylik Gun: {is_gun}")
        else:
            self._lbl_donem.setText("Dönem: —")
            self._lbl_aylik_gun.setText("Aylik Gun: 0")

    def _hesapla(self) -> None:
        self._alert.temizle()
        try:
            rows = self._svc.donem_hesapla(self._secili_yil(), self._secili_ay())
            self._tablo.blockSignals(True)
            self._tablo.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self._set_item(i, C_PID, r.get("personel_id"), editable=False)
                self._set_item(i, C_TC, r.get("tc_kimlik"), editable=False)
                self._set_item(i, C_AD, r.get("ad_soyad"), editable=False)
                self._set_item(i, C_BIRIM, r.get("gorev_yeri"), editable=False)
                self._set_item(i, C_KOSUL, r.get("calisma_kosulu") or "B", editable=False)
                self._set_item(i, C_GUN, self._fmt_gun(r.get("aylik_gun")), editable=True)

                izin_gun = self._to_float(self._fmt_gun(r.get("izin_gun")))
                kosul_text = str(r.get("calisma_kosulu") or "B").strip().upper()
                kosul = kosul_text if kosul_text in ("A", "B") else "B"
                aylik_gun = self._to_float(self._fmt_gun(r.get("aylik_gun")))
                fiili_saat = self._svc.fiili_saat_hesapla(aylik_gun, izin_gun, kosul)

                self._set_item(i, C_IZIN, self._fmt_gun(izin_gun), editable=True)
                self._set_item(i, C_SAAT, f"{fiili_saat:.1f}", editable=False)
                self._set_item(i, C_NOT, r.get("notlar") or "", editable=True)
            self._tablo.blockSignals(False)
            self._alert.goster(f"{len(rows)} satir hazirlandi.", "success")
        except Exception as exc:
            exc_logla("FhszYonetimPage._hesapla", exc)
            self._alert.goster(str(exc), "danger")

    def _kaydet(self) -> None:
        self._alert.temizle()
        try:
            satirlar: list[dict] = []
            for i in range(self._tablo.rowCount()):
                pid = self._text(i, C_PID)
                if not pid:
                    continue
                kosul_text = self._text(i, C_KOSUL).upper()
                kosul_char = kosul_text.split()[-1] if kosul_text else "B"
                satirlar.append(
                    {
                        "personel_id": pid,
                        "calisma_kosulu": kosul_char if kosul_char in ("A", "B") else "B",
                        "aylik_gun": self._to_float(self._text(i, C_GUN)),
                        "izin_gun": self._to_float(self._text(i, C_IZIN)),
                        "notlar": self._text(i, C_NOT),
                    }
                )
            adet = self._svc.donem_kaydet(self._secili_yil(), self._secili_ay(), satirlar)
            self._alert.goster(f"FHSZ kaydedildi. Satir: {adet}", "success")
            self._hesapla()
        except Exception as exc:
            exc_logla("FhszYonetimPage._kaydet", exc)
            self._alert.goster(str(exc), "danger")

    def _satir_saat_guncelle(self, item: QTableWidgetItem) -> None:
        if item.column() not in (C_KOSUL, C_GUN, C_IZIN):
            return
        row = item.row()
        kosul_text = self._text(row, C_KOSUL).upper()
        kosul = kosul_text.split()[-1] if kosul_text else "B"
        kosul = kosul if kosul in ("A", "B") else "B"
        gun = self._to_float(self._text(row, C_GUN))
        izin = self._to_float(self._text(row, C_IZIN))
        saat = self._svc.fiili_saat_hesapla(gun, izin, kosul)

        self._tablo.blockSignals(True)
        self._set_item(row, C_SAAT, f"{saat:.1f}", editable=False)
        self._tablo.blockSignals(False)

    def _kosul_sag_tik_menu(self, pos) -> None:
        idx = self._tablo.indexAt(pos)
        if not idx.isValid() or idx.column() != C_KOSUL:
            return

        menu = QMenu(self)
        act_a = menu.addAction("Koşul A")
        act_b = menu.addAction("Koşul B")
        secilen = menu.exec(self._tablo.viewport().mapToGlobal(pos))
        if secilen not in (act_a, act_b):
            return

        yeni_kosul = "A" if secilen == act_a else "B"
        row = idx.row()
        self._tablo.blockSignals(True)
        self._set_item(row, C_KOSUL, yeni_kosul, editable=False)
        self._tablo.blockSignals(False)
        self._satir_saat_guncelle(self._tablo.item(row, C_KOSUL))

    def _set_item(self, row: int, col: int, value, editable: bool) -> None:
        # C_KOSUL için "Koşul A" / "Koşul B" formatı
        if col == C_KOSUL:
            kosul_char = str(value if value is not None else "B").upper()[0]
            display_val = f"Koşul {kosul_char}" if kosul_char in ("A", "B") else "Koşul B"
        else:
            display_val = str(value if value is not None else "")
        
        item = QTableWidgetItem(display_val)
        flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        if editable:
            flags |= Qt.ItemFlag.ItemIsEditable
        item.setFlags(flags)
        if col in (C_GUN, C_IZIN, C_SAAT):
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self._tablo.setItem(row, col, item)

    def _text(self, row: int, col: int) -> str:
        item = self._tablo.item(row, col)
        return str(item.text()).strip() if item else ""

    @staticmethod
    def _to_float(text: str) -> float:
        try:
            return max(0.0, float(str(text).replace(",", ".")))
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _fmt_gun(value) -> str:
        try:
            val = float(value)
        except (TypeError, ValueError):
            return "0"
        if abs(val - round(val)) < 1e-9:
            return str(int(round(val)))
        return f"{val:.1f}"

    def _secili_yil(self) -> int:
        return int(self._yil.currentData())

    def _secili_ay(self) -> int:
        return int(self._ay.currentData())
