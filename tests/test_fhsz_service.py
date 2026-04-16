# -*- coding: utf-8 -*-
"""tests/test_fhsz_service.py"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import Database
from app.db.migrations import run as migrate
from app.services.fhsz_service import FhszService
from app.services.personel_service import PersonelService
from app.validators import is_gunu_say


def test_puantaj_rapor_kumulatif_hesap(tmp_path):
    db = Database(tmp_path / "test.db")
    migrate(db)
    try:
        psvc = PersonelService(db)
        fsvc = FhszService(db)

        pid = psvc.ekle(
            {
                "tc_kimlik": "10000000146",
                "ad": "Ali",
                "soyad": "Kaya",
                "memuriyet_baslama": "2018-01-01",
            }
        )

        fsvc.donem_kaydet(
            yil=2026,
            donem=1,
            satirlar=[
                {
                    "personel_id": pid,
                    "calisma_kosulu": "A",
                    "aylik_gun": 20,
                    "izin_gun": 2,
                }
            ],
        )
        fsvc.donem_kaydet(
            yil=2026,
            donem=2,
            satirlar=[
                {
                    "personel_id": pid,
                    "calisma_kosulu": "A",
                    "aylik_gun": 18,
                    "izin_gun": 0,
                }
            ],
        )

        rapor = fsvc.puantaj_rapor_uret(yil=2026)
        assert len(rapor) == 3

        d1 = next(r for r in rapor if r["donem"] == 1)
        d2 = next(r for r in rapor if r["donem"] == 2)
        toplam = next(r for r in rapor if r["donem"] == "Toplam")

        assert d1["fiili_saat"] == 126.0
        assert d1["kumulatif_saat"] == 126.0
        assert d2["fiili_saat"] == 126.0
        assert d2["kumulatif_saat"] == 252.0
        assert toplam["kumulatif_saat"] == 252.0
        assert toplam["sua_hak_edis"] == 6

        tek = fsvc.puantaj_rapor_uret(yil=2026, donem=2)
        assert len(tek) == 1
        assert tek[0]["donem"] == 2
        assert tek[0]["kumulatif_saat"] == 252.0
    finally:
        db.close()


def test_donem_hesapla_esik_oncesi_donem_hata(tmp_path):
    db = Database(tmp_path / "test.db")
    migrate(db)
    try:
        fsvc = FhszService(db)
        with pytest.raises(ValueError):
            fsvc.donem_hesapla(yil=2022, donem=1)
    finally:
        db.close()


def test_donem_hesapla_izin_kesisim_is_gunu(tmp_path):
    db = Database(tmp_path / "test.db")
    migrate(db)
    try:
        psvc = PersonelService(db)
        fsvc = FhszService(db)

        pid = psvc.ekle(
            {
                "tc_kimlik": "10000000146",
                "ad": "Ali",
                "soyad": "Kaya",
                "memuriyet_baslama": "2018-01-01",
                "hizmet_sinifi": "Radyasyon Gorevlisi",
            }
        )

        # Kayitli donem varsa kosul bu kayittan okunur; A olmali.
        fsvc.donem_kaydet(
            yil=2026,
            donem=1,
            satirlar=[
                {
                    "personel_id": pid,
                    "calisma_kosulu": "A",
                    "aylik_gun": 0,
                    "izin_gun": 0,
                }
            ],
        )

        db.execute(
            "INSERT INTO izin (id, personel_id, tur, baslama, gun, bitis, durum) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("izin1", pid, "Yillik Izin", "2026-01-20", 3, "2026-01-22", "aktif"),
        )

        rows = fsvc.donem_hesapla(yil=2026, donem=1)
        assert len(rows) == 1

        row = rows[0]
        assert row["izin_gun"] == 3

        tatiller = db.fetchall(
            "SELECT tarih FROM tatil WHERE tarih BETWEEN ? AND ?",
            ("2026-01-15", "2026-02-14"),
        )
        tatil_seti = {str(r.get("tarih") or "") for r in tatiller if r.get("tarih")}
        beklenen_gun = is_gunu_say("2026-01-15", "2026-02-14", tatiller=tatil_seti)
        assert row["aylik_gun"] == beklenen_gun
        assert row["fiili_saat"] == float(max(0, beklenen_gun - 3) * 7)
    finally:
        db.close()


def test_donem_hesapla_yarim_gun_tatil_duser(tmp_path):
    db = Database(tmp_path / "test.db")
    migrate(db)
    try:
        psvc = PersonelService(db)
        fsvc = FhszService(db)

        pid = psvc.ekle(
            {
                    "tc_kimlik": "10000000146",
                "ad": "Veli",
                "soyad": "Demir",
                "memuriyet_baslama": "2019-01-01",
                "hizmet_sinifi": "Radyasyon Gorevlisi",
            }
        )

        fsvc.donem_kaydet(
            yil=2026,
            donem=1,
            satirlar=[
                {
                    "personel_id": pid,
                    "calisma_kosulu": "A",
                    "aylik_gun": 0,
                    "izin_gun": 0,
                }
            ],
        )

        db.execute("DELETE FROM tatil WHERE tarih=?", ("2026-01-01",))
        db.execute(
            "INSERT INTO tatil (tarih, ad, tur, yarim_gun) VALUES (?,?,?,?)",
            ("2026-01-20", "Arefe", "dini", 1),
        )

        rows = fsvc.donem_hesapla(yil=2026, donem=1)
        assert len(rows) == 1

        row = rows[0]
        tatiller = db.fetchall(
            "SELECT tarih FROM tatil WHERE tarih BETWEEN ? AND ? AND COALESCE(yarim_gun, 0) = 0",
            ("2026-01-15", "2026-02-14"),
        )
        tatil_seti = {str(r.get("tarih") or "") for r in tatiller if r.get("tarih")}
        beklenen_tam_gun = is_gunu_say("2026-01-15", "2026-02-14", tatiller=tatil_seti)

        assert row["aylik_gun"] == float(beklenen_tam_gun) - 0.5
        assert row["fiili_saat"] == (float(beklenen_tam_gun) - 0.5) * 7.0
    finally:
        db.close()


def test_donem_hesapla_birim_gecmisinden_kosul_belirler(tmp_path):
    db = Database(tmp_path / "test.db")
    migrate(db)
    try:
        psvc = PersonelService(db)
        fsvc = FhszService(db)

        gy_a = db.fetchone("SELECT id, ad FROM gorev_yeri WHERE sua_hakki = 1 ORDER BY ad LIMIT 1")
        gy_b = db.fetchone("SELECT id, ad FROM gorev_yeri WHERE sua_hakki = 0 ORDER BY ad LIMIT 1")
        assert gy_a is not None and gy_b is not None

        pid = psvc.ekle(
            {
                "tc_kimlik": "14522068356",
                "ad": "Veli",
                "soyad": "Kaya",
                "memuriyet_baslama": "2020-01-01",
                "hizmet_sinifi": "Radyasyon Gorevlisi",
                "gorev_yeri_id": gy_b["id"],
            }
        )

        # Donem baslangici 2026-01-15 oldugu icin bu tarihte gorev yeri A olmali.
        db.execute(
            "UPDATE personel_gorev_gecmis SET bitis_tarihi=? WHERE personel_id=? AND bitis_tarihi IS NULL",
            ("2026-01-14", pid),
        )
        db.execute(
            "INSERT INTO personel_gorev_gecmis "
            "(id, personel_id, gorev_yeri_id, baslama_tarihi, aciklama) "
            "VALUES (?,?,?,?,?)",
            ("gh1", pid, gy_a["id"], "2026-01-15", "Test gecis"),
        )

        rows = fsvc.donem_hesapla(yil=2026, donem=1)
        row = next(r for r in rows if r["personel_id"] == pid)

        assert row["calisma_kosulu"] == "A"
        assert row["gorev_yeri"] == gy_a["ad"]
        assert row["fiili_saat"] > 0
    finally:
        db.close()
