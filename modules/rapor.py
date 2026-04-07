from app.module_registry import register, ModuleDef, Bolum
register(ModuleDef(id="rapor", label="Raporlar", icon="📈",
    bolum=Bolum.SISTEM, sira=20, page_cls="ui.pages.placeholder.PlaceholderPage"))
