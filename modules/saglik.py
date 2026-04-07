from app.module_registry import register, ModuleDef, Bolum
register(ModuleDef(id="saglik", label="Sağlık Takip", icon="🏥",
    bolum=Bolum.ANA_MENU, sira=30, page_cls="ui.pages.placeholder.PlaceholderPage"))
