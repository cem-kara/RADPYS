# -*- coding: utf-8 -*-
"""ui/pages/demo/theme_demo_form.py - Tema ve bilesen demo sayfasi."""
from __future__ import annotations

from pathlib import Path
import sys

from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

try:
    from ui.components import (
        AlertBar,
        Badge,
        Card,
        CheckField,
        ComboField,
        DangerButton,
        DataTable,
        DateField,
        FloatField,
        FormGroup,
        GhostButton,
        IntField,
        PrimaryButton,
        RadioGroup,
        SearchBar,
        SectionCard,
        StatCard,
        SuccessButton,
        TextAreaField,
        TextField,
    )
    from ui.styles import DARK, LIGHT, T, ThemeManager
except ModuleNotFoundError:
    project_root = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from ui.components import (
        AlertBar,
        Badge,
        Card,
        CheckField,
        ComboField,
        DangerButton,
        DataTable,
        DateField,
        FloatField,
        FormGroup,
        GhostButton,
        IntField,
        PrimaryButton,
        RadioGroup,
        SearchBar,
        SectionCard,
        StatCard,
        SuccessButton,
        TextAreaField,
        TextField,
    )
    from ui.styles import DARK, LIGHT, T, ThemeManager


class _ColorPaletteWidget(QWidget):
    """Aktif temadaki token renklerini listeler."""

    _GROUPS = {
        "Zemin": ["BG_PRIMARY", "BG_SECONDARY", "BG_TERTIARY", "BG_ELEVATED", "BG_HOVER"],
        "Metin": ["TEXT_PRIMARY", "TEXT_SECONDARY", "TEXT_MUTED"],
        "Vurgu": ["ACCENT", "ACCENT2", "ACCENT_BG"],
        "Durum": ["STATUS_SUCCESS", "STATUS_WARNING", "STATUS_ERROR", "STATUS_INFO"],
    }

    def __init__(self, tokens: dict[str, str], parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(10)

        for group_name, token_names in self._GROUPS.items():
            title = QLabel(group_name)
            title.setStyleSheet(f"color:{T.text2}; font-weight:600;")
            lay.addWidget(title)
            for token_name in token_names:
                lay.addWidget(self._row(token_name, tokens.get(token_name, "-")))

        lay.addStretch()

    def _row(self, key: str, value: str) -> QWidget:
        row = QFrame()
        row.setStyleSheet(
            f"background:{T.bg2}; border:1px solid {T.border}; border-radius:{T.radius_sm}px;"
        )
        rlay = QHBoxLayout(row)
        rlay.setContentsMargins(10, 8, 10, 8)
        rlay.setSpacing(10)

        chip = QFrame()
        chip.setFixedSize(34, 20)
        chip.setStyleSheet(f"background:{value}; border:1px solid {T.border2}; border-radius:4px;")

        label = QLabel(f"{key}: {value}")
        label.setStyleSheet(f"color:{T.text};")

        rlay.addWidget(chip)
        rlay.addWidget(label)
        rlay.addStretch()
        return row


class ThemeDemoForm(QWidget):
    """Tema, form ve ortak bilesenleri gosteren demo sayfasi."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._palette_host = QWidget()
        self._palette_lay = QVBoxLayout(self._palette_host)
        self._palette_lay.setContentsMargins(0, 0, 0, 0)
        self._palette_lay.setSpacing(0)
        self._build()
        self._refresh_palette()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(12)

        top = QHBoxLayout()
        top.setSpacing(8)
        title = QLabel("RADPYS tema ve bilesen demosu")
        title.setStyleSheet(f"color:{T.text}; font-size:16px; font-weight:700;")
        top.addWidget(title)
        top.addStretch()

        dark_btn = GhostButton("Koyu Tema")
        light_btn = GhostButton("Acik Tema")
        dark_btn.clicked.connect(lambda: self._set_theme("dark"))
        light_btn.clicked.connect(lambda: self._set_theme("light"))
        top.addWidget(dark_btn)
        top.addWidget(light_btn)
        root.addLayout(top)

        self._alert = AlertBar(self)
        self._alert.goster("Bu ekran guncel tema tokenlari ve ortak UI bilesenlerini gosterir.", "info")
        root.addWidget(self._alert)

        tabs = QTabWidget()
        tabs.addTab(self._build_components_tab(), "Bilesenler")
        tabs.addTab(self._build_form_tab(), "Form")
        tabs.addTab(self._build_table_tab(), "Tablo")
        tabs.addTab(self._palette_host, "Renkler")
        root.addWidget(tabs, 1)

    def _build_components_tab(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(12)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)
        c1 = StatCard("Aktif Personel")
        c1.set("128", alt="Toplam personel")
        c2 = StatCard("Bugun Nobet")
        c2.set("14", alt="Planlanan vardiya")
        c3 = StatCard("Acik Is")
        c3.set("3", renk=T.amber, alt="Takip edilen kayit")
        stats_row.addWidget(c1)
        stats_row.addWidget(c2)
        stats_row.addWidget(c3)
        lay.addLayout(stats_row)

        section = SectionCard("Buton ve durum gosterimi")
        badges = QHBoxLayout()
        badges.addWidget(Badge("aktif"))
        badges.addWidget(Badge("uyari"))
        badges.addWidget(Badge("tehlike"))
        badges.addStretch()
        section.layout_.addLayout(badges)

        buttons = QHBoxLayout()
        buttons.addWidget(PrimaryButton("Kaydet"))
        buttons.addWidget(SuccessButton("Onayla"))
        buttons.addWidget(DangerButton("Sil"))
        buttons.addWidget(GhostButton("Vazgec"))
        buttons.addStretch()
        section.layout_.addLayout(buttons)
        lay.addWidget(section)

        note = Card()
        note.layout_.addWidget(
            QLabel("Kart, rozet, buton ve uyarilar ortak component kutuphanesinden gelir.")
        )
        lay.addWidget(note)
        lay.addStretch()
        return page

    def _build_form_tab(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(12)

        grp = FormGroup("Ornek personel formu")
        self._ad = TextField("Ad Soyad", zorunlu=True, placeholder="Orn: Ayse Yilmaz")
        self._tc = TextField("TC Kimlik", max_uzunluk=11)
        self._dogum = DateField("Dogum Tarihi")
        self._birim = ComboField("Gorev Yeri")
        self._birim.doldur([("Radyoloji", "radyoloji"), ("MR", "mr"), ("BT", "bt")])
        self._puan = FloatField("Nobet Katsayisi", min_val=0.0, max_val=3.0, adim=0.1)
        self._kid = IntField("Kidemi (yil)", min_val=0, max_val=40)
        self._aktif = CheckField("Aktif Personel", varsayilan=True)
        self._vardiya = RadioGroup("Vardiya", secenekler=[("Gunduz", "gunduz"), ("Gece", "gece")])
        self._not = TextAreaField("Not", placeholder="Kisa aciklama giriniz", yukseklik=76)

        grp.ekle_yatay(self._ad, self._tc)
        grp.ekle_yatay(self._dogum, self._birim)
        grp.ekle_yatay(self._kid, self._puan)
        grp.ekle_yatay(self._aktif, self._vardiya)
        grp.ekle(self._not)
        lay.addWidget(grp)

        actions = QHBoxLayout()
        btn_preview = PrimaryButton("Onizleme")
        btn_clear = GhostButton("Temizle")
        actions.addWidget(btn_preview)
        actions.addWidget(btn_clear)
        actions.addStretch()
        lay.addLayout(actions)

        btn_preview.clicked.connect(self._show_preview)
        btn_clear.clicked.connect(self._clear_form)
        lay.addStretch()
        return page

    def _build_table_tab(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(10)

        self._search = SearchBar("Ad, birim veya durum ara")
        lay.addWidget(self._search)

        self._table = DataTable()
        self._table.kur_kolonlar(
            [
                ("ad", "Ad Soyad", 220),
                ("birim", "Birim", 130),
                ("durum", "Durum", 90),
                ("telefon", "Telefon", 160),
            ]
        )
        self._table.set_veri(
            [
                {"ad": "Ali Kaya", "birim": "MR", "durum": "Aktif", "telefon": "0555 111 22 33"},
                {"ad": "Ayse Demir", "birim": "BT", "durum": "Aktif", "telefon": "0555 444 55 66"},
                {"ad": "Kemal Aras", "birim": "Radyoloji", "durum": "Pasif", "telefon": "0555 777 88 99"},
            ]
        )
        self._search.textChanged.connect(self._table.ara)
        lay.addWidget(self._table, 1)
        return page

    def _refresh_palette(self) -> None:
        while self._palette_lay.count() > 0:
            item = self._palette_lay.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        tokens = LIGHT if ThemeManager.current_theme() == "light" else DARK
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(_ColorPaletteWidget(tokens, self))
        self._palette_lay.addWidget(scroll)

    def _set_theme(self, theme_name: str) -> None:
        app = QApplication.instance()
        if not app:
            return
        if theme_name == "light":
            ThemeManager.apply_light(app)
        else:
            ThemeManager.apply_dark(app)
        self._refresh_palette()

    def _show_preview(self) -> None:
        if not self._ad.deger():
            self._ad.hata_goster("Ad alani zorunludur.")
            self._alert.goster("Formda eksik alan var.", "warning")
            return
        self._ad.hata_temizle()
        self._alert.goster(
            f"Onizleme: {self._ad.deger()} / {self._birim.deger() or '-'} / {self._vardiya.deger() or '-'}",
            "success",
        )

    def _clear_form(self) -> None:
        self._ad.set_deger("")
        self._tc.set_deger("")
        self._dogum.set_deger("")
        self._birim.set_deger("")
        self._puan.set_deger(0.0)
        self._kid.set_deger(0)
        self._aktif.set_deger(True)
        self._vardiya.set_deger("")
        self._not.set_deger("")
        self._ad.hata_temizle()
        self._alert.goster("Form temizlendi.", "info")


class DemoWindow(QMainWindow):
    """Standalone calisma icin pencere sarmalayicisi."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RADPYS Tema Demo")
        self.resize(1180, 760)
        self.setCentralWidget(ThemeDemoForm(self))


def main() -> None:
    """Demo penceresini tek basina calistirir."""
    app = QApplication.instance() or QApplication(sys.argv)
    ThemeManager.apply_dark(app)
    win = DemoWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()