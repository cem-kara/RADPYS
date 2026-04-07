from app.module_registry import register, ModuleDef, Bolum
register(ModuleDef(id="cihaz", label="Cihaz Listesi", icon="⚙",
    bolum=Bolum.CIHAZ, sira=10, page_cls="ui.pages.placeholder.PlaceholderPage"))
