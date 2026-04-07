# -*- coding: utf-8 -*-
from app.module_registry import register, ModuleDef, Bolum

register(ModuleDef(
    id         = "izin",
    label      = "İzin Takip",
    icon       = "📅",
    bolum      = Bolum.ANA_MENU,
    sira       = 20,
    page_cls   = "ui.pages.placeholder.PlaceholderPage",
    badge_fn   = lambda db: str(db.fetchval(
        "SELECT COUNT(*) FROM izin WHERE durum='aktif'"
        " AND baslama <= date('now') AND bitis >= date('now')"
    ) or "") or None,
    badge_renk = "#e8a020",
))
