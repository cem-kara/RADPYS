from app.module_registry import register, ModuleDef, Bolum
register(ModuleDef(id="dozimetre", label="Dozimetre", icon="☢",
    bolum=Bolum.ANA_MENU, sira=40, page_cls="ui.pages.placeholder.PlaceholderPage"))
