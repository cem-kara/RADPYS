# -*- coding: utf-8 -*-
"""
app/config.py
─────────────
Uygulama genelinde sabitler.
Tüm iş kuralı sabitleri burada — servis dosyalarına dağıtılmaz.
"""
from __future__ import annotations
from pathlib import Path

# ── Dizinler ──────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent.parent
DATA_DIR    = BASE_DIR / "data"
LOG_DIR     = BASE_DIR / "logs"
BELGE_DIR   = DATA_DIR / "belgeler"
DB_PATH     = DATA_DIR / "radpys.db"

# Uygulama açılışında oluşturulacak dizinler
ZORUNLU_DIZINLER = [DATA_DIR, LOG_DIR, BELGE_DIR]

# ── Uygulama Bilgisi ──────────────────────────────────────────────
APP_ADI      = "RADPYS"
APP_SURUM    = "2.0.0"
APP_BASLIK   = f"{APP_ADI} v{APP_SURUM}"

# ── İzin İş Kuralları (657 Sayılı Kanun) ─────────────────────────
YILLIK_HAK_1_10  = 20.0   # 1–10 yıl hizmet → 20 gün
YILLIK_HAK_10P   = 30.0   # 10 yıl üzeri → 30 gün
YILLIK_MAX_DEVIR = 2.0    # Devir katsayısı: kalan × 2 (657 SK md.102)
PASIF_MIN_GUN    = 30     # Bu gün sayısının üstündeki izinler personeli pasif yapar
PASIF_TIPLER     = {"ucretsiz", "ayliksiz"}  # Bu türler de pasif yapar
SUA_HAK_GUN      = 30.0   # Koşul A → yıllık şua hakkı (iş günü)

# ── Dozimetre Limitleri (Radyasyon Güvenliği Yönetmeliği) ─────────
HP10_UYARI       = 2.0    # mSv — periyot uyarı eşiği
HP10_TEHLIKE     = 5.0    # mSv — periyot tehlike eşiği
NDK_YILLIK       = 20.0   # mSv — yıllık normal doz kısıtlaması
NDK_BES_YILLIK   = 100.0  # mSv — 5 yıllık kümülatif limit
NDK_CALISMA_A    = 6.0    # mSv — Çalışma Koşulu A yıllık eşiği
DOZIMETRE_MIN_PERIYOT = 1   # Periyot degeri en az 1 olmali
DOZIMETRE_YIL_AY_SAYISI = 12
DOZIMETRE_REFERANS_GUN = 15
TAEK_BILDIRIM_GUN = 30    # Doz aşımında TAEK'e bildirim süresi (gün)

# ── Nöbet Algoritması ─────────────────────────────────────────────
NOBET_GUNLUK_HEDEF_SAAT = 7.0   # Radyoloji standardı iş günü
NOBET_GONULLU_KATSAYI   = 1.2   # Gönüllü personel hedef çarpanı
NOBET_TOLERANS_SAAT     = 7.0   # ±1 slot toleransı

# ── FHSZ ─────────────────────────────────────────────────────────
FHSZ_DONEM_SAYISI = 12   # Yılda 12 dönem (1'er aylık)

# ── Lookup Kategorileri ───────────────────────────────────────────
class LookupKategori:
    IZIN_TUR       = "izin_tur"
    HIZMET_SINIFI  = "hizmet_sinifi"
    KADRO_UNVANI   = "kadro_unvani"
    UZMANLIK       = "uzmanlik"
    BELGE_TUR      = "belge_tur"
    NOBET_HEDEF    = "nobet_hedef_tipi"


class LookupPolitika:
    STRICT = "strict"
    REVIEW = "review"
    PERMISSIVE = "permissive"


LOOKUP_DOGRULAMA_POLITIKALARI: dict[str, str] = {
    LookupKategori.IZIN_TUR: LookupPolitika.STRICT,
    LookupKategori.HIZMET_SINIFI: LookupPolitika.STRICT,
    LookupKategori.KADRO_UNVANI: LookupPolitika.STRICT,
    LookupKategori.UZMANLIK: LookupPolitika.STRICT,
    LookupKategori.BELGE_TUR: LookupPolitika.STRICT,
    LookupKategori.NOBET_HEDEF: LookupPolitika.STRICT,
}

# ── RBAC ──────────────────────────────────────────────────────────
RBAC_ROLLER: tuple[str, ...] = ("admin", "yonetici", "kullanici", "operator")

RBAC_ROL_YETKILERI: dict[str, set] = {
    "admin": {
        "personel.ekle",
        "personel.guncelle",
        "personel.pasife_al",
        "kullanici.goruntule",
        "kullanici.olustur",
        "kullanici.guncelle",
        "kullanici.pasife_al",
    },
    "yonetici": {
        "personel.ekle",
        "personel.guncelle",
        "kullanici.goruntule",
        "kullanici.guncelle",
    },
    "kullanici": set(),
    "operator": set(),
}

# ── Tarih Formatı ─────────────────────────────────────────────────
TARIH_FORMAT = "%Y-%m-%d"   # ISO-8601, veritabanında kullanılan format
TARIH_UI     = "%d.%m.%Y"   # Kullanıcıya gösterilen format

# ── Logging ───────────────────────────────────────────────────────
LOG_MAX_BYTES        = 10 * 1024 * 1024
LOG_BACKUP_COUNT     = 5
LOG_CLEANUP_DAYS     = 7
LOG_MAX_TOTAL_MB     = 100
LOG_WARN_FILE_MB     = 8
LOG_WARN_TOTAL_MB    = 80
