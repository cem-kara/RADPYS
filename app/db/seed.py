# -*- coding: utf-8 -*-
"""
app/db/seed.py
──────────────
Başlangıç verileri (lookup, gorev_yeri, tatiller).
Sadece INSERT OR IGNORE — mevcut veri korunur.
"""
from __future__ import annotations
from uuid import uuid4
from app.db.database import Database
import logging

logger = logging.getLogger("radpys.db.seed")


def seed_all(db: Database) -> None:
    """Tüm seed fonksiyonlarını çalıştırır."""
    _seed_gorev_yerleri(db)
    _seed_lookup(db)
    _seed_tatiller(db)
    seed_kullanicilar(db)
    logger.info("Seed data yüklendi.")


def seed_kullanicilar(db: Database) -> None:
    """Varsayılan kullanıcıları ekler (INSERT OR IGNORE)."""
    import bcrypt
    from uuid import uuid4

    kullanicilar = [
        ("admin",     "admin123",     "admin"),
        ("yonetici",  "yonetici123",  "yonetici"),
        ("kullanici", "kullanici123", "kullanici"),
    ]
    for ad, parola, rol_adi in kullanicilar:
        if not db.fetchval("SELECT 1 FROM kullanici WHERE ad=?", (ad,)):
            sifre_hash = bcrypt.hashpw(parola.encode(), bcrypt.gensalt()).decode()
            db.execute(
                "INSERT INTO kullanici (id, ad, sifre_hash, rol, aktif) "
                "VALUES (?,?,?,?,?)",
                (uuid4().hex, ad, sifre_hash, rol_adi, 1),
            )
    logger.info("Varsayılan kullanıcılar seed edildi.")


# ── Görev Yerleri ─────────────────────────────────────────────────

def _seed_gorev_yerleri(db: Database) -> None:
    yerler = [
        # (ad, kisaltma, sua_hakki)
        # Koşul A → sua_hakki=1 (Radyasyonlu çalışma alanı)
        ("Acil Radyoloji",                   "ARAD",  1),
        ("Anjiografi",                        "ANJ",   1),
        ("Girişimsel Radyoloji",              "RANI",  1),
        ("Koroner Anjiografi",                "KANJ",  1),
        ("Nöroradyoloji Anjiografi",          "NANJ",  1),
        ("Mamografi",                         "MAM",   1),
        ("Manyetik Rezonans Ünitesi",         "MRI",   1),
        ("Radyoloji USG",                     "USG",   1),
        ("Tomografi",                         "CT",    1),
        ("Ameliyathane",                      "AML",   1),
        ("Poliklinik",                        "POL",   1),
        # Koşul B → sua_hakki=0
        ("Gögüs Hastalıkları Yerleşkesi",    "GH",    0),
        ("Esnaf Hastanesi Yerleşkesi",        "ESN",   0),
        ("Yoğun Bakım Ünitesi",              "YBU",   1),
        ("Endoskopi Ünitesi",                "ENU",   0),
        ("Idari",                             "IDR",   0),
    ]
    for ad, kis, sua in yerler:
        db.execute(
            "INSERT OR IGNORE INTO gorev_yeri (id, ad, kisaltma, sua_hakki) "
            "VALUES (?,?,?,?)",
            (uuid4().hex, ad, kis, sua),
        )


# ── Lookup Verileri ───────────────────────────────────────────────

def _seed_lookup(db: Database) -> None:

    def ekle(kategori: str, degerler: list[str]):
        for i, deger in enumerate(degerler):
            db.execute(
                "INSERT OR IGNORE INTO lookup (id, kategori, deger, siralama) "
                "VALUES (?,?,?,?)",
                (uuid4().hex, kategori, deger, i),
            )

    # İzin türleri
    ekle("izin_tur", [
        "Yıllık İzin",
        "Şua İzni",
        "Hastalık Raporu",
        "Mazeret İzni",
        "Ücretsiz İzin",
        "Aylıksız İzin",
        "Doğum İzni",
        "Babalık İzni",
        "Evlilik İzni",
        "Ölüm İzni",
    ])

    # Hizmet sınıfları
    ekle("hizmet_sinifi", [
        "Akademik Personel",
        "Asistan Doktor",
        "Hemşire",
        "Radyasyon Görevlisi",
        "İdari Personel",
        "Diğer",
    ])

    # Kadro unvanları
    ekle("kadro_unvani", [
        "Profesör Doktor",
        "Doçent Doktor",
        "Doktor Öğretim Üyesi",
        "Uzman Doktor",
        "Araştırma Görevlisi",
        "Asistan Doktor",
        "Radyoloji Teknikeri",
        "Radyoloji Teknisyeni",
        "Teknisyen",
        "Hemşire",
        "Sağlık Memuru",
        "Sağlık Teknikeri",
        "Sağlık Teknisyeni",
        "Ebe",
        "İdari Personel",
        "Diğer",
    ])

    # Muayene uzmanlıkları
    ekle("uzmanlik", [
        "Genel",
        "Dermatoloji",
        "Dahiliye",
        "Göz",
        "Görüntüleme",
        "Diğer",
    ])

    # Belge türleri
    ekle("belge_tur", [
        "Diploma",
        "Sertifika",
        "Periyodik Muayene Raporu",
        "İşe Giriş Muayenesi",
        "Hastalık Raporu",
        "Dozimetre Sonuçları",
        "Doz Araştırma Formu",
        "NDK Lisansı",
        "Diğer",
    ])

    # Nöbet hedef tipleri
    ekle("nobet_hedef_tipi", [
        "normal",
        "gonullu",
        "rapor",
        "muaf",
    ])

    # Dozimetre türleri
    ekle("dozimetre_tur", [
        "TLD",
        "OSL",
        "Nötron",
        "Elektronik",
    ])

    # Vücut bölgeleri (dozimetre)
    ekle("vucut_bolgesi", [
        "Tüm Vücut Göğüs (Önlük Altı)",
        "Tüm Vücut Göğüs (Önlük Üstü)",
        "El / Bilek",
        "Göz",
        "Yaka",
    ])


# ── Tatiller ──────────────────────────────────────────────────────

def _seed_tatiller(db: Database) -> None:
    tatiller = [
        # 2026
        ("2026-01-01", "Yılbaşı",                          "resmi"),
        ("2026-04-23", "Ulusal Egemenlik ve Çocuk Bayramı", "resmi"),
        ("2026-05-01", "Emek ve Dayanışma Günü",            "resmi"),
        ("2026-05-19", "Atatürk'ü Anma, Gençlik Bayramı",  "resmi"),
        ("2026-07-15", "Demokrasi ve Milli Birlik Günü",    "resmi"),
        ("2026-08-30", "Zafer Bayramı",                     "resmi"),
        ("2026-10-29", "Cumhuriyet Bayramı",                "resmi"),
        # 2025
        ("2025-01-01", "Yılbaşı",                          "resmi"),
        ("2025-04-23", "Ulusal Egemenlik ve Çocuk Bayramı", "resmi"),
        ("2025-05-01", "Emek ve Dayanışma Günü",            "resmi"),
        ("2025-05-19", "Atatürk'ü Anma, Gençlik Bayramı",  "resmi"),
        ("2025-07-15", "Demokrasi ve Milli Birlik Günü",    "resmi"),
        ("2025-08-30", "Zafer Bayramı",                     "resmi"),
        ("2025-10-29", "Cumhuriyet Bayramı",                "resmi"),
    ]
    for tarih, ad, tur in tatiller:
        db.execute(
            "INSERT OR IGNORE INTO tatil (tarih, ad, tur) VALUES (?,?,?)",
            (tarih, ad, tur),
        )
