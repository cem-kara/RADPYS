# -*- coding: utf-8 -*-
"""tests/test_module_registry.py"""
import sys
from pathlib import Path
from types import ModuleType

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import app.module_registry as mr


@pytest.fixture
def temiz_registry(monkeypatch):
    monkeypatch.setattr(mr, "_yuklendi", False)
    mr._moduller.clear()
    mr._bolumler.clear()
    yield
    monkeypatch.setattr(mr, "_yuklendi", False)
    mr._moduller.clear()
    mr._bolumler.clear()


class TestRegistryYukleme:

    def test_get_all_bos_degildir(self, temiz_registry):
        lst = mr.get_all()
        assert len(lst) > 0

    def test_varsayilan_id_beklenen_deger(self, temiz_registry):
        assert mr.get_varsayilan_id() == "personel"

    def test_get_bolumler_bolum_ve_modul_icerir(self, temiz_registry):
        bolumler = mr.get_bolumler()
        assert len(bolumler) > 0
        bolum, moduller = bolumler[0]
        assert bolum.id
        assert isinstance(moduller, list)


class TestSayfaOlustur:

    def test_bilinmeyen_modul_hata_firlatir(self, temiz_registry):
        with pytest.raises(KeyError):
            mr.sayfa_olustur("olmayan_modul", db=object())

    def test_gecersiz_page_cls_hata_firlatir(self, monkeypatch):
        sahte_modul = mr.ModuleDef(
            id="sahte_modul",
            label="Sahte",
            icon="dashboard",
            bolum="ana_menu",
            bolum_sira=0,
            sira=0,
            page_cls="gecersiz-page-cls",
        )
        monkeypatch.setattr(mr, "_moduller", [sahte_modul])
        monkeypatch.setattr(mr, "_yuklendi", True)

        with pytest.raises(ValueError):
            mr.sayfa_olustur("sahte_modul", db=object())

    def test_oturum_parametresi_desteklemeyen_sinifa_fallback(self, monkeypatch):
        class SahteSayfa:
            def __init__(self, db):
                self.db = db

        sahte_modul = ModuleType("tests._sahte_page_modulu")
        sahte_modul.SahteSayfa = SahteSayfa
        sys.modules["tests._sahte_page_modulu"] = sahte_modul

        kayit = mr.ModuleDef(
            id="sahte",
            label="Sahte",
            icon="dashboard",
            bolum="ana_menu",
            bolum_sira=0,
            sira=0,
            page_cls="tests._sahte_page_modulu.SahteSayfa",
        )
        monkeypatch.setattr(mr, "_moduller", [kayit])
        monkeypatch.setattr(mr, "_yuklendi", True)

        widget = mr.sayfa_olustur("sahte", db="db-nesnesi", oturum={"rol": "admin"})
        assert isinstance(widget, SahteSayfa)
        assert widget.db == "db-nesnesi"
