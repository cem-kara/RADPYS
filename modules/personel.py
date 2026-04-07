# -*- coding: utf-8 -*-
"""
modules/personel.py — Personel modülü tanımı.

Yeni modül yazmak için bu dosyayı şablon olarak kullan.
Sadece bu dosyayı oluşturmak yeterli — sidebar, routing otomatik güncellenir.
"""
from app.module_registry import register, ModuleDef, Bolum

register(ModuleDef(
    id        = "personel",
    label     = "Personel",
    icon      = "👤",
    bolum     = Bolum.ANA_MENU,
    sira      = 10,
    page_cls  = "ui.pages.personel.personel_page.PersonelPage",
    badge_fn  = lambda db: str(db.fetchval(
        "SELECT COUNT(*) FROM personel WHERE durum='aktif'"
    ) or ""),
    badge_renk = "#3479ff",
    varsayilan = True,
))
