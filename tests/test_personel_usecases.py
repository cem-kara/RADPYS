# -*- coding: utf-8 -*-
"""tests/test_personel_usecases.py"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import Database
from app.db.migrations import run as migrate
from app.db.repos.lookup_repo import GorevYeriRepo
from app.db.repos.personel_repo import PersonelRepo
from app.exceptions import KayitZatenVar, PasifPersonelHatasi
from app.usecases.personel import personel_ekle, personel_guncelle, personel_pasife_al


@pytest.fixture
def db(tmp_path):
    d = Database(tmp_path / "test.db")
    migrate(d)
    yield d
    d.close()


@pytest.fixture
def personel_repo(db):
    return PersonelRepo(db)


@pytest.fixture
def gorev_yeri_repo(db):
    return GorevYeriRepo(db)


class TestPersonelEkleUseCase:

    def test_basarili_ve_gorev_yeri_ad_cozumu(self, personel_repo, gorev_yeri_repo):
        gy = gorev_yeri_repo.listele()[0]
        pid = personel_ekle(
            personel_repo,
            gorev_yeri_repo,
            {
                "tc_kimlik": "10000000146",
                "ad": "Ali",
                "soyad": "Kaya",
                "gorev_yeri_ad": gy["ad"],
            },
        )
        row = personel_repo.getir(pid)
        assert row is not None
        assert row["gorev_yeri_id"] == gy["id"]

    def test_ayni_tc_tekrar_eklenemez(self, personel_repo, gorev_yeri_repo):
        personel_ekle(
            personel_repo,
            gorev_yeri_repo,
            {"tc_kimlik": "10000000146", "ad": "Ali", "soyad": "Kaya"},
        )
        with pytest.raises(KayitZatenVar):
            personel_ekle(
                personel_repo,
                gorev_yeri_repo,
                {"tc_kimlik": "10000000146", "ad": "Veli", "soyad": "Kaya"},
            )


class TestPersonelGuncelleUseCase:

    def test_tc_ve_id_korunur(self, personel_repo, gorev_yeri_repo):
        pid = personel_ekle(
            personel_repo,
            gorev_yeri_repo,
            {"tc_kimlik": "10000000146", "ad": "Ali", "soyad": "Kaya"},
        )

        personel_guncelle(
            personel_repo,
            gorev_yeri_repo,
            pid,
            {"tc_kimlik": "99999999999", "id": "fake", "telefon": "05550000000"},
        )
        row = personel_repo.getir(pid)
        assert row is not None
        assert row["tc_kimlik"] == "10000000146"
        assert row["telefon"] == "05550000000"


class TestPersonelPasifeAlUseCase:

    def test_pasife_alir(self, personel_repo, gorev_yeri_repo):
        pid = personel_ekle(
            personel_repo,
            gorev_yeri_repo,
            {"tc_kimlik": "10000000146", "ad": "Ali", "soyad": "Kaya"},
        )
        mevcut = personel_repo.getir(pid)
        personel_pasife_al(personel_repo, mevcut, pid, "2026-01-01", "Emeklilik")

        row = personel_repo.getir(pid)
        assert row is not None
        assert row["durum"] == "ayrildi"
        assert row["ayrilik_tarihi"] == "2026-01-01"
        assert row["ayrilik_nedeni"] == "Emeklilik"

    def test_zaten_ayrildiysa_hata(self, personel_repo, gorev_yeri_repo):
        pid = personel_ekle(
            personel_repo,
            gorev_yeri_repo,
            {"tc_kimlik": "10000000146", "ad": "Ali", "soyad": "Kaya"},
        )
        mevcut = personel_repo.getir(pid)
        personel_pasife_al(personel_repo, mevcut, pid, "2026-01-01")
        ayrilmis = personel_repo.getir(pid)

        with pytest.raises(PasifPersonelHatasi):
            personel_pasife_al(personel_repo, ayrilmis, pid, "2026-02-01")
