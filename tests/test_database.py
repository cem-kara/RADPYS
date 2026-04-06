# -*- coding: utf-8 -*-
"""tests/test_database.py — Database ve migration testleri"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.db.database import Database
from app.db.migrations import run as migration_calistir


@pytest.fixture
def db(tmp_path):
    """Her test için temiz in-memory DB."""
    d = Database(tmp_path / "test.db")
    migration_calistir(d)
    yield d
    d.close()


class TestDatabase:

    def test_baglanti_acilir(self, tmp_path):
        d = Database(tmp_path / "test.db")
        assert d.path.exists()
        d.close()

    def test_fetchone_yok(self, db):
        sonuc = db.fetchone("SELECT * FROM personel WHERE id='yok'")
        assert sonuc is None

    def test_fetchall_bos(self, db):
        sonuc = db.fetchall("SELECT * FROM personel")
        assert sonuc == []

    def test_insert_fetchone(self, db):
        db.execute(
            "INSERT INTO gorev_yeri (id, ad, sua_hakki) VALUES (?,?,?)",
            ("test-gy-1", "Test Birimi", 1),
        )
        r = db.fetchone("SELECT * FROM gorev_yeri WHERE id=?", ("test-gy-1",))
        assert r is not None
        assert r["ad"] == "Test Birimi"
        assert r["sua_hakki"] == 1

    def test_fetchval(self, db):
        sayac = db.fetchval("SELECT COUNT(*) FROM lookup")
        assert isinstance(sayac, int)
        assert sayac > 0   # Seed data yüklendi

    def test_transaction_commit(self, db):
        with db.transaction():
            db.execute(
                "INSERT INTO gorev_yeri (id, ad) VALUES (?,?)",
                ("tx-1", "TX Birimi"),
            )
        r = db.fetchone("SELECT id FROM gorev_yeri WHERE id=?", ("tx-1",))
        assert r is not None

    def test_transaction_rollback(self, db):
        try:
            with db.transaction():
                db.execute(
                    "INSERT INTO gorev_yeri (id, ad) VALUES (?,?)",
                    ("tx-2", "TX Rollback"),
                )
                raise ValueError("test hatası")
        except ValueError:
            pass
        r = db.fetchone("SELECT id FROM gorev_yeri WHERE id=?", ("tx-2",))
        assert r is None   # Rollback başarılı

    def test_tablo_var_mi(self, db):
        assert db.tablo_var_mi("personel") is True
        assert db.tablo_var_mi("olmayan_tablo") is False

    def test_fk_aktif(self, db):
        """FK ihlali hata vermeli."""
        import sqlite3
        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO personel "
                "(id, tc_kimlik, ad, soyad, gorev_yeri_id) "
                "VALUES (?,?,?,?,?)",
                ("p1", "10000000146", "Ali", "Kaya", "olmayan-gy-id"),
            )


class TestMigrations:

    def test_migration_calisiyor(self, tmp_path):
        d = Database(tmp_path / "migration_test.db")
        migration_calistir(d)
        # Temel tablolar oluştu mu?
        for tablo in ("personel", "izin", "muayene", "fhsz",
                      "dozimetre", "nb_plan", "belge", "lookup", "tatil"):
            assert d.tablo_var_mi(tablo), f"{tablo} tablosu oluşmadı"
        d.close()

    def test_tekrar_migration_zarar_vermez(self, tmp_path):
        d = Database(tmp_path / "m2.db")
        migration_calistir(d)
        migration_calistir(d)   # İkinci çalıştırma sorunsuz
        d.close()

    def test_seed_yuklendi(self, db):
        # Lookup seed var mı?
        sayac = db.fetchval(
            "SELECT COUNT(*) FROM lookup WHERE kategori=?", ("izin_tur",)
        )
        assert sayac >= 5

    def test_gorev_yeri_seed(self, db):
        sayac = db.fetchval("SELECT COUNT(*) FROM gorev_yeri")
        assert sayac > 0

    def test_tatil_seed(self, db):
        sayac = db.fetchval("SELECT COUNT(*) FROM tatil")
        assert sayac > 0

    def test_versiyon_kayitlandi(self, db):
        v = db.fetchval("SELECT MAX(versiyon) FROM _db_versiyon")
        assert v == 1
