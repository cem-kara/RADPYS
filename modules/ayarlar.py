from app.module_registry import register, ModuleDef, Bolum
register(ModuleDef(id="ayarlar", label="Yönetim", icon="⚙",
    bolum=Bolum.SISTEM, sira=30, page_cls="ui.pages.placeholder.PlaceholderPage"))
