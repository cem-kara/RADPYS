from app.module_registry import register, ModuleDef, Bolum
register(ModuleDef(id="nobet", label="Nöbet Planı", icon="🌙",
    bolum=Bolum.NOBET, sira=10, page_cls="ui.pages.placeholder.PlaceholderPage"))
