from app.module_registry import register, ModuleDef, Bolum
register(ModuleDef(id="ariza", label="Arıza Takip", icon="🔧",
    bolum=Bolum.CIHAZ, sira=20, page_cls="ui.pages.placeholder.PlaceholderPage",
    badge_renk="#e83a5a"))
