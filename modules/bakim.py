from app.module_registry import register, ModuleDef, Bolum
register(ModuleDef(id="bakim", label="Bakım & Kalibr.", icon="🔬",
    bolum=Bolum.CIHAZ, sira=30, page_cls="ui.pages.placeholder.PlaceholderPage"))
