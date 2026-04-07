# -*- coding: utf-8 -*-
"""
app/badge_functions.py
───────────────────────
Dinamik badge fonksiyonları.

menus.json'da "badge_id" alanı olan modüller için burada
DB sorgusu yazılır. Fonksiyon None veya "" dönerse badge gizlenir.

Yeni badge eklemek:
    1. menus.json'da ilgili modüle "badge_id": "benim_badge_id" ekle
    2. Buraya aynı isimde fonksiyon yaz:
           def benim_badge_id(db) -> str | None: ...

badge_id → fonksiyon eşlemesi BADGE_FN sözlüğünde tutulur.
Başka hiçbir dosyaya dokunmak gerekmez.
"""
from __future__ import annotations
from app.db.database import Database


# ── Badge Fonksiyonları ───────────────────────────────────────────

def personel_aktif(db: Database) -> str | None:
    """Aktif personel sayısı."""
    n = db.fetchval("SELECT COUNT(*) FROM personel WHERE durum='aktif'")
    return str(n) if n else None


def izin_aktif(db: Database) -> str | None:
    """Bugün aktif olan izin sayısı."""
    n = db.fetchval(
        "SELECT COUNT(*) FROM izin "
        "WHERE durum='aktif' "
        "  AND baslama <= date('now') "
        "  AND bitis   >= date('now')"
    )
    return str(n) if n else None


def ariza_acik(db: Database) -> str | None:
    """Henüz çözülmemiş arıza sayısı — Cihaz modülü Sprint'te eklenecek."""
    # Tablo henüz yok — güvenli hata yönetimi
    try:
        n = db.fetchval(
            "SELECT COUNT(*) FROM cihaz_ariza WHERE durum='acik'"
        )
        return str(n) if n else None
    except Exception:
        return None


# ── Kayıt Sözlüğü ────────────────────────────────────────────────
# menus.json'daki badge_id → bu sözlükteki fonksiyon

BADGE_FN: dict[str, callable] = {
    "personel_aktif": personel_aktif,
    "izin_aktif":     izin_aktif,
    "ariza_acik":     ariza_acik,
}
