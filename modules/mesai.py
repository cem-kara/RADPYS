from app.module_registry import register, ModuleDef, Bolum
register(ModuleDef(id="mesai", label="Fazla Mesai", icon="⏰",
    bolum=Bolum.NOBET, sira=20, page_cls="ui.pages.placeholder.PlaceholderPage"))
