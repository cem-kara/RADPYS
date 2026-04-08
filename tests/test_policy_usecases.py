# -*- coding: utf-8 -*-
"""tests/test_policy_usecases.py"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import Database
from app.db.migrations import run as migrate
from app.db.repos.policy_repo import PolicyRepo
from app.exceptions import YetkiHatasi
from app.usecases.policy import rol_modullerini_kaydet, tum_rol_modulleri_getir


@pytest.fixture
def db(tmp_path):
    d = Database(tmp_path / "test.db")
    migrate(d)
    yield d
    d.close()


@pytest.fixture
def repo(db):
    return PolicyRepo(db)


class TestTumRolModulleriGetirUseCase:

    def test_admin_none_doner(self, repo):
        harita = tum_rol_modulleri_getir(repo.tum_izinler())
        assert "admin" in harita
        assert harita["admin"] is None

    def test_kullanici_set_doner(self, repo):
        harita = tum_rol_modulleri_getir(repo.tum_izinler())
        assert "kullanici" in harita
        assert isinstance(harita["kullanici"], set)


class TestRolModulleriniKaydetUseCase:

    def test_admin_rolu_icin_hata(self, repo):
        with pytest.raises(YetkiHatasi):
            rol_modullerini_kaydet(repo, "admin", {"dashboard"})

    def test_yonetici_icin_kayit(self, repo):
        rol_modullerini_kaydet(repo, "yonetici", {"dashboard", "personel"})
        rows = repo.rol_izinleri("yonetici")
        izinliler = {r["modul_id"] for r in rows if int(r.get("izinli", 0))}
        assert izinliler == {"dashboard", "personel"}
