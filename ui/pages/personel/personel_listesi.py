# -*- coding: utf-8 -*-
"""Personel listesi sayfasi.

UI -> Service katmani kuraliyla calisir.
"""
from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPoint,
    QRect,
    QSize,
    QSortFilterProxyModel,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtGui import QColor, QCursor, QFont, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QProgressBar,
    QPushButton,
    QStyledItemDelegate,
    QStyle,
    QTableView,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from app.exceptions import AppHatasi
from app.logger import exc_logla, logger
from app.services.personel_service import PersonelService
from app.text_utils import turkish_lower, turkish_title_case
from ui.components.alerts import AlertBar
from ui.components.async_runner import AsyncRunner
from ui.components.buttons import GhostButton, PrimaryButton
from ui.pages.personel.personel_detay import PersonelDetayPage
from ui.pages.personel.personel_ekle import PersonelEklePage
from ui.styles import T
from ui.styles.icons import ic


COLUMNS = [
    ("_avatar", "", 56),
    ("ad_soyad", "Ad Soyad", 180),
    ("_tc_sicil", "TC / Sicil", 160),
    ("_birim", "Birim · Unvan", 240),
    ("telefon", "Telefon", 140),
    ("durum", "Durum", 220),
]


def _durum_ui(durum: str) -> str:
    d = turkish_lower((durum or "").strip())
    if d == "aktif":
        return "Aktif"
    if d == "pasif" or d == "ayrildi":
        return "Pasif"
    return "Bilinmiyor"


class _PersonelTableModel(QAbstractTableModel):
    RAW_ROW_ROLE = Qt.ItemDataRole.UserRole + 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: list[dict] = []

    def set_rows(self, rows: list[dict]) -> None:
        self.beginResetModel()
        self._rows = rows or []
        self.endResetModel()

    def get_row(self, idx: int) -> dict | None:
        if 0 <= idx < len(self._rows):
            return self._rows[idx]
        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        return len(COLUMNS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return COLUMNS[section][1]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row = self._rows[index.row()]
        key = COLUMNS[index.column()][0]

        if role == self.RAW_ROW_ROLE:
            return row

        if role == Qt.ItemDataRole.DisplayRole:
            if key == "_avatar":
                return ""
            if key == "ad_soyad":
                return row.get("AdSoyad", "")
            if key == "_tc_sicil":
                return row.get("KimlikNo", "")
            if key == "_birim":
                return row.get("GorevYeri", "")
            if key == "telefon":
                return row.get("CepTelefonu", "") or "-"
            if key == "durum":
                return row.get("Durum", "")
            return str(row.get(key, ""))

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if key in ("durum", "_avatar"):
                return Qt.AlignmentFlag.AlignCenter
            return Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft

        return None


class _PersonelDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._hover_row = -1

    def set_hover_row(self, row: int) -> None:
        self._hover_row = row

    def paint(self, painter: QPainter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        row_idx = index.row()
        col_idx = index.column()
        key = COLUMNS[col_idx][0]
        rect = option.rect

        is_sel = bool(option.state & QStyle.StateFlag.State_Selected)
        if is_sel:
            c = QColor(T.accent)
            c.setAlpha(56)
            painter.fillRect(rect, c)
        elif row_idx == self._hover_row:
            c = QColor(T.text)
            c.setAlpha(12)
            painter.fillRect(rect, c)

        row = index.model().data(index, _PersonelTableModel.RAW_ROW_ROLE)
        if not row:
            painter.restore()
            return

        if key == "_avatar":
            self._draw_avatar(painter, rect, row)
        elif key == "ad_soyad":
            self._draw_primary(painter, rect, row.get("AdSoyad", ""))
        elif key == "_tc_sicil":
            self._draw_two_line(
                painter,
                rect,
                row.get("KimlikNo", ""),
                row.get("KurumSicilNo", ""),
                mono_top=True,
            )
        elif key == "_birim":
            self._draw_two_line(
                painter,
                rect,
                row.get("GorevYeri", "-") or "-",
                row.get("KadroUnvani", "") or "",
            )
        elif key == "telefon":
            self._draw_mono(painter, rect, row.get("CepTelefonu", "-") or "-")
        elif key == "durum":
            self._draw_status(painter, rect, row)

        painter.restore()

    def _draw_avatar(self, painter: QPainter, rect: QRect, row: dict) -> None:
        ad = str(row.get("AdSoyad", "")).strip()
        initials = "".join(w[:1] for w in ad.split()[:2]).upper() or "?"
        cx, cy, r = rect.center().x(), rect.center().y(), 12
        hue = (sum(ord(c) for c in ad) * 29) % 360
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor.fromHsl(hue, 120, 90))
        painter.drawEllipse(QPoint(cx, cy), r, r)
        painter.setPen(QColor(T.text))
        painter.setFont(QFont("", 8, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, initials)

    def _draw_primary(self, painter: QPainter, rect: QRect, text: str) -> None:
        painter.setPen(QColor(T.text))
        painter.setFont(QFont("", 9, QFont.Weight.Medium))
        draw_rect = QRect(rect.x() + 8, rect.y(), rect.width() - 16, rect.height())
        show = painter.fontMetrics().elidedText(
            text,
            Qt.TextElideMode.ElideRight,
            draw_rect.width(),
        )
        painter.drawText(
            draw_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            show,
        )

    def _draw_two_line(
        self,
        painter: QPainter,
        rect: QRect,
        top: str,
        bottom: str,
        mono_top: bool = False,
    ) -> None:
        pad = 8
        top_rect = QRect(rect.x() + pad, rect.y() + 4, rect.width() - pad * 2, 16)
        bot_rect = QRect(rect.x() + pad, rect.y() + 20, rect.width() - pad * 2, 14)

        painter.setFont(QFont("Consolas", 8) if mono_top else QFont("", 9, QFont.Weight.Medium))
        painter.setPen(QColor(T.text2))
        painter.drawText(
            top_rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            painter.fontMetrics().elidedText(top, Qt.TextElideMode.ElideRight, top_rect.width()),
        )

        painter.setFont(QFont("", 8))
        painter.setPen(QColor(T.text3))
        painter.drawText(
            bot_rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            painter.fontMetrics().elidedText(bottom, Qt.TextElideMode.ElideRight, bot_rect.width()),
        )

    def _draw_mono(self, painter: QPainter, rect: QRect, text: str) -> None:
        painter.setFont(QFont("Consolas", 8))
        painter.setPen(QColor(T.text3))
        draw_rect = QRect(rect.x() + 8, rect.y(), rect.width() - 16, rect.height())
        painter.drawText(
            draw_rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            text,
        )

    def _draw_status(self, painter: QPainter, rect: QRect, row: dict) -> None:
        durum = str(row.get("Durum", "")).strip()
        if durum == "Aktif":
            fg = QColor(T.green2)
        elif durum == "Pasif":
            fg = QColor(T.red)
        else:
            fg = QColor(T.text2)

        bg = QColor(fg)
        bg.setAlpha(42)

        font = QFont("", 8, QFont.Weight.Medium)
        painter.setFont(font)
        fm = QFontMetrics(font)

        max_width = max(60, rect.width() - 12)
        text = fm.elidedText(durum, Qt.TextElideMode.ElideRight, max_width - 20)
        pill_w = min(max_width, fm.horizontalAdvance(text) + 20)
        pill_h = fm.height() + 8
        px = rect.x() + 6
        py = rect.center().y() - pill_h // 2

        painter.setBrush(bg)
        painter.setPen(QPen(fg, 1))
        painter.drawRoundedRect(px, py, pill_w, pill_h, 4, 4)
        painter.setPen(fg)
        painter.drawText(
            QRect(px + 8, py, pill_w - 12, pill_h),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            text,
        )


class PersonelListesi(QWidget):
    """Personel listesi sayfasi."""

    secildi = Signal(str)
    yeni_istendi = Signal()
    detay_requested = Signal(dict)

    def __init__(self, db, oturum: dict | None = None, parent=None):
        super().__init__(parent)
        self._db = db
        self._oturum = oturum
        self._svc = PersonelService(db)
        self._mdi_windows: list[QDialog] = []
        self._all_data: list[dict] = []
        self._active_filter = "Aktif"
        self._filter_btns: dict[str, QPushButton] = {}
        self._last_search_text = ""

        self._search_timer = QTimer(self)
        self._search_timer.setInterval(250)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._execute_search)

        self._setup_ui()
        self._connect_signals()
        self.load_data()

    def _setup_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        self._alert = AlertBar(self)
        main.addWidget(self._alert)
        main.addWidget(self._build_toolbar())
        main.addWidget(self._build_subtoolbar())
        main.addWidget(self._build_table(), 1)
        main.addWidget(self._build_footer())

    def _build_toolbar(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"QFrame{{background:{T.bg1};border-bottom:1px solid {T.border};}}")
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(16, 8, 16, 8)
        lay.setSpacing(8)

        title = QLabel("Personel Listesi")
        title.setStyleSheet(f"color:{T.text};font-size:16px;font-weight:700;")
        lay.addWidget(title)
        lay.addWidget(self._sep())

        for lbl in ("Aktif", "Pasif", "Tumu"):
            btn = QPushButton(lbl)
            btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFixedHeight(28)
            btn.setMinimumWidth(90)
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background:{T.overlay_low};
                    color:{T.text2};
                    border:1px solid {T.border2};
                    border-radius:6px;
                    padding:4px 12px;
                    font-size:11px;
                    font-weight:500;
                }}
                QPushButton:hover {{
                    background:{T.overlay_mid};
                    color:{T.text};
                }}
                QPushButton:checked {{
                    background:{T.accent_bg};
                    color:{T.text};
                    border:1px solid {T.accent};
                    font-weight:600;
                }}
                """
            )
            if lbl == self._active_filter:
                btn.setChecked(True)
            self._filter_btns[lbl] = btn
            lay.addWidget(btn)

        lay.addWidget(self._sep())

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ad, TC, birim ara...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedWidth(260)
        lay.addWidget(self.search_input)

        lay.addStretch()

        self.btn_yenile = GhostButton("", ikon="yenile")
        self.btn_yenile.setIcon(ic("yenile", size=16, color=T.text2))
        self.btn_yenile.setIconSize(QSize(16, 16))
        self.btn_yenile.setFixedSize(32, 28)
        self.btn_yenile.setToolTip("Yenile")
        self.btn_yenile.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        lay.addWidget(self.btn_yenile)

        self.btn_yeni = PrimaryButton(" Yeni Personel", ikon="user_add")
        self.btn_yeni.setIcon(ic("user_add", size=16, color=T.text))
        self.btn_yeni.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_yeni.setFixedHeight(30)
        lay.addWidget(self.btn_yeni)

        return frame

    def _build_subtoolbar(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"QFrame{{background:{T.bg0};border-bottom:1px solid {T.border};}}")
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(16, 8, 16, 8)
        lay.setSpacing(8)

        lbl = QLabel("FILTRE:")
        lbl.setStyleSheet(f"color:{T.text3};font-size:12px;")
        lay.addWidget(lbl)

        self.cmb_gorev_yeri = QComboBox()
        self.cmb_gorev_yeri.addItem("Tum Birimler")
        self.cmb_gorev_yeri.setFixedWidth(250)
        lay.addWidget(self.cmb_gorev_yeri)

        self.cmb_hizmet = QComboBox()
        self.cmb_hizmet.addItem("Tum Siniflar")
        self.cmb_hizmet.setFixedWidth(280)
        lay.addWidget(self.cmb_hizmet)

        lay.addStretch()

        self.btn_excel = GhostButton(" Excel", ikon="download")
        self.btn_excel.setIcon(ic("download", size=16, color=T.text2))
        self.btn_excel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        lay.addWidget(self.btn_excel)
        return frame

    def _build_table(self) -> QTableView:
        self._model = _PersonelTableModel(self)
        self._proxy = QSortFilterProxyModel(self)
        self._proxy.setSourceModel(self._model)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setFilterKeyColumn(-1)

        self.table = QTableView()
        self.table.setModel(self._proxy)
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setShowGrid(False)
        self.table.setMouseTracking(True)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self._delegate = _PersonelDelegate(self.table)
        self.table.setItemDelegate(self._delegate)

        for i, (_, _, w) in enumerate(COLUMNS):
            self.table.setColumnWidth(i, w)
        hdr = self.table.horizontalHeader()
        hdr.setStretchLastSection(False)
        hdr.setSectionResizeMode(1, hdr.ResizeMode.Stretch)
        hdr.setSectionResizeMode(3, hdr.ResizeMode.Stretch)

        return self.table

    def _build_footer(self) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet(f"QFrame{{background:{T.bg1};border-top:1px solid {T.border};}}")
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(16, 6, 16, 6)
        lay.setSpacing(16)

        self.lbl_info = QLabel("0 kayit")
        self.lbl_info.setStyleSheet(f"color:{T.text2};font-size:11px;")
        lay.addWidget(self.lbl_info)

        self.lbl_detail = QLabel("")
        self.lbl_detail.setStyleSheet(f"color:{T.text3};font-size:11px;")
        lay.addWidget(self.lbl_detail)

        lay.addStretch()

        self.progress = QProgressBar()
        self.progress.setFixedSize(120, 4)
        self.progress.setVisible(False)
        self.progress.setTextVisible(False)
        lay.addWidget(self.progress)

        return frame

    def _connect_signals(self) -> None:
        for text, btn in self._filter_btns.items():
            btn.clicked.connect(lambda _, t=text: self._on_filter_click(t))

        self.search_input.textChanged.connect(self._on_search)
        self.cmb_gorev_yeri.currentTextChanged.connect(lambda _: self._apply_filters())
        self.cmb_hizmet.currentTextChanged.connect(lambda _: self._apply_filters())
        self.btn_yenile.clicked.connect(self.load_data)
        self.btn_yeni.clicked.connect(self.yeni_istendi.emit)
        self.yeni_istendi.connect(self._open_ekle_dialog)
        self.btn_excel.clicked.connect(self._export_excel)

        self.table.doubleClicked.connect(self._on_double_click)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        self.table.mouseMoveEvent = self._tbl_mouse_move

    def load_data(self) -> None:
        self.progress.setVisible(True)

        def _fetch() -> list[dict]:
            return self._svc.listele(aktif_only=False)

        def _done(rows: list[dict]) -> None:
            self._all_data = [self._to_view_row(r) for r in (rows or [])]
            self._populate_combos()
            self._apply_filters()
            self._update_pill_counts()
            self._alert.temizle()
            self.progress.setVisible(False)

        def _err(msg: str) -> None:
            self.progress.setVisible(False)
            self._alert.goster(msg, "danger")

        AsyncRunner(fn=_fetch, on_done=_done, on_error=_err, parent=self).start()

    def _to_view_row(self, row: dict) -> dict:
        ad = str(row.get("ad") or "").strip()
        soyad = str(row.get("soyad") or "").strip()
        ad_soyad = turkish_title_case(f"{ad} {soyad}".strip())
        return {
            "id": str(row.get("id") or "").strip(),
            "AdSoyad": ad_soyad,
            "KimlikNo": str(row.get("tc_kimlik") or "").strip(),
            "KurumSicilNo": str(row.get("sicil_no") or "").strip(),
            "GorevYeri": str(row.get("gorev_yeri_ad") or "-").strip(),
            "KadroUnvani": str(row.get("kadro_unvani") or "").strip(),
            "CepTelefonu": str(row.get("telefon") or "").strip(),
            "Durum": _durum_ui(str(row.get("durum") or "")),
            "HizmetSinifi": str(row.get("hizmet_sinifi") or "").strip(),
        }

    def _populate_combos(self) -> None:
        try:
            gorevler = self._svc.gorev_yeri_adlari() or []
            siniflar = self._svc.hizmet_siniflari() or []
        except Exception as exc:
            exc_logla("PersonelListesi._populate_combos", exc)
            return

        prev_gy = self.cmb_gorev_yeri.currentText()
        prev_hs = self.cmb_hizmet.currentText()

        self.cmb_gorev_yeri.blockSignals(True)
        self.cmb_hizmet.blockSignals(True)

        self.cmb_gorev_yeri.clear()
        self.cmb_gorev_yeri.addItem("Tum Birimler")
        self.cmb_gorev_yeri.addItems(gorevler)

        self.cmb_hizmet.clear()
        self.cmb_hizmet.addItem("Tum Siniflar")
        self.cmb_hizmet.addItems(siniflar)

        idx_gy = self.cmb_gorev_yeri.findText(prev_gy)
        idx_hs = self.cmb_hizmet.findText(prev_hs)
        self.cmb_gorev_yeri.setCurrentIndex(idx_gy if idx_gy >= 0 else 0)
        self.cmb_hizmet.setCurrentIndex(idx_hs if idx_hs >= 0 else 0)

        self.cmb_gorev_yeri.blockSignals(False)
        self.cmb_hizmet.blockSignals(False)

    def _on_filter_click(self, text: str) -> None:
        self._active_filter = text
        for t, btn in self._filter_btns.items():
            btn.setChecked(t == text)
        self._apply_filters()

    def _on_search(self, text: str) -> None:
        self._last_search_text = text
        self._search_timer.stop()
        self._search_timer.start()

    def _execute_search(self) -> None:
        self._proxy.setFilterFixedString(self._last_search_text)
        self._update_count()

    def _apply_filters(self) -> None:
        filtered = self._all_data

        if self._active_filter != "Tumu":
            filtered = [
                r for r in filtered
                if str(r.get("Durum", "")).strip() == self._active_filter
            ]

        birim = self.cmb_gorev_yeri.currentText()
        if birim and birim != "Tum Birimler":
            filtered = [
                r for r in filtered
                if str(r.get("GorevYeri", "")).strip() == birim
            ]

        sinif = self.cmb_hizmet.currentText()
        if sinif and sinif != "Tum Siniflar":
            filtered = [
                r for r in filtered
                if str(r.get("HizmetSinifi", "")).strip() == sinif
            ]

        self._model.set_rows(filtered)
        self._proxy.setFilterFixedString(self._last_search_text)
        self._update_count()
        self._update_pill_counts()

    def _update_count(self) -> None:
        self.lbl_info.setText(f"Gosterilen {self._proxy.rowCount()} / {len(self._all_data)}")

    def _update_pill_counts(self) -> None:
        aktif = sum(1 for r in self._all_data if r.get("Durum") == "Aktif")
        pasif = sum(1 for r in self._all_data if r.get("Durum") == "Pasif")
        tumu = len(self._all_data)

        self.lbl_detail.setText(f"Aktif {aktif}  ·  Pasif {pasif}")

        counts = {"Aktif": aktif, "Pasif": pasif, "Tumu": tumu}
        for t, btn in self._filter_btns.items():
            btn.setText(f"{t} ({counts.get(t, 0)})")

    def _tbl_mouse_move(self, event) -> None:
        idx = self.table.indexAt(event.pos())
        src_row = self._proxy.mapToSource(idx).row() if idx.isValid() else -1
        self._delegate.set_hover_row(src_row)
        self.table.viewport().update()
        self._show_tooltip(idx, event.globalPos())
        QTableView.mouseMoveEvent(self.table, event)

    def _show_tooltip(self, idx, global_pos) -> None:
        if not idx.isValid():
            QToolTip.hideText()
            return

        src = self._proxy.mapToSource(idx)
        row = self._model.get_row(src.row())
        if not row:
            return

        tc = row.get("KimlikNo", "")
        ad = row.get("AdSoyad", "")
        gorev = row.get("GorevYeri", "")
        text = f"{ad}\nTC: {tc}\nBirim: {gorev}"
        QToolTip.showText(global_pos, text, self.table)

    def _on_double_click(self, index) -> None:
        src = self._proxy.mapToSource(index)
        row = self._model.get_row(src.row())
        if not row:
            return
        pid = str(row.get("id") or "").strip()
        if pid:
            self.secildi.emit(pid)
        self._open_detay_dialog(row)

    def get_selected(self) -> dict | None:
        idxs = self.table.selectionModel().selectedRows()
        if not idxs:
            return None
        src_row = self._proxy.mapToSource(idxs[0]).row()
        return self._model.get_row(src_row)

    def yenile(self) -> None:
        self.load_data()

    def sec(self, personel_id: str) -> None:
        pid = str(personel_id or "").strip()
        if not pid:
            return
        for row_no in range(self._model.rowCount()):
            row = self._model.get_row(row_no)
            if row and str(row.get("id") or "") == pid:
                idx = self._model.index(row_no, 0)
                proxy_idx = self._proxy.mapFromSource(idx)
                self.table.selectRow(proxy_idx.row())
                self.table.scrollTo(proxy_idx, QTableView.ScrollHint.PositionAtCenter)
                return

    def _show_context_menu(self, pos) -> None:
        idx = self.table.indexAt(pos)
        if not idx.isValid():
            return

        row = self._model.get_row(self._proxy.mapToSource(idx).row())
        if not row:
            return

        menu = QMenu(self)
        menu.addAction("Detay Goruntule").triggered.connect(lambda: self._open_detay_dialog(row))

        durum = str(row.get("Durum") or "")
        pid = str(row.get("id") or "")
        ad = str(row.get("AdSoyad") or "")

        menu.addSeparator()
        if durum != "Aktif":
            menu.addAction("Aktif Yap").triggered.connect(
                lambda: self._change_durum(pid, ad, "aktif")
            )
        if durum != "Pasif":
            menu.addAction("Pasif Yap").triggered.connect(
                lambda: self._change_durum(pid, ad, "pasif")
            )

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _open_ekle_dialog(self) -> None:
        self._open_mdi_form("Personel Ekle", None)

    def _open_detay_dialog(self, row: dict) -> None:
        personel_id = str((row or {}).get("id") or "").strip()
        if not personel_id:
            self._alert.goster("Detayi gosterilecek personel secilemedi.", "warning")
            return

        try:
            src = self._svc.getir(personel_id)
        except Exception as exc:
            exc_logla("PersonelListesi._open_detay_dialog", exc)
            self._alert.goster(str(exc), "danger")
            return

        self._open_mdi_form("Personel Detay", src)

    def _open_mdi_form(self, title: str, edit_data: dict | None) -> None:
        key_suffix = "ekle" if edit_data is None else str((edit_data or {}).get("id") or "duzenle")
        mdi_key = f"personel_form_{key_suffix}"
        is_edit = edit_data is not None
        app_win = self.window()
        if app_win is not None and hasattr(app_win, "open_mdi_child"):
            form_host = QWidget()
            lay = QVBoxLayout(form_host)
            lay.setContentsMargins(8, 8, 8, 8)
            lay.setSpacing(6)
            if is_edit:
                form = PersonelDetayPage(
                    db=self._db,
                    edit_data=edit_data or {},
                    on_saved=self.load_data,
                    oturum=self._oturum,
                    parent=form_host,
                )
            else:
                form = PersonelEklePage(
                    db=self._db,
                    edit_data=None,
                    on_saved=self.load_data,
                    oturum=self._oturum,
                    parent=form_host,
                )
            form.form_closed.connect(lambda: self._close_mdi_child(mdi_key))
            lay.addWidget(form)
            app_win.open_mdi_child(mdi_key, form_host, title)
            return

        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.resize(980, 700)
        dlg.setModal(False)
        dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(6)

        if is_edit:
            form = PersonelDetayPage(
                db=self._db,
                edit_data=edit_data or {},
                on_saved=self.load_data,
                oturum=self._oturum,
                parent=dlg,
            )
        else:
            form = PersonelEklePage(
                db=self._db,
                edit_data=None,
                on_saved=self.load_data,
                oturum=self._oturum,
                parent=dlg,
            )
        form.form_closed.connect(dlg.close)
        lay.addWidget(form)

        self._mdi_windows.append(dlg)
        dlg.destroyed.connect(lambda *_: self._cleanup_mdi_windows())
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()

    def _cleanup_mdi_windows(self) -> None:
        self._mdi_windows = [w for w in self._mdi_windows if w and not w.isHidden()]

    def _close_mdi_child(self, key: str) -> None:
        app_win = self.window()
        if app_win is None or not hasattr(app_win, "close_mdi_child"):
            return
        try:
            app_win.close_mdi_child(key)
        except Exception:
            return

    def _change_durum(self, personel_id: str, ad_soyad: str, yeni_durum: str) -> None:
        if not personel_id:
            self._alert.goster("Personel kimligi bulunamadi.", "warning")
            return

        def _run() -> str:
            self._svc.guncelle(personel_id, {"durum": yeni_durum})
            return yeni_durum

        def _done(durum: str) -> None:
            logger.info("Personel durum guncellendi: %s -> %s", personel_id, durum)
            self._alert.goster(f"{ad_soyad} durumu guncellendi.", "success")
            self.load_data()

        def _err(msg: str) -> None:
            self._alert.goster(msg, "danger")

        AsyncRunner(fn=_run, on_done=_done, on_error=_err, parent=self).start()

    def _export_excel(self) -> None:
        rows = [self._model.get_row(i) for i in range(self._model.rowCount())]
        export_rows = [r for r in rows if r]
        if not export_rows:
            self._alert.goster("Disa aktarilacak veri yok.", "warning")
            return

        try:
            import importlib
            from PySide6.QtWidgets import QFileDialog

            openpyxl = importlib.import_module("openpyxl")
            styles = importlib.import_module("openpyxl.styles")
            Workbook = openpyxl.Workbook
            Alignment = styles.Alignment
            Border = styles.Border
            Font = styles.Font
            PatternFill = styles.PatternFill
            Side = styles.Side
        except Exception as exc:
            exc_logla("PersonelListesi._export_excel.import", exc)
            self._alert.goster("Excel aktarimi icin openpyxl gerekli.", "warning")
            return

        ts = datetime.now().strftime("%Y%m%d_%H%M")
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Excel Dosyasini Kaydet",
            f"Personel_Listesi_{ts}.xlsx",
            "Excel Files (*.xlsx)",
        )
        if not file_path:
            return

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Personel"

            headers = [
                "Ad Soyad",
                "TC Kimlik No",
                "Sicil No",
                "Birim",
                "Unvan",
                "Telefon",
                "Durum",
            ]

            fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            hfont = Font(bold=True, color="FFFFFF", size=11)
            align = Alignment(horizontal="left", vertical="center")
            border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )

            for i, h in enumerate(headers, start=1):
                cell = ws.cell(row=1, column=i, value=h)
                cell.fill = fill
                cell.font = hfont
                cell.alignment = align
                cell.border = border

            for r_idx, row in enumerate(export_rows, start=2):
                vals = [
                    row.get("AdSoyad", ""),
                    row.get("KimlikNo", ""),
                    row.get("KurumSicilNo", ""),
                    row.get("GorevYeri", ""),
                    row.get("KadroUnvani", ""),
                    row.get("CepTelefonu", ""),
                    row.get("Durum", ""),
                ]
                for c_idx, val in enumerate(vals, start=1):
                    cell = ws.cell(row=r_idx, column=c_idx, value=str(val or ""))
                    cell.alignment = align
                    cell.border = border

            ws.column_dimensions["A"].width = 22
            ws.column_dimensions["B"].width = 16
            ws.column_dimensions["C"].width = 16
            ws.column_dimensions["D"].width = 22
            ws.column_dimensions["E"].width = 24
            ws.column_dimensions["F"].width = 16
            ws.column_dimensions["G"].width = 12
            ws.freeze_panes = "A2"

            wb.save(file_path)
            self._alert.goster(f"Excel dosyasi kaydedildi: {file_path}", "success")

        except AppHatasi as exc:
            self._alert.goster(str(exc), "danger")
        except Exception as exc:
            exc_logla("PersonelListesi._export_excel", exc)
            self._alert.goster("Excel dosyasi olusturulamadi.", "danger")

    @staticmethod
    def _sep() -> QFrame:
        sep = QFrame()
        sep.setFixedSize(1, 20)
        sep.setStyleSheet(f"background:{T.border};")
        return sep
