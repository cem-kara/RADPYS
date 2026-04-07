from app.module_registry import register, ModuleDef, Bolum
register(ModuleDef(id="rke", label="RKE Envanter", icon="🛡",
    bolum=Bolum.CIHAZ, sira=40, page_cls="ui.pages.placeholder.PlaceholderPage"))
