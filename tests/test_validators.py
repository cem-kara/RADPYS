# -*- coding: utf-8 -*-
"""tests/test_validators.py — Validator testleri"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.validators import (
    tc_dogrula, tc_dogrula_veya_hata,
    parse_tarih, format_tarih, bitis_hesapla, is_gunu_say,
    zorunlu, pozitif_sayi, to_float, to_int,
    email_dogrula, telefon_dogrula, bos_degil,
    uzunluk_dogrula, sayisal_dogrula, alfasayisal_dogrula,
    tarih_format_dogrula,
)
from app.exceptions import TCHatasi, DogrulamaHatasi


# ── TC ────────────────────────────────────────────────────────────

class TestTCDogrula:

    def test_gecerli_tc(self):
        assert tc_dogrula("10000000146") is True

    def test_gecerli_tc_2(self):
        assert tc_dogrula("14522068356") is True

    def test_kisa_tc(self):
        assert tc_dogrula("1234567890") is False

    def test_uzun_tc(self):
        assert tc_dogrula("123456789012") is False

    def test_bos_tc(self):
        assert tc_dogrula("") is False
        assert tc_dogrula(None) is False

    def test_ilk_rakam_sifir(self):
        assert tc_dogrula("01234567890") is False

    def test_harf_iceren(self):
        assert tc_dogrula("1234567890A") is False

    def test_tamami_sifir(self):
        assert tc_dogrula("00000000000") is False

    def test_veya_hata_gecerli(self):
        assert tc_dogrula_veya_hata("10000000146") == "10000000146"

    def test_veya_hata_gecersiz(self):
        with pytest.raises(TCHatasi):
            tc_dogrula_veya_hata("12345678900")


# ── Tarih ─────────────────────────────────────────────────────────

class TestTarih:

    def test_iso_parse(self):
        t = parse_tarih("2026-01-15")
        assert t.year == 2026
        assert t.month == 1
        assert t.day == 15

    def test_turkce_parse(self):
        t = parse_tarih("15.01.2026")
        assert t.year == 2026 and t.day == 15

    def test_none_parse(self):
        assert parse_tarih(None) is None
        assert parse_tarih("") is None

    def test_gecersiz_parse(self):
        assert parse_tarih("geçersiz-tarih") is None

    def test_format_iso(self):
        from datetime import date
        assert format_tarih(date(2026, 1, 15)) == "2026-01-15"

    def test_format_ui(self):
        from datetime import date
        assert format_tarih(date(2026, 1, 15), ui=True) == "15.01.2026"

    def test_format_none(self):
        assert format_tarih(None) == ""

    def test_bitis_hesapla_1_gun(self):
        assert bitis_hesapla("2026-01-15", 1) == "2026-01-15"

    def test_bitis_hesapla_5_gun(self):
        assert bitis_hesapla("2026-01-15", 5) == "2026-01-19"

    def test_is_gunu_say_hafta_ici(self):
        # 2026-01-19 Pazartesi, 2026-01-23 Cuma → 5 iş günü
        assert is_gunu_say("2026-01-19", "2026-01-23") == 5

    def test_is_gunu_say_hafta_sonu_haric(self):
        # Pazartesi-Pazar → 5 iş günü
        assert is_gunu_say("2026-01-19", "2026-01-25") == 5

    def test_is_gunu_say_tatil_haric(self):
        # 1 gün, tatil günü
        tatiller = {"2026-01-19"}
        assert is_gunu_say("2026-01-19", "2026-01-19", tatiller) == 0


# ── Genel Doğrulayıcılar ─────────────────────────────────────────

class TestGenel:

    def test_zorunlu_dolu(self):
        assert zorunlu("Ali", "Ad") == "Ali"
        assert zorunlu("  Ali  ", "Ad") == "Ali"

    def test_zorunlu_bos(self):
        with pytest.raises(DogrulamaHatasi):
            zorunlu("", "Ad")
        with pytest.raises(DogrulamaHatasi):
            zorunlu("   ", "Ad")
        with pytest.raises(DogrulamaHatasi):
            zorunlu(None, "Ad")

    def test_pozitif_sayi(self):
        assert pozitif_sayi(5, "Gün") == 5
        assert pozitif_sayi("10", "Gün") == 10

    def test_pozitif_sayi_sifir(self):
        with pytest.raises(DogrulamaHatasi):
            pozitif_sayi(0, "Gün")

    def test_pozitif_sayi_negatif(self):
        with pytest.raises(DogrulamaHatasi):
            pozitif_sayi(-1, "Gün")

    def test_to_float(self):
        assert to_float("3.14") == pytest.approx(3.14)
        assert to_float("3,14") == pytest.approx(3.14)
        assert to_float(None)   == 0.0
        assert to_float("")     == 0.0
        assert to_float("abc")  == 0.0

    def test_to_int(self):
        assert to_int("5")  == 5
        assert to_int(None) == 0
        assert to_int("")   == 0


class TestEkDogrulayicilar:

    def test_email_dogrula(self):
        assert email_dogrula("test@example.com") is True
        assert email_dogrula("") is True
        assert email_dogrula("gecersiz-email") is False

    def test_telefon_dogrula(self):
        assert telefon_dogrula("05551234567") is True
        assert telefon_dogrula("5551234567") is True
        assert telefon_dogrula("123456") is False

    def test_bos_degil(self):
        assert bos_degil("Ali") is True
        assert bos_degil("   ") is False
        assert bos_degil(None) is False

    def test_uzunluk_dogrula(self):
        assert uzunluk_dogrula("abc", min_uzunluk=2, max_uzunluk=4) is True
        assert uzunluk_dogrula("a", min_uzunluk=2) is False
        assert uzunluk_dogrula("abcde", max_uzunluk=4) is False

    def test_sayisal_dogrula(self):
        assert sayisal_dogrula("12345") is True
        assert sayisal_dogrula("") is True
        assert sayisal_dogrula("12a45") is False

    def test_alfasayisal_dogrula(self):
        assert alfasayisal_dogrula("Ali Veli 123") is True
        assert alfasayisal_dogrula("") is True
        assert alfasayisal_dogrula("Ali-Veli") is False

    def test_tarih_format_dogrula(self):
        assert tarih_format_dogrula("15.01.2026") is True
        assert tarih_format_dogrula("") is True
        assert tarih_format_dogrula("2026-01-15") is False
