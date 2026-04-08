# -*- coding: utf-8 -*-
"""
ui/pages/demo/theme_demo_form.py ï¿½?" Tema Demo Formu
ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

Yeni tema sisteminin interaktif demo'su. TÃ¼m widget'ler,
renk token'larÄ± ve icon'larÄ± gÃ¶rselleï¿½Ytirir.

KullanÄ±m (standalone):
    python -m ui.pages.demo.theme_demo_form

KullanÄ±m (app iÃ§inde):
    from ui.pages.demo.theme_demo_form import DemoWindow
    window = DemoWindow()
    window.show()
"""

from __future__ import annotations
from pathlib import Path
import sys

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QDateEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QTextEdit, QCheckBox, QRadioButton, QPushButton,
    QGroupBox, QScrollArea, QFrame, QFormLayout, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QFont

try:
    from ui.styles import DARK, LIGHT, ThemeManager, ic
except ModuleNotFoundError:
    # Dosya doï¿½Yrudan Ã§alÄ±ï¿½YtÄ±rÄ±ldÄ±ï¿½YÄ±nda proje kÃ¶kÃ¼nÃ¼ path'e ekle.
    project_root = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from ui.styles import DARK, LIGHT, ThemeManager, ic


# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½
#  Demo Form Widget'larÄ±
# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

class ColorPaletteWidget(QWidget):
    """Renk paletini gÃ¶steren widget."""

    def __init__(self, tokens: dict[str, str]):
        super().__init__()
        self.tokens = tokens
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Zemin renkleri
        main_layout.addWidget(QLabel("gYï¿½ï¿½ <b>Zemin KatmanlarÄ±</b>"))
        for key in ["BG_PRIMARY", "BG_SECONDARY", "BG_TERTIARY", "BG_ELEVATED"]:
            color = self.tokens.get(key, "#000000")
            main_layout.addLayout(self._create_color_row(key, color))
        
        # Metin renkleri
        main_layout.addWidget(QLabel(""))
        main_layout.addWidget(QLabel("gY"ï¿½ <b>Metin</b>"))
        for key in ["TEXT_PRIMARY", "TEXT_SECONDARY", "TEXT_MUTED"]:
            color = self.tokens.get(key, "#000000")
            main_layout.addLayout(self._create_color_row(key, color))
        
        # Vurgu renkleri
        main_layout.addWidget(QLabel(""))
        main_layout.addWidget(QLabel("gY'ï¿½ <b>Vurgu</b>"))
        for key in ["ACCENT", "ACCENT2"]:
            color = self.tokens.get(key, "#000000")
            main_layout.addLayout(self._create_color_row(key, color))
        
        # Durum renkleri
        main_layout.addWidget(QLabel(""))
        main_layout.addWidget(QLabel("ï¿½sï¿½ <b>Durum</b>"))
        for key in ["STATUS_SUCCESS", "STATUS_WARNING", "STATUS_ERROR"]:
            color = self.tokens.get(key, "#000000")
            main_layout.addLayout(self._create_color_row(key, color))
        
        main_layout.addStretch()

    def _create_color_row(self, name: str, color: str) -> QHBoxLayout:
        """Renk satÄ±rÄ± layout'u oluï¿½Ytur."""
        color_box = QFrame()
        color_box.setStyleSheet(f"background-color: {color}; border: 1px solid #333;")
        color_box.setMinimumHeight(30)
        color_box.setMaximumHeight(30)
        color_box.setMinimumWidth(50)
        color_box.setMaximumWidth(50)
        
        label = QLabel(f"{name}: {color}")
        label.setFont(QFont("Monospace", 9))
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(color_box)
        layout.addWidget(label)
        return layout


class IconShowcaseWidget(QWidget):
    """Icon'larÄ± gÃ¶steren widget."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("gYï¿½ï¿½ Icon Vitrin")
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Icon grid layout
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(15)

        icons_list = [
            "users", "user_add", "bell", "search", "menu",
            "check", "x", "calendar", "lock", "eye",
            "mail", "phone", "trash2", "edit", "download"
        ]

        for icon_name in icons_list:
            # Icon + label
            widget = QWidget()
            w_layout = QVBoxLayout(widget)
            w_layout.setContentsMargins(0, 0, 0, 0)
            w_layout.setSpacing(5)
            w_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Icon button
            btn = QPushButton()
            btn.setIcon(ic(icon_name, size=24, color="accent"))
            btn.setIconSize(QSize(32, 32))
            btn.setFixedSize(50, 50)
            btn.setFlat(True)
            btn.setToolTip(icon_name)

            # Label
            lbl = QLabel(icon_name)
            lbl.setFont(QFont("Arial", 8))
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            w_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
            w_layout.addWidget(lbl)

            grid_layout.addWidget(widget)

        layout.addLayout(grid_layout)
        layout.addStretch()


# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½
#  Ana Demo Form
# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

class DemoWindow(QMainWindow):
    """Tema demo penceresi."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RADPYS v2 ï¿½?" Tema Demo")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()
        self.apply_dark_theme()

    def init_ui(self):
        """ArayÃ¼zÃ¼ oluï¿½Ytur."""
        # Ana widget
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Baï¿½YlÄ±k + Tema butonlarÄ±
        header_layout = QHBoxLayout()

        title = QLabel("gYï¿½ï¿½ RADPYS v2 Tema Sistemi Demo")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        dark_btn = QPushButton("gYOT Koyu Tema")
        dark_btn.clicked.connect(self.apply_dark_theme)
        header_layout.addWidget(dark_btn)

        light_btn = QPushButton("ï¿½~?ï¸ AÃ§Ä±k Tema")
        light_btn.clicked.connect(self.apply_light_theme)
        header_layout.addWidget(light_btn)

        main_layout.addLayout(header_layout)

        # Tab widget
        tabs = QTabWidget()

        # Tab 1: Form ï¿½-rneï¿½Yi
        form_tab = self.create_form_tab()
        tabs.addTab(form_tab, "gY"ï¿½ Form ï¿½-rneï¿½Yi")

        # Tab 2: Renk Paleti
        self.palette_tab = QWidget()
        self.palette_layout = QVBoxLayout(self.palette_tab)
        tabs.addTab(self.palette_tab, "gYï¿½ï¿½ Renk Paleti")

        # Tab 3: Icon'lar
        icons_scroll = QScrollArea()
        icons_scroll.setWidget(IconShowcaseWidget())
        icons_scroll.setWidgetResizable(True)
        tabs.addTab(icons_scroll, "gYï¿½ï¿½ Icon Vitrin")

        # Tab 4: Widget ï¿½-rnekleri
        widgets_tab = self.create_widgets_tab()
        tabs.addTab(widgets_tab, "gYï¿½ï¿½ Widget'ler")

        main_layout.addWidget(tabs)

        # Palette'i gÃ¼ncelle (ilk sefer)
        self.update_palette_tab()

    def create_form_tab(self) -> QWidget:
        """Form Ã¶rneï¿½Yi tab'Ä± oluï¿½Ytur."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        # Form container
        form_container = QWidget()
        form_layout = QFormLayout(form_container)
        form_layout.setSpacing(10)

        # Form alanlarÄ±
        form_layout.addRow("Ad:", QLineEdit())
        form_layout.addRow("Soyad:", QLineEdit())

        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Doï¿½Yum Tarihi:", date_edit)

        combo = QComboBox()
        combo.addItems(["SeÃ§iniz...", "Python", "JavaScript", "TypeScript", "Rust"])
        form_layout.addRow("Programlama Dili:", combo)

        spin = QSpinBox()
        spin.setRange(0, 100)
        form_layout.addRow("Seviye (0-100):", spin)

        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Notlar...")
        text_edit.setMinimumHeight(80)
        form_layout.addRow("Notlar:", text_edit)

        # Checkbox grup
        group_box = QGroupBox("Tercihler")
        group_layout = QVBoxLayout(group_box)
        group_layout.addWidget(QCheckBox("E-posta bildirimleri"))
        group_layout.addWidget(QCheckBox("SMS bildirimleri"))
        group_layout.addWidget(QCheckBox("Push bildirimleri"))
        form_layout.addRow(group_box)

        # Radio grup
        radio_group = QGroupBox("Cinsiyet")
        radio_layout = QVBoxLayout(radio_group)
        radio_layout.addWidget(QRadioButton("Erkek"))
        radio_layout.addWidget(QRadioButton("KadÄ±n"))
        radio_layout.addWidget(QRadioButton("Belirtmek istemiyorum"))
        form_layout.addRow(radio_group)

        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QPushButton("gY'ï¿½ Kaydet"))
        btn_layout.addWidget(QPushButton("gY-'ï¸ Sil"))
        btn_layout.addWidget(QPushButton("ï¿½O Ä°ptal"))
        form_layout.addRow(btn_layout)

        scroll.setWidget(form_container)
        layout.addWidget(scroll)

        return widget

    def create_widgets_tab(self) -> QWidget:
        """Widget Ã¶rnekleri tab'Ä± oluï¿½Ytur."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Butonlar
        button_group = QGroupBox("Butonlar")
        button_layout = QHBoxLayout(button_group)
        button_layout.addWidget(QPushButton("Primary"))
        button_layout.addWidget(QPushButton("Secondary"))
        button_layout.addWidget(QPushButton("Danger"))
        button_layout.addWidget(QPushButton("Success"))
        layout.addWidget(button_group)

        # Input alanlarÄ±
        input_group = QGroupBox("Input AlanlarÄ±")
        input_layout = QFormLayout(input_group)
        input_layout.addRow("Metin:", QLineEdit())
        input_layout.addRow("SayÄ±:", QSpinBox())
        input_layout.addRow("OndalÄ±k:", QDoubleSpinBox())
        input_layout.addRow("Tarih:", QDateEdit())
        layout.addWidget(input_group)

        # Tablo
        table_group = QGroupBox("ï¿½-rnek Tablo")
        table_layout = QVBoxLayout(table_group)
        
        table = QTableWidget(5, 3)
        table.setHorizontalHeaderLabels(["Ad", "SoyadÄ±", "Durum"])
        
        data = [
            ["Ali", "YÄ±lmaz", "ï¿½o""],
            ["Ayï¿½Ye", "Kara", "ï¿½o""],
            ["Mehmet", "Demir", "ï¿½sï¿½ï¸"],
            ["Fatma", "Zeynep", "ï¿½o-"],
            ["Hasan", "GÃ¶rÃ¼r", "ï¿½o""],
        ]
        
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                table.setItem(row_idx, col_idx, item)
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_layout.addWidget(table)
        layout.addWidget(table_group)

        layout.addStretch()
        return widget

    def update_palette_tab(self):
        """Renk paleti tab'Ä±nÄ± gÃ¼ncelle."""
        # Eski widget'i temizle
        while self.palette_layout.count() > 0:
            item = self.palette_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        # Yeni widget ekle
        current_tokens = DARK if ThemeManager.current_theme() == "dark" else LIGHT
        
        scroll = QScrollArea()
        scroll.setWidget(ColorPaletteWidget(current_tokens))
        scroll.setWidgetResizable(True)
        
        self.palette_layout.addWidget(scroll)

    def apply_dark_theme(self):
        """Koyu temayÄ± uygula."""
        app = QApplication.instance()
        if app:
            ThemeManager.apply_dark(app)
        self.update_palette_tab()

    def apply_light_theme(self):
        """AÃ§Ä±k temayÄ± uygula."""
        app = QApplication.instance()
        if app:
            ThemeManager.apply_light(app)
        self.update_palette_tab()


# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½
#  Standalone Mode
# ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½ï¿½.ï¿½

def main():
    """Standalone Ã§alÄ±ï¿½YtÄ±rma."""
    app = QApplication.instance() or QApplication(sys.argv)

    # Baï¿½YlangÄ±Ã§ temasÄ±
    ThemeManager.apply_dark(app)

    # Demo penceresi
    window = DemoWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

