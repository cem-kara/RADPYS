# -*- coding: utf-8 -*-
from app.module_registry import register, ModuleDef, Bolum

register(ModuleDef(
    id       = "dashboard",
    label    = "Dashboard",
    icon     = "⊞",
    bolum    = Bolum.ANA_MENU,
    sira     = 0,
    page_cls = "ui.pages.dashboard.dashboard_page.DashboardPage",
))
