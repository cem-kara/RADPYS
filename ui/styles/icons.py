# -*- coding: utf-8 -*-

"""
ui/styles/icons.py - RADPYS v2 · SVG İkon Kütüphanesi
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Profesyonel SVG icon sistemi. Lucide Icons ve Tabler Icons
projelerinden esinlenilmiştir.
Kullanım:
    from ui.styles.icons import Icons, resolve_icon_color
    # QIcon olarak al (QPushButton, QAction için)
    btn.setIcon(Icons.get("users", color="primary"))

    # QPixmap olarak al (QLabel için)
    pixmap = Icons.pixmap("users", size=20, color="#6bd3ff")

    # Rol tarafından rengi çöz
    hex_color = resolve_icon_color("accent")  -?' "#4080e0"

İcon Listesi:
    -?- users, user_add, user_check, user_minus
    -?- bell, bell_dot, search, menu, settings
    -?- check, x, chevron_up, chevron_down, chevron_left, chevron_right
    -?- calendar, clock, lock, unlock, eye, eye_off
    -?- mail, phone, world_wide_web
    -?- trash2, edit, copy, download, upload
    -?- play, pause, arrow_up, arrow_down
    Daha fazlası: SVG_PATHS dict'inde

"""
import hashlib
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QByteArray
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QPushButton, QLabel



# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#  Rol - Renk Hexöap  (QSS ile uyumlu)
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

ROLE_COLOR_MAP = {

    "primary":   "#d6e4f0",   # TEXT_PRIMARY (koyu tema)
    "secondary": "#6a8ca8",   # TEXT_SECONDARY
    "muted":     "#38526a",   # TEXT_MUTED
    "disabled":  "#1a2a3e",   # TEXT_DISABLED
    "accent":    "#4080e0",   # ACCENT
    "accent2":   "#60a8f8",   # ACCENT2
    "ok":        "#2ec98e",   # STATUS_SUCCESS
    "success":   "#2ec98e",   # Dişer isim
    "warn":      "#e8a030",   # STATUS_WARNING
    "warning":   "#e8a030",   # Dişer isim
    "err":       "#e85555",   # STATUS_ERROR
    "error":     "#e85555",   # Dişer isim
    "info":      "#4080e0",   # STATUS_INFO

}

def resolve_icon_color(color: str | None) -> str:
    """
    İcon rengini çöz. Eşer bir rol ismi ise hex koduna çevirir,
    deşilse olduşu gibi döner.
    Args:
        color: Hex renk (#rrggbb) veya rol ("primary", "accent", vs.)
    Returns:
        Hex renk kodu (#rrggbb)
    """
    if not color:
        return "#d6e4f0"  # Varsayılan: TEXT_PRIMARY

    # Hex ise olduşu gibi döner
    if isinstance(color, str) and color.startswith("#"):
        return color

    # Rol ismi ise çöz
    return ROLE_COLOR_MAP.get(str(color).lower(), "#d6e4f0")

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#  SVG Path Tanımları  (Stroke-based, Lucide/Tabler stili)
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

SVG_PATHS: dict[str, str] = {
    # ---- Personel ----------------------------------------------------------------------------------------------------
    "users": """
        <circle cx="9" cy="7" r="3.5"/>
        <path d="M2 20c0-3.866 3.134-7 7-7s7 3.134 7 7"/>
        <path d="M17 11c1.657 0 3 1.343 3 3" stroke-linecap="round"/>
        <path d="M19.5 20H22c0-2.761-1.791-5-4-5.5"/>
    """,

    "user_add": """
        <circle cx="9" cy="7" r="3.5"/>
        <path d="M2 20c0-3.866 3.134-7 7-7s7 3.134 7 7"/>
        <path d="M16 8v4m2-2h-4" stroke-linecap="round"/>
    """,

    "user_check": """
        <circle cx="9" cy="7" r="3.5"/>
        <path d="M2 20c0-3.866 3.134-7 7-7s7 3.134 7 7"/>
        <path d="M16 8l2 2l4-4" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "user_minus": """
        <circle cx="9" cy="7" r="3.5"/>
        <path d="M2 20c0-3.866 3.134-7 7-7s7 3.134 7 7"/>
        <path d="M16 10h4" stroke-linecap="round"/>
    """,

    # ---- Uyarı ve Bildirim ----------------------------------------------------------------------------

    "bell": """
        <path d="M18 8c0-1-1-2-2-2-2 0-3-1-4-1s-2 1-4 1c-1 0-2 1-2 2v10c0 1 1 2 2 2h8c1 0 2-1 2-2V8z" 
              stroke-linecap="round"/>
        <path d="M9 21a2 2 0 1 0 4 0" stroke-linecap="round"/>
    """,

    "bell_dot": """
        <path d="M18 8c0-1-1-2-2-2-2 0-3-1-4-1s-2 1-4 1c-1 0-2 1-2 2v10c0 1 1 2 2 2h8c1 0 2-1 2-2V8z" 
              stroke-linecap="round"/>
        <path d="M9 21a2 2 0 1 0 4 0" stroke-linecap="round"/>
        <circle cx="19" cy="7" r="2.5" fill="currentColor"/>
    """,

    # ---- Arama ve Menü ------------------------------------------------------------------------------------

    "search": """
        <circle cx="11" cy="11" r="8"/>
        <path d="m21 21-4.35-4.35" stroke-linecap="round"/>
    """,

    "menu": """
        <path d="M4 6h16M4 12h16M4 18h16" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "settings": """
        <circle cx="12" cy="12" r="3"/>
        <path d="M12 1v6m8.66 1.34l-4.24 4.24m1.34 8.66h-6m-8.66-1.34l4.24-4.24M1 12v6" 
              stroke-linecap="round" stroke-linejoin="round"/>
    """,

    # ---- Saşlama ve Vazgeçme ----------------------------------------------------------------------

    "check": """
        <path d="M20 6L9 17l-5-5" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "x": """
        <path d="M18 6L6 18M6 6l12 12" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "circle_check": """
        <circle cx="12" cy="12" r="10"/>
        <path d="M8 12l2 2 4-4" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "circle_x": """
        <circle cx="12" cy="12" r="10"/>
        <path d="M15 9l-6 6M9 9l6 6" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    # ---- Navigasyon ----------------------------------------------------------------------------------------
    "chevron_up": """
        <path d="M18 15l-6-6-6 6" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "chevron_down": """
        <path d="M6 9l6 6 6-6" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "chevron_left": """
        <path d="M15 18l-6-6 6-6" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "chevron_right": """
        <path d="M9 18l6-6-6-6" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "arrow_up": """
        <path d="M12 5v14m0-14l-4 4m4-4l4 4" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "arrow_down": """
        <path d="M12 19V5m0 14l-4-4m4 4l4-4" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    # ---- Tarih ve Zaman --------------------------------------------------------------------------------

    "calendar": """
        <rect x="3" y="4" width="18" height="18" rx="2"/>
        <path d="M16 2v4M8 2v4M3 10h18" stroke-linecap="round"/>
    """,

    "clock": """
        <circle cx="12" cy="12" r="9"/>
        <path d="M12 7v5l3 2" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    # ---- Güvenlik --------------------------------------------------------------------------------------------
    "lock": """
        <rect x="4" y="10" width="16" height="10" rx="2"/>
        <path d="M7 10V6a5 5 0 0 1 10 0v4" stroke-linecap="round"/>
    """,

    "unlock": """
        <rect x="4" y="10" width="16" height="10" rx="2"/>
        <path d="M10 10V6a2 2 0 1 1 4 0v4" stroke-linecap="round"/>
    """,

    "eye": """
        <circle cx="12" cy="12" r="3"/>
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke-linecap="round"/>
    """,

    "eye_off": """
        <path d="M1 1l22 22M9.88 9.88A3 3 0 1 0 15.12 15.12M9.88 9.88C8.72 8.72 8 7.27 8 5.5c0-3.035 2.686-5.5 6-5.5s6 2.465 6 5.5"/>
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke-linecap="round" fill="none"/>
    """,

    # ---- İletişim --------------------------------------------------------------------------------------------
    "mail": """
        <rect x="2" y="4" width="20" height="16" rx="2"/>
        <path d="M2 6l10 8 10-8" stroke-linecap="round"/>
    """,

    "phone": """
        <path d="M22 16.92l-3.66-1.82a2 2 0 0 0-2.15.53l-2.49 2.49c-2.8-1.4-5.6-4.2-7-7l2.49-2.49a2 2 0 0 0 .53-2.15L3.08 2" 
              stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M22 16.92v3a2 2 0 0 1-2.18 2C9.97 21 3 14.03 3 4.18A2 2 0 0 1 5.08 2h3" 
              stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "world_wide_web": """
        <circle cx="12" cy="12" r="10"/>
        <path d="M2 12h20M12 2c-3 4-4 6-4 10s1 6 4 10c3-4 4-6 4-10s-1-6-4-10"/>
    """,

    # ---- Düzenleme ve Silme --------------------------------------------------------------------

    "trash2": """
        <polyline points="3 6 5 6 21 6"/>
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
        <line x1="10" y1="11" x2="10" y2="17"/>
        <line x1="14" y1="11" x2="14" y2="17"/>
    """,

    "edit": """
        <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z" 
              stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "edit2": """
        <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>
    """,

    "copy": """
        <rect x="9" y="9" width="13" height="13" rx="2"/>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" 
              stroke-linecap="round" stroke-linejoin="round"/>
    """,

    # ---- Dosya İşlemleri ------------------------------------------------------------------------------

    "download": """
        <polyline points="8 17 12 21 16 17"/>
        <line x1="12" y1="12" x2="12" y2="21"/>
        <path d="M20.88 18.09A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.29" 
              stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "upload": """
        <polyline points="16 7 12 3 8 7"/>
        <line x1="12" y1="12" x2="12" y2="3"/>
        <path d="M20.88 18.09A5 5 0 0 1 18 9h-1.26A8 8 0 1 1 3 16.29" 
              stroke-linecap="round" stroke-linejoin="round"/>
    """,

    # ---- Medya Kontrolleri ----------------------------------------------------------------------------

    "play": """
        <polygon points="5 3 19 12 5 21 5 3"/>
    """,

    "pause": """
        <rect x="6" y="4" width="4" height="16"/>
        <rect x="14" y="4" width="4" height="16"/>
    """,

    "stop": """
        <square x="4" y="4" width="16" height="16"/>
    """,

    # ---- Diğer --------------------------------------------------------------------------------------------------

    "alert": """
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
    """,

    "info": """
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="16" x2="12" y2="12"/>
        <line x1="12" y1="8" x2="12.01" y2="8"/>
    """,

    # Daha fazla eklenebilir...

    # ---- Sidebar menü (Türkçe isimler -?" menus.json uyumlu) ----------

    "dashboard": """
        <rect x="3" y="3" width="7" height="7" rx="1.5"/>
        <rect x="14" y="3" width="7" height="7" rx="1.5"/>
        <rect x="3" y="14" width="7" height="7" rx="1.5"/>
        <rect x="14" y="14" width="7" height="7" rx="1.5"/>
    """,

    "personel": """
        <circle cx="9" cy="7" r="3.5"/>
        <path d="M2 20c0-3.866 3.134-7 7-7s7 3.134 7 7"/>
        <path d="M17 11c1.657 0 3 1.343 3 3" stroke-linecap="round"/>
        <path d="M19.5 20H22c0-2.761-1.791-5-4-5.5"/>
    """,

    "izin": """
        <rect x="3" y="4" width="18" height="18" rx="2"/>
        <path d="M16 2v4M8 2v4M3 10h18" stroke-linecap="round"/>
        <circle cx="16" cy="16" r="3"/>
        <path d="M16 14.5v1.5l1 1" stroke-linecap="round"/>
    """,

    "saglik": """
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78
                 l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
              stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M6 12h2l2-4 2 8 2-4h2" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "dozimetre": """
        <circle cx="12" cy="12" r="2" fill="currentColor"/>
        <path d="M12 10V4" stroke-linecap="round"/>
        <path d="M10.27 11.27L5.5 8.5" stroke-linecap="round"/>
        <path d="M13.73 11.27L18.5 8.5" stroke-linecap="round"/>
        <path d="M12 14v6" stroke-linecap="round"/>
        <path d="M10.27 12.73L5.5 15.5" stroke-linecap="round"/>
        <path d="M13.73 12.73L18.5 15.5" stroke-linecap="round"/>
    """,

    "cihaz": """
        <rect x="2" y="3" width="20" height="13" rx="2"/>
        <path d="M8 21h8M12 17v4" stroke-linecap="round"/>
    """,

    "ariza": """
        <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77
                 a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91
                 a6 6 0 0 1 7.94-7.94l-3.76 3.76z"
              stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "bakim": """
        <circle cx="12" cy="12" r="3"/>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06
                 a1.65 1.65 0 0 0-2.82 1.17V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4
                 a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06
                 A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09
                 A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06
                 a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51
                 V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06
                 a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9
                 a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"
              stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "rke": """
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"
              stroke-linejoin="round"/>
        <path d="M8 12l3 3 5-5" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "nobet": """
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"
              stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "mesai": """
        <circle cx="12" cy="12" r="9"/>
        <path d="M12 7v5l3 2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M17 18l2 2" stroke-linecap="round"/>
    """,

    "dokumanlar": """
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"
              stroke-linejoin="round"/>
        <path d="M8 13h8M8 17h5" stroke-linecap="round"/>
    """,

    "rapor": """
        <path d="M18 20V10" stroke-linecap="round"/>
        <path d="M12 20V4" stroke-linecap="round"/>
        <path d="M6 20v-6" stroke-linecap="round"/>
        <path d="M2 20h20" stroke-linecap="round"/>
    """,

    "ayarlar": """
        <circle cx="12" cy="12" r="3"/>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06
                 a1.65 1.65 0 0 0-2.82 1.17V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4
                 a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06
                 A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09
                 A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06
                 a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51
                 V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06
                 a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9
                 a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"
              stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "bildirim": """
        <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" stroke-linecap="round"/>
        <path d="M13.73 21a2 2 0 0 1-3.46 0" stroke-linecap="round"/>
    """,

    "kullanici": """
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke-linecap="round"/>
        <circle cx="12" cy="7" r="4"/>
    """,

    # ---- Türkçe takma adlar (bileşenler + sayfalar için) ------------------------

    "kapat": """
        <path d="M18 6L6 18M6 6l12 12" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "goz": """
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke-linejoin="round"/>
        <circle cx="12" cy="12" r="3"/>
    """,

    "goz_kapali": """
        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8
                 a18.45 18.45 0 0 1 5.06-5.94" stroke-linecap="round"/>
        <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8
                 a18.5 18.5 0 0 1-2.16 3.19" stroke-linecap="round"/>
        <path d="M1 1l22 22" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "ara": """
        <circle cx="11" cy="11" r="8"/>
        <path d="m21 21-4.35-4.35" stroke-linecap="round"/>
    """,

    "parola": """
        <rect x="4" y="10" width="16" height="10" rx="2"/>
        <path d="M7 10V6a5 5 0 0 1 10 0v4" stroke-linecap="round"/>
    """,

    "ekle": """
        <path d="M12 5v14M5 12h14" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "geri": """
        <path d="M15 18l-6-6 6-6" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "kimlik": """
        <rect x="2" y="5" width="20" height="14" rx="2"/>
        <circle cx="8" cy="12" r="2.5"/>
        <path d="M14 10h4M14 14h3" stroke-linecap="round"/>
    """,

    "fhsz": """
        <rect x="3" y="3" width="18" height="18" rx="2"/>
        <path d="M3 9h18M9 9v12M3 15h6" stroke-linecap="round"/>
    """,

    "belge": """
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"
              stroke-linejoin="round"/>
        <path d="M14 2v6h6M8 13h8M8 17h5" stroke-linecap="round"/>
    """,

    "yenile": """
        <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 0 0 4.582 9m0 0H9
                 m11 11v-5h-.581m0 0a8 8 0 0 1-15.357-2m15.357 2H15"
              stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "duzenle": """
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"
              stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"
              stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "kaydet": """
        <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"
              stroke-linejoin="round"/>
        <path d="M17 21v-8H7v8M7 3v5h8" stroke-linecap="round"/>
    """,

    "alert_hata": """
        <circle cx="12" cy="12" r="10"/>
        <path d="M15 9l-6 6M9 9l6 6" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "alert_uyari": """
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3
                 L13.71 3.86a2 2 0 0 0-3.42 0z" stroke-linejoin="round"/>
        <path d="M12 9v4M12 17h.01" stroke-linecap="round"/>
    """,

    "alert_basari": """
        <circle cx="12" cy="12" r="10"/>
        <path d="M8 12l2 2 4-4" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "alert_bilgi": """
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 16v-4M12 8h.01" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "pasif": """
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke-linecap="round"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M23 18l-2-2-2 2M19 16v5" stroke-linecap="round" stroke-linejoin="round"/>
    """,

    "aktif_personel": """
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke-linecap="round"/>
        <circle cx="9" cy="7" r="4"/>
        <path d="M16 11l2 2 4-4" stroke-linecap="round" stroke-linejoin="round"/>
    """,
}

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#  Icons Sınıfı
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Icons:
    """SVG İcon Yöneticisi."""
    DEFAULT_COLOR = "#d6e4f0"
    DEFAULT_SIZE = 16
    _qss_cache: dict[str, str] = {}

    @staticmethod
    def get(name: str, size: int = 16, color: str | None = None) -> QIcon:
        """
        SVG ikondan QIcon oluştur.
        Args:
            name:  İcon adı ("users", "bell", vs.)
            size:  Boyut piksel (varsayılan: 16)
            color: Renk hex veya rol ("primary", "accent", vs.)

        Returns:
            QIcon örneşi
        """

        color = resolve_icon_color(color)
        svg_content = SVG_PATHS.get(name, "")

        if not svg_content:
            return QIcon()  # Boş ikon
        return Icons._create_icon(svg_content, size, color)

    @staticmethod
    def pixmap(name: str, size: int = 16, color: str | None = None) -> QPixmap:
        """
        SVG ikondan QPixmap oluştur.

        Args:
            name:  İcon adı
            size:  Boyut piksel
            color: Renk hex veya rol
        Returns:
            QPixmap örneşi
        """
        color = resolve_icon_color(color)
        svg_content = SVG_PATHS.get(name, "")

        if not svg_content:
            return QPixmap()  # Boş pixmap
        return Icons._create_pixmap(svg_content, size, color)

    @staticmethod
    def _create_icon(svg_content: str, size: int, color: str) -> QIcon:
        """SVG içerikten HiDPI-aware çok-çözünürlüklü QIcon oluştur."""
        icon = QIcon()
        for scale in (1, 2):
            pm = Icons._create_pixmap(svg_content, size, color, _scale=scale)
            icon.addPixmap(pm)
        return icon

    @staticmethod
    def _create_pixmap(svg_content: str, size: int, color: str, _scale: int = 1) -> QPixmap:
        """SVG içerikten HiDPI-aware QPixmap oluştur."""
        actual = size * _scale
        svg_data = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            f'width="{actual}" height="{actual}" '
            f'fill="none" stroke="{color}" stroke-width="1.75" '
            'stroke-linecap="round" stroke-linejoin="round">'
            + svg_content
            + '</svg>'
        )
        pixmap = QPixmap(actual, actual)
        pixmap.fill(Qt.GlobalColor.transparent)
        pixmap.setDevicePixelRatio(_scale)
        qsvg = QSvgRenderer(QByteArray(svg_data.encode("utf-8")))
        painter = QPainter(pixmap)
        qsvg.render(painter)
        painter.end()
        return pixmap

    @staticmethod
    def available() -> list[str]:
        """Mevcut tüm icon adlarını döner."""
        return list(SVG_PATHS.keys())

    @staticmethod
    def qss_url(name: str, color: str | None = None, size: int = 16) -> str:
        """QSS image:url(...) icin temp klasorde SVG olusturup dosya URL'i dondurur."""
        svg_content = SVG_PATHS.get(name, "")
        if not svg_content:
            return ""

        hex_color = resolve_icon_color(color)
        cache_key = f"{name}|{hex_color}|{size}"
        cached = Icons._qss_cache.get(cache_key)
        if cached:
            return cached

        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            f'width="{size}" height="{size}" '
            'fill="none" '
            f'stroke="{hex_color}" stroke-width="1.9" '
            'stroke-linecap="round" stroke-linejoin="round">'
            f"{svg_content}</svg>"
        )

        # Turkce karakter ve bosluk iceren proje yolundan bagimsiz temp dizin.
        temp_dir = Path(tempfile.gettempdir()) / "radpys_qss_icons"
        temp_dir.mkdir(parents=True, exist_ok=True)

        digest = hashlib.sha1(cache_key.encode("utf-8")).hexdigest()[:12]
        file_path = temp_dir / f"{name}_{size}_{digest}.svg"
        if not file_path.exists():
            file_path.write_text(svg, encoding="utf-8")

        # QSS url() ham dosya yolu ister; file:// oneki eklenmemeli.
        url = str(file_path).replace("\\", "/")
        Icons._qss_cache[cache_key] = url
        return url



    @staticmethod
    def label(name: str, color: str | None = None, size: int = 16) -> "QLabel":
        """QLabel içinde ikon döner (eski Icon.label() uyumluluşu)."""
        lbl = QLabel()
        lbl.setPixmap(Icons.pixmap(name, size=size, color=color))
        lbl.setFixedSize(size, size)
        lbl.setStyleSheet("background:transparent;")
        return lbl

    @staticmethod
    def btn(widget, name: str, color: str | None = None, size: int = 16) -> None:
        """Butona ikon ata (eski Icon.btn() uyumluluşu)."""
        widget.setIcon(Icons.get(name, size=size, color=color))
        widget.setIconSize(QSize(size, size))

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#  Uyumluluşu (eski kodlar için - ui/icons.py ile uyumlu)
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def ic(name: str, size: int = 16, color: str | None = None) -> QIcon:
    """
    Kısayol fonksiyon. eski ui/icons.py ile uyumlu.
    Kullanım:
        from ui.styles import ic
        button.setIcon(ic("users", size=20, color="accent"))
    """
    return Icons.get(name, size=size, color=color)

def pixmap(name: str, size: int = 16, color: str | None = None) -> QPixmap:
    """Kısayol -?" QPixmap döner (QLabel için)."""
    return Icons.pixmap(name, size=size, color=color)



