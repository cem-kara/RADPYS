# -*- coding: utf-8 -*-
"""ui/components/buttons.py - Buton bileşenleri"""
from __future__ import annotations
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QSize


def _ikon_ata(btn: QPushButton, ikon: str, renk: str, boyut: int) -> None:
    """Butona qtawesome ikonu ata. İkon boşsa hiçbir şey yapmaz."""
    if not ikon:
        return
    from ui.styles.icons import ic
    btn.setIcon(ic(ikon, size=boyut, color=renk))
    btn.setIconSize(QSize(boyut, boyut))


class PrimaryButton(QPushButton):
    """
    Mavi/teal aksiyon butonu.

    Kullanım:
        btn = PrimaryButton("Kaydet")
        btn = PrimaryButton("Ekle", ikon="ekle")
    """

    def __init__(self, text: str, ikon: str = "", parent=None):
        super().__init__(text, parent)
        self.setProperty("primary", "true")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        _ikon_ata(self, ikon, "#0b1218", 15)


class DangerButton(QPushButton):
    """
    Kırmızı silme/iptal butonu.

    Kullanım:
        btn = DangerButton("Sil")
        btn = DangerButton("Pasife Al", ikon="pasif")
    """

    def __init__(self, text: str, ikon: str = "", parent=None):
        super().__init__(text, parent)
        self.setProperty("danger", "true")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        from ui.styles import T
        _ikon_ata(self, ikon, T.red2, 15)


class SuccessButton(QPushButton):
    """
    Yeşil onay/tamamlama butonu.

    Kullanım:
        btn = SuccessButton("Onayla", ikon="check")
    """

    def __init__(self, text: str, ikon: str = "", parent=None):
        super().__init__(text, parent)
        self.setProperty("success", "true")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        from ui.styles import T
        _ikon_ata(self, ikon, T.green2, 15)


class GhostButton(QPushButton):
    """
    Şeffaf arka plan butonu.

    Kullanım:
        btn = GhostButton("İptal")
        btn = GhostButton("Yenile", ikon="yenile")
    """

    def __init__(self, text: str, ikon: str = "", parent=None):
        super().__init__(text, parent)
        self.setProperty("ghost", "true")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        from ui.styles import T
        _ikon_ata(self, ikon, T.text3, 15)


class IconButton(QPushButton):
    """
    Sadece ikon - metin yok, kare boyut.

    Kullanım:
        btn = IconButton("duzenle", tooltip="Düzenle")
        btn = IconButton("sil", tooltip="Sil", size=28, renk=T.red)
    """

    def __init__(self, ikon: str = "", tooltip: str = "",
                 size: int = 32, renk: str = "", parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setProperty("ghost", "true")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if tooltip:
            self.setToolTip(tooltip)
        if ikon:
            from ui.styles import T
            renk = renk or T.text2
            from ui.styles.icons import ic
            icon_size = max(12, size - 10)
            self.setIcon(ic(ikon, size=icon_size, color=renk))
            self.setIconSize(QSize(icon_size, icon_size))



