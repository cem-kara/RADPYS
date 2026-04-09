# -*- coding: utf-8 -*-

"""

ui/styles/colors.py - Merkezi Renk Tanımları
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Koyu ve açık temaların token sözlükleri.
Kullanım:
    from ui.styles.colors import DARK, LIGHT
    # QSS'de
    color = DARK["TEXT_PRIMARY"]  # "#d6e4f0"
"""
from __future__ import annotations

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#  KOYU TEMA PALETİ
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
DARK = {

    # Zemin
    "BG_DARK":       "#060b14",
    "BG_PRIMARY":    "#0b0f14",
    "BG_SECONDARY":  "#101722",
    "BG_TERTIARY":   "#141e2b",
    "BG_ELEVATED":   "#182436",
    "BG_HOVER":      "rgba(64,128,224,0.08)",
    "BG_SELECTED":   "rgba(64,128,224,0.15)",

    # Kenarlıklar
    "BORDER_PRIMARY":   "#192a42",
    "BORDER_SECONDARY": "#203352",
    "BORDER_STRONG":    "#2a4068",
    "BORDER_FOCUS":     "#4080e0",

    # Metin
    "TEXT_PRIMARY":       "#d6e4f0",
    "TEXT_SECONDARY":     "#6a8ca8",
    "TEXT_MUTED":         "#38526a",
    "TEXT_DISABLED":      "#1a2a3e",
    "TEXT_TABLE_HEADER":  "#9ab8d0",

    # Form
    "INPUT_BG":            "#0f1724",
    "INPUT_BORDER":        "#192a42",
    "INPUT_BORDER_FOCUS":  "#4080e0",

    # Vurgu
    "ACCENT":     "#4080e0",
    "ACCENT2":    "#60a8f8",
    "ACCENT_BG":  "rgba(64,128,224,0.12)",
    "ACCENT_10":  "rgba(64,128,224,0.10)",
    "ACCENT_20":  "rgba(64,128,224,0.20)",
    "ACCENT_35":  "rgba(64,128,224,0.35)",

    # Overlay
    "OVERLAY_LOW":  "rgba(255,255,255,0.06)",
    "OVERLAY_MID":  "rgba(255,255,255,0.11)",
    "OVERLAY_HIGH": "rgba(255,255,255,0.18)",

    # Butonlar
    "BTN_PRIMARY_BG":       "#2b62c8",
    "BTN_PRIMARY_TEXT":     "#ffffff",
    "BTN_PRIMARY_HOVER":    "#4080e0",
    "BTN_PRIMARY_BORDER":   "#2b62c8",
    "BTN_SECONDARY_BG":     "transparent",
    "BTN_SECONDARY_TEXT":   "#6a8ca8",
    "BTN_SECONDARY_BORDER": "#192a42",
    "BTN_SECONDARY_HOVER":  "#182436",
    "BTN_DANGER_BG":        "rgba(232,85,85,0.12)",
    "BTN_DANGER_TEXT":      "#e85555",
    "BTN_DANGER_BORDER":    "rgba(232,85,85,0.28)",
    "BTN_DANGER_HOVER":     "rgba(232,85,85,0.22)",
    "BTN_SUCCESS_BG":       "rgba(46,201,142,0.12)",
    "BTN_SUCCESS_TEXT":     "#2ec98e",
    "BTN_SUCCESS_BORDER":   "rgba(46,201,142,0.28)",
    "BTN_SUCCESS_HOVER":    "rgba(46,201,142,0.22)",
    "BTN_WARNING_TEXT":     "#1a0f00",

    # Durum Renkleri
    "STATUS_SUCCESS":        "#2ec98e",
    "STATUS_SUCCESS_BG":     "rgba(46,201,142,0.10)",
    "STATUS_SUCCESS_BORDER": "rgba(46,201,142,0.28)",
    "STATUS_WARNING":        "#e8a030",
    "STATUS_WARNING_BG":     "rgba(232,160,48,0.10)",
    "STATUS_WARNING_BORDER": "rgba(232,160,48,0.28)",
    "STATUS_ERROR":          "#e85555",
    "STATUS_ERROR_BG":       "rgba(232,85,85,0.10)",
    "STATUS_ERROR_BORDER":   "rgba(232,85,85,0.28)",
    "STATUS_INFO":           "#4080e0",

    # Font
    "MONOSPACE": "\"JetBrains Mono\", \"Consolas\", monospace",
    # Diğer
    "PLACEHOLDER": "#38526a",
}

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#  AÇIK TEMA PALETİ
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


LIGHT = {

    # Zemin
    "BG_DARK":       "#1e293b",
    "BG_PRIMARY":    "#eef2f7",
    "BG_SECONDARY":  "#ffffff",
    "BG_TERTIARY":   "#e4ecf4",
    "BG_ELEVATED":   "#ffffff",
    "BG_HOVER":      "rgba(37,99,200,0.06)",
    "BG_SELECTED":   "rgba(37,99,200,0.10)",

    # Kenarlıklar
    "BORDER_PRIMARY":   "#d0dce8",
    "BORDER_SECONDARY": "#b8ccdc",
    "BORDER_STRONG":    "#8aaec8",
    "BORDER_FOCUS":     "#2563c8",

    # Metin
    "TEXT_PRIMARY":       "#0f1e2e",
    "TEXT_SECONDARY":     "#3e6080",
    "TEXT_MUTED":         "#7890a4",
    "TEXT_DISABLED":      "#c4d0dc",
    "TEXT_TABLE_HEADER":  "#1a2d3e",

    # Form
    "INPUT_BG":            "#ffffff",
    "INPUT_BORDER":        "#d0dce8",
    "INPUT_BORDER_FOCUS":  "#2563c8",

    # Vurgu
    "ACCENT":     "#2563c8",
    "ACCENT2":    "#1e52a8",
    "ACCENT_BG":  "rgba(37,99,200,0.08)",
    "ACCENT_10":  "rgba(37,99,200,0.10)",
    "ACCENT_20":  "rgba(37,99,200,0.20)",
    "ACCENT_35":  "rgba(37,99,200,0.38)",

    # Overlay
    "OVERLAY_LOW":  "rgba(15,30,46,0.05)",
    "OVERLAY_MID":  "rgba(15,30,46,0.10)",
    "OVERLAY_HIGH": "rgba(15,30,46,0.16)",


    # Butonlar
    "BTN_PRIMARY_BG":       "#2563c8",
    "BTN_PRIMARY_TEXT":     "#ffffff",
    "BTN_PRIMARY_HOVER":    "#1e52a8",
    "BTN_PRIMARY_BORDER":   "#2563c8",
    "BTN_SECONDARY_BG":     "transparent",
    "BTN_SECONDARY_TEXT":   "#3e6080",
    "BTN_SECONDARY_BORDER": "#d0dce8",
    "BTN_SECONDARY_HOVER":  "#e4ecf4",
    "BTN_DANGER_BG":        "rgba(192,32,32,0.08)",
    "BTN_DANGER_TEXT":      "#b82020",
    "BTN_DANGER_BORDER":    "rgba(192,32,32,0.22)",
    "BTN_DANGER_HOVER":     "rgba(192,32,32,0.14)",
    "BTN_SUCCESS_BG":       "rgba(15,122,64,0.08)",
    "BTN_SUCCESS_TEXT":     "#0f7a40",
    "BTN_SUCCESS_BORDER":   "rgba(15,122,64,0.22)",
    "BTN_SUCCESS_HOVER":    "rgba(15,122,64,0.14)",
    "BTN_WARNING_TEXT":     "#3a1800",

    # Durum Renkleri
    "STATUS_SUCCESS":        "#0f7a40",
    "STATUS_SUCCESS_BG":     "rgba(15,122,64,0.08)",
    "STATUS_SUCCESS_BORDER": "rgba(15,122,64,0.22)",
    "STATUS_WARNING":        "#9a5800",
    "STATUS_WARNING_BG":     "rgba(154,88,0,0.08)",
    "STATUS_WARNING_BORDER": "rgba(154,88,0,0.22)",
    "STATUS_ERROR":          "#b82020",
    "STATUS_ERROR_BG":       "rgba(192,32,32,0.08)",
    "STATUS_ERROR_BORDER":   "rgba(192,32,32,0.22)",
    "STATUS_INFO":           "#2563c8",

    # Font
    "MONOSPACE": "\"JetBrains Mono\", \"Consolas\", monospace",

    # Diğer
    "PLACEHOLDER": "#7890a4",
}



