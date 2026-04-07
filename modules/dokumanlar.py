from app.module_registry import register, ModuleDef, Bolum
register(ModuleDef(id="dokumanlar", label="Dökümanlar", icon="📁",
    bolum=Bolum.SISTEM, sira=10, page_cls="ui.pages.placeholder.PlaceholderPage"))
