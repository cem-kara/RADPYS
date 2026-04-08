# -*- coding: utf-8 -*-
"""tests/test_auth_usecases.py"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import Database
from app.db.migrations import run as migrate
from app.db.repos.kullanici_repo import KullaniciRepo
from app.exceptions import DogrulamaHatasi, KayitZatenVar
from app.usecases.auth import (
    kullanici_aktiflik_guncelle,
    kullanici_ekle,
    kullanici_rol_guncelle,
)


@pytest.fixture
def db(tmp_path):
    d = Database(tmp_path / "test.db")
    migrate(d)
    yield d
    d.close()


@pytest.fixture
def repo(db):
    return KullaniciRepo(db)


def _hash(parola: str) -> str:
    return "HASH:" + parola


def _rol_var_mi(rol: str) -> bool:
    return rol in {"admin", "yonetici", "kullanici"}


class TestKullaniciEkleUseCase:

    def test_basarili(self, repo):
        kid = kullanici_ekle(
            repo,
            _hash,
            _rol_var_mi,
            {"ad": "ucase1", "parola": "guclu123", "rol": "kullanici"},
        )
        row = repo.id_ile_getir(kid)
        assert row is not None
        assert row["ad"] == "ucase1"
        assert row["sifre_hash"] == "HASH:guclu123"
        assert int(row["sifre_degismeli"]) == 1

    def test_gecersiz_rol(self, repo):
        with pytest.raises(DogrulamaHatasi):
            kullanici_ekle(
                repo,
                _hash,
                _rol_var_mi,
                {"ad": "ucase2", "parola": "guclu123", "rol": "x"},
            )

    def test_tekrarli_ad(self, repo):
        kullanici_ekle(
            repo,
            _hash,
            _rol_var_mi,
            {"ad": "ucase3", "parola": "guclu123", "rol": "kullanici"},
        )
        with pytest.raises(KayitZatenVar):
            kullanici_ekle(
                repo,
                _hash,
                _rol_var_mi,
                {"ad": "ucase3", "parola": "guclu123", "rol": "kullanici"},
            )


class TestKullaniciGuncelleUseCase:

    def test_rol_gunceller(self, repo):
        kid = kullanici_ekle(
            repo,
            _hash,
            _rol_var_mi,
            {"ad": "ucase4", "parola": "guclu123", "rol": "kullanici"},
        )
        kullanici_rol_guncelle(repo, kid, "yonetici")
        row = repo.id_ile_getir(kid)
        assert row is not None
        assert row["rol"] == "yonetici"

    def test_aktiflik_gunceller(self, repo):
        kid = kullanici_ekle(
            repo,
            _hash,
            _rol_var_mi,
            {"ad": "ucase5", "parola": "guclu123", "rol": "kullanici"},
        )
        kullanici_aktiflik_guncelle(repo, kid, False)
        row = repo.id_ile_getir(kid)
        assert int(row["aktif"]) == 0
