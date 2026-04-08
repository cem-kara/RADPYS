# -*- coding: utf-8 -*-
"""
ui/icons.py
───────────
Merkezi ikon sistemi — qtawesome (mdi6) üzerine ince sarmalayıcı.

Kullanım:
    from ui.icons import Icon, ic

    # QIcon döner — butonlar, sekme başlıkları için
    btn.setIcon(ic("duzenle"))
    btn.setIcon(ic("duzenle", renk="#5b9bff", boyut=18))

    # QLabel üzerine ikon — metin etiketleri için
    lbl = Icon.label("bildirim", renk=T.text2, boyut=16)

    # Sekme / buton metniyle birlikte
    btn = QPushButton()
    btn.setIcon(ic("kaydet"))
    btn.setText("Kaydet")
    btn.setIconSize(QSize(16, 16))

Tüm ikon isimleri bu dosyanın sonundaki IKONLAR sözlüğünde tanımlı.
Yeni ikon eklemek = IKONLAR sözlüğüne bir satır eklemek.
"""
from __future__ import annotations
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QSize
from ui.theme import T


# ── Ikon tanımları (isim → mdi6 ikon kodu) ───────────────────────
IKONLAR: dict[str, str] = {
    # ── Sidebar menü ─────────────────────────────────────────────
    "dashboard":      "mdi6.view-dashboard",
    "personel":       "mdi6.account-group",
    "izin":           "mdi6.calendar-clock",
    "saglik":         "mdi6.heart-pulse",
    "dozimetre":      "mdi6.radioactive",
    "cihaz":          "mdi6.devices",
    "ariza":          "mdi6.wrench",
    "bakim":          "mdi6.tools",
    "rke":            "mdi6.shield-check",
    "nobet":          "mdi6.moon-waning-crescent",
    "mesai":          "mdi6.clock-time-four-outline",
    "dokumanlar":     "mdi6.folder-open",
    "rapor":          "mdi6.chart-bar",
    "ayarlar":        "mdi6.cog",

    # ── Topbar ───────────────────────────────────────────────────
    "bildirim":       "mdi6.bell-outline",
    "ara":            "mdi6.magnify",
    "kullanici":      "mdi6.account-circle",
    "sistem_aktif":   "mdi6.check-circle",

    # ── Genel eylem butonları ─────────────────────────────────────
    "ekle":           "mdi6.plus",
    "duzenle":        "mdi6.pencil",
    "kaydet":         "mdi6.content-save",
    "sil":            "mdi6.delete",
    "iptal":          "mdi6.close",
    "geri":           "mdi6.arrow-left",
    "ileri":          "mdi6.arrow-right",
    "yenile":         "mdi6.refresh",
    "kapat":          "mdi6.close",
    "indir":          "mdi6.download",
    "yukle":          "mdi6.upload",
    "yazdir":         "mdi6.printer",
    "filtre":         "mdi6.filter-variant",
    "sirala":         "mdi6.sort",
    "disa_aktar":     "mdi6.export",

    # ── Alert / Bildirim ──────────────────────────────────────────
    "alert_hata":     "mdi6.alert-circle",
    "alert_uyari":    "mdi6.alert",
    "alert_basari":   "mdi6.check-circle",
    "alert_bilgi":    "mdi6.information",

    # ── Personel paneli sekmeleri ─────────────────────────────────
    "kimlik":         "mdi6.card-account-details",
    "belge":          "mdi6.file-multiple",
    "fhsz":           "mdi6.table-clock",
    "pasif":          "mdi6.account-off",
    "aktif_personel": "mdi6.account-check",

    # ── Durum ─────────────────────────────────────────────────────
    "uyari_kirmizi":  "mdi6.alert-circle",
    "uyari_sari":     "mdi6.alert",
    "check":          "mdi6.check",
    "kalkan":         "mdi6.shield",
    "radyasyon":      "mdi6.radioactive",
    "takvim":         "mdi6.calendar",
}


# ── İkon önbelleği ────────────────────────────────────────────────
_cache: dict[tuple, QIcon] = {}


def ic(isim: str,
       renk: str = "",
       boyut: int = 16,
       aktif_renk: str = "") -> QIcon:
    """
    İsme göre QIcon döner. Önbellek kullanır.

    Args:
        isim:       IKONLAR sözlüğündeki anahtar
        renk:       Hex renk kodu. Boşsa T.text2 kullanılır.
        boyut:      Pixel boyutu (genelde 14-20 arası)
        aktif_renk: İkon.Normal modunda farklı renk (opsiyonel)

    Returns:
        QIcon
    """
    import qtawesome as qta

    renk = renk or T.text2
    cache_key = (isim, renk, boyut)

    if cache_key not in _cache:
        mdi_kodu = IKONLAR.get(isim)
        if mdi_kodu is None:
            # Bilinmeyen ikon — boş QIcon döner
            _cache[cache_key] = QIcon()
        else:
            opts: dict = {"color": renk, "scale_factor": boyut / 16}
            if aktif_renk:
                opts["color_active"] = aktif_renk
            try:
                _cache[cache_key] = qta.icon(mdi_kodu, **opts)
            except Exception:
                _cache[cache_key] = QIcon()

    return _cache[cache_key]


def pixmap(isim: str,
           renk: str = "",
           boyut: int = 16) -> QPixmap:
    """QPixmap döner — özel boyutlu çizim için."""
    return ic(isim, renk, boyut).pixmap(QSize(boyut, boyut))


class Icon:
    """Kısayol metotları."""

    @staticmethod
    def label(isim: str,
              renk: str = "",
              boyut: int = 16) -> QLabel:
        """İkon içeren QLabel oluşturur."""
        lbl = QLabel()
        lbl.setPixmap(pixmap(isim, renk, boyut))
        lbl.setFixedSize(boyut, boyut)
        lbl.setStyleSheet("background:transparent;")
        return lbl

    @staticmethod
    def btn(widget, isim: str,
            renk: str = "",
            boyut: int = 16) -> None:
        """Bir butona ikon ata."""
        widget.setIcon(ic(isim, renk, boyut))
        widget.setIconSize(QSize(boyut, boyut))
