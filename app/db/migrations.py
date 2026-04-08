# -*- coding: utf-8 -*-
"""
app/db/migrations.py
────────────────────
Versiyonlu migration sistemi.

Her migration:
  - Bir sürüm numarasına karşılık gelir
  - Bir kez çalışır, tekrar çalışmaz
  - İçinde transaction var — yarıda kesilirse geri alınır
  - İdempotent değil (DROP/CREATE — veri kaybı riski)

Kullanım:
    from app.db.migrations import run
    db = Database("radpys.db")
    run(db)   # Gerekli tüm migration'ları uygular
"""
from __future__ import annotations
import logging
from app.db.database import Database

logger = logging.getLogger("radpys.db.migration")

# Hedef şema versiyonu — her migration eklenince artır
HEDEF_VERSIYON = 4


# ══════════════════════════════════════════════════════════════════
#  PUBLIC API
# ══════════════════════════════════════════════════════════════════

def run(db: Database) -> None:
    """
    Gerekli tüm migration'ları sırayla çalıştırır.
    Zaten güncel ise sessizce döner.
    """
    _versiyon_tablosu_olustur(db)
    mevcut = _mevcut_versiyon(db)

    if mevcut >= HEDEF_VERSIYON:
        logger.info(f"DB güncel (v{mevcut}), migration gerek yok.")
        return

    for v in range(mevcut + 1, HEDEF_VERSIYON + 1):
        fn = _MIGRATIONS.get(v)
        if fn is None:
            raise RuntimeError(f"Migration v{v} tanımlı değil")
        logger.info(f"Migration v{v} uygulanıyor…")
        with db.transaction():
            fn(db)
            _versiyon_yaz(db, v)
        logger.info(f"Migration v{v} tamamlandı.")

    logger.info(f"DB v{HEDEF_VERSIYON} sürümüne getirildi.")


# ══════════════════════════════════════════════════════════════════
#  MİGRATİON'LAR
# ══════════════════════════════════════════════════════════════════

def _v1(db: Database) -> None:
    """
    v1 — İlk şema.
    Tüm tablolar, indeksler ve temel seed data.
    """

    # ── Çekirdek tablolar ─────────────────────────────────────────

    db.execute("""
    CREATE TABLE personel (
        id                  TEXT PRIMARY KEY,
        tc_kimlik           TEXT NOT NULL UNIQUE,
        ad                  TEXT NOT NULL,
        soyad               TEXT NOT NULL,
        dogum_tarihi        TEXT,
        dogum_yeri          TEXT,
        hizmet_sinifi       TEXT,
        kadro_unvani        TEXT,
        gorev_yeri_id       TEXT REFERENCES gorev_yeri(id),
        sicil_no            TEXT,
        memuriyet_baslama   TEXT,
        telefon             TEXT,
        e_posta             TEXT,
        fotograf            TEXT,
        durum               TEXT NOT NULL DEFAULT 'aktif'
                                CHECK (durum IN ('aktif','pasif','ayrildi')),
        ayrilik_tarihi      TEXT,
        ayrilik_nedeni      TEXT,
        okul_1              TEXT,
        fakulte_1           TEXT,
        mezuniyet_1         TEXT,
        diploma_no_1        TEXT,
        okul_2              TEXT,
        fakulte_2           TEXT,
        mezuniyet_2         TEXT,
        diploma_no_2        TEXT,
        olusturuldu         TEXT NOT NULL DEFAULT (date('now')),
        guncellendi         TEXT
    )
    """)

    db.execute("""
    CREATE TABLE gorev_yeri (
        id          TEXT PRIMARY KEY,
        ad          TEXT NOT NULL UNIQUE,
        kisaltma    TEXT,
        sua_hakki   INTEGER NOT NULL DEFAULT 0
                        CHECK (sua_hakki IN (0,1)),
        aktif       INTEGER NOT NULL DEFAULT 1
    )
    """)

    db.execute("""
    CREATE TABLE izin (
        id          TEXT PRIMARY KEY,
        personel_id TEXT NOT NULL REFERENCES personel(id),
        tur         TEXT NOT NULL,
        baslama     TEXT NOT NULL,
        gun         INTEGER NOT NULL CHECK (gun > 0),
        bitis       TEXT NOT NULL,
        durum       TEXT NOT NULL DEFAULT 'aktif'
                        CHECK (durum IN ('aktif','iptal')),
        aciklama    TEXT,
        olusturuldu TEXT NOT NULL DEFAULT (date('now'))
    )
    """)

    db.execute("""
    CREATE TABLE muayene (
        id          TEXT PRIMARY KEY,
        personel_id TEXT NOT NULL REFERENCES personel(id),
        uzmanlik    TEXT NOT NULL,
        tarih       TEXT NOT NULL,
        sonraki     TEXT,
        sonuc       TEXT CHECK (sonuc IN
                        ('uygun','uygun_degil','takip',NULL)),
        notlar      TEXT,
        belge_id    TEXT REFERENCES belge(id),
        olusturuldu TEXT NOT NULL DEFAULT (date('now'))
    )
    """)

    db.execute("""
    CREATE TABLE fhsz (
        id              TEXT PRIMARY KEY,
        personel_id     TEXT NOT NULL REFERENCES personel(id),
        yil             INTEGER NOT NULL,
        donem           INTEGER NOT NULL CHECK (donem BETWEEN 1 AND 6),
        aylik_gun       INTEGER,
        izin_gun        INTEGER DEFAULT 0,
        fiili_saat      REAL,
        calisma_kosulu  TEXT,
        notlar          TEXT,
        olusturuldu     TEXT NOT NULL DEFAULT (date('now')),
        UNIQUE (personel_id, yil, donem)
    )
    """)

    db.execute("""
    CREATE TABLE dozimetre (
        id              TEXT PRIMARY KEY,
        personel_id     TEXT NOT NULL REFERENCES personel(id),
        rapor_no        TEXT,
        yil             INTEGER NOT NULL,
        periyot         INTEGER NOT NULL CHECK (periyot BETWEEN 1 AND 4),
        periyot_adi     TEXT,
        dozimetre_no    TEXT,
        tur             TEXT,
        bolge           TEXT,
        hp10            REAL,
        hp007           REAL,
        durum           TEXT,
        olusturuldu     TEXT NOT NULL DEFAULT (date('now')),
        UNIQUE (personel_id, yil, periyot, dozimetre_no)
    )
    """)

    db.execute("""
    CREATE TABLE doz_form (
        id              TEXT PRIMARY KEY,
        dozimetre_id    TEXT NOT NULL REFERENCES dozimetre(id),
        personel_id     TEXT NOT NULL REFERENCES personel(id),
        pdf_yolu        TEXT,
        olusturuldu     TEXT NOT NULL DEFAULT (date('now')),
        UNIQUE (dozimetre_id)
    )
    """)

    # ── Nöbet tabloları ───────────────────────────────────────────

    db.execute("""
    CREATE TABLE nb_birim (
        id          TEXT PRIMARY KEY,
        ad          TEXT NOT NULL UNIQUE,
        kisaltma    TEXT,
        aktif       INTEGER NOT NULL DEFAULT 1
    )
    """)

    db.execute("""
    CREATE TABLE nb_birim_ayar (
        id              TEXT PRIMARY KEY,
        birim_id        TEXT NOT NULL REFERENCES nb_birim(id),
        slot_personel   INTEGER NOT NULL DEFAULT 2,
        max_ardisik_gun INTEGER NOT NULL DEFAULT 3,
        hafta_sonu      INTEGER NOT NULL DEFAULT 1,
        resmi_tatil     INTEGER NOT NULL DEFAULT 1,
        dini_tatil      INTEGER NOT NULL DEFAULT 0,
        gecerli_bastan  TEXT NOT NULL,
        gecerli_bitis   TEXT,
        UNIQUE (birim_id, gecerli_bastan)
    )
    """)

    db.execute("""
    CREATE TABLE nb_vardiya (
        id          TEXT PRIMARY KEY,
        birim_id    TEXT NOT NULL REFERENCES nb_birim(id),
        ad          TEXT NOT NULL,
        saat_suresi REAL NOT NULL,
        ana         INTEGER NOT NULL DEFAULT 1,
        aktif       INTEGER NOT NULL DEFAULT 1
    )
    """)

    db.execute("""
    CREATE TABLE nb_personel (
        id          TEXT PRIMARY KEY,
        birim_id    TEXT NOT NULL REFERENCES nb_birim(id),
        personel_id TEXT NOT NULL REFERENCES personel(id),
        baslama     TEXT NOT NULL,
        bitis       TEXT,
        aktif       INTEGER NOT NULL DEFAULT 1,
        UNIQUE (birim_id, personel_id, baslama)
    )
    """)

    db.execute("""
    CREATE TABLE nb_tercih (
        id              TEXT PRIMARY KEY,
        birim_id        TEXT NOT NULL REFERENCES nb_birim(id),
        personel_id     TEXT NOT NULL REFERENCES personel(id),
        hedef_tipi      TEXT NOT NULL DEFAULT 'normal',
        max_gun         INTEGER,
        tercih_vardiya  TEXT,
        kacin_tarihler  TEXT,
        gecerli_bastan  TEXT NOT NULL,
        gecerli_bitis   TEXT,
        UNIQUE (birim_id, personel_id, gecerli_bastan)
    )
    """)

    db.execute("""
    CREATE TABLE nb_plan (
        id          TEXT PRIMARY KEY,
        birim_id    TEXT NOT NULL REFERENCES nb_birim(id),
        yil         INTEGER NOT NULL,
        ay          INTEGER NOT NULL CHECK (ay BETWEEN 1 AND 12),
        durum       TEXT NOT NULL DEFAULT 'taslak'
                        CHECK (durum IN ('taslak','onaylandi','iptal')),
        notlar      TEXT,
        onaylayan   TEXT,
        olusturuldu TEXT NOT NULL DEFAULT (date('now')),
        UNIQUE (birim_id, yil, ay)
    )
    """)

    db.execute("""
    CREATE TABLE nb_satir (
        id          TEXT PRIMARY KEY,
        plan_id     TEXT NOT NULL REFERENCES nb_plan(id),
        personel_id TEXT NOT NULL REFERENCES personel(id),
        vardiya_id  TEXT NOT NULL REFERENCES nb_vardiya(id),
        tarih       TEXT NOT NULL,
        saat_suresi REAL NOT NULL,
        kaynak      TEXT NOT NULL DEFAULT 'algoritma',
        olusturuldu TEXT NOT NULL DEFAULT (date('now'))
    )
    """)

    # ── Destek tabloları ──────────────────────────────────────────

    db.execute("""
    CREATE TABLE belge (
        id          TEXT PRIMARY KEY,
        entity_turu TEXT NOT NULL,
        entity_id   TEXT NOT NULL,
        tur         TEXT NOT NULL,
        dosya_adi   TEXT NOT NULL,
        lokal_yol   TEXT,
        drive_link  TEXT,
        aciklama    TEXT,
        yuklendi    TEXT NOT NULL DEFAULT (date('now'))
    )
    """)

    db.execute("""
    CREATE TABLE tatil (
        tarih   TEXT PRIMARY KEY,
        ad      TEXT NOT NULL,
        tur     TEXT NOT NULL DEFAULT 'resmi'
                    CHECK (tur IN ('resmi','dini'))
    )
    """)

    db.execute("""
    CREATE TABLE lookup (
        id          TEXT PRIMARY KEY,
        kategori    TEXT NOT NULL,
        deger       TEXT NOT NULL,
        siralama    INTEGER DEFAULT 0,
        aktif       INTEGER NOT NULL DEFAULT 1,
        UNIQUE (kategori, deger)
    )
    """)

    db.execute("""
    CREATE TABLE kullanici (
        id          TEXT PRIMARY KEY,
        ad          TEXT NOT NULL UNIQUE,
        sifre_hash  TEXT NOT NULL,
        personel_id TEXT REFERENCES personel(id),
        rol         TEXT NOT NULL DEFAULT 'kullanici'
                        CHECK (rol IN ('admin','yonetici','kullanici')),
        aktif       INTEGER NOT NULL DEFAULT 1,
        sifre_degismeli INTEGER NOT NULL DEFAULT 1,
        son_giris   TEXT,
        olusturuldu TEXT NOT NULL DEFAULT (date('now'))
    )
    """)

    # ── İndeksler ─────────────────────────────────────────────────

    indeksler = [
        "CREATE INDEX idx_personel_tc      ON personel(tc_kimlik)",
        "CREATE INDEX idx_personel_durum   ON personel(durum)",
        "CREATE INDEX idx_izin_personel    ON izin(personel_id)",
        "CREATE INDEX idx_izin_baslama     ON izin(baslama)",
        "CREATE INDEX idx_izin_durum       ON izin(durum)",
        "CREATE INDEX idx_muayene_personel ON muayene(personel_id)",
        "CREATE INDEX idx_muayene_sonraki  ON muayene(sonraki)",
        "CREATE INDEX idx_doz_personel     ON dozimetre(personel_id)",
        "CREATE INDEX idx_fhsz_personel    ON fhsz(personel_id)",
        "CREATE INDEX idx_satir_plan       ON nb_satir(plan_id)",
        "CREATE INDEX idx_satir_personel   ON nb_satir(personel_id)",
        "CREATE INDEX idx_satir_tarih      ON nb_satir(tarih)",
        "CREATE INDEX idx_belge_entity     ON belge(entity_turu, entity_id)",
    ]
    for sql in indeksler:
        db.execute(sql)

    logger.info("v1: Tüm tablolar ve indeksler oluşturuldu.")

    # Seed data'yı ayrı fonksiyon çalıştırır
    from app.db.seed import seed_all
    seed_all(db)


# ── Migration kaydı ───────────────────────────────────────────────

_TUM_MODULLER = [
    "dashboard", "personel", "izin", "saglik", "dozimetre",
    "cihaz", "ariza", "bakim", "rke", "nobet", "mesai",
    "dokumanlar", "kullanici_giris", "rapor", "ayarlar",
]

_VARSAYILAN_MODUL_IZINLERI: dict[str, set[str] | None] = {
    "admin": None,  # None = tüm modüller
    "yonetici": {
        "dashboard", "personel", "izin", "saglik", "dozimetre",
        "cihaz", "ariza", "bakim", "rke", "nobet", "mesai",
        "dokumanlar", "rapor", "kullanici_giris",
    },
    "kullanici": {"dashboard", "personel", "dokumanlar"},
}


def _v2(db: Database) -> None:
    """v2 — Kullanıcı seed backfill + rbac_modul_izin tablosu."""

    # Mevcut DB'ye eksik kullanıcıları ekle (idempotent)
    from app.db.seed import seed_kullanicilar
    seed_kullanicilar(db)

    db.execute("""
    CREATE TABLE IF NOT EXISTS rbac_modul_izin (
        id        TEXT PRIMARY KEY,
        rol       TEXT NOT NULL,
        modul_id  TEXT NOT NULL,
        izinli    INTEGER NOT NULL DEFAULT 1,
        UNIQUE(rol, modul_id)
    )
    """)
    db.execute(
        "CREATE INDEX IF NOT EXISTS idx_rbac_rol_modul "
        "ON rbac_modul_izin(rol, modul_id)"
    )
    _rbac_modul_izin_seed(db)
    logger.info("v2: rbac_modul_izin tablosu oluşturuldu ve seed edildi.")


def _v3(db: Database) -> None:
    """v3 — İlk girişte şifre değişimi için kullanici.sifre_degismeli alanı."""
    if not _kolon_var_mi(db, "kullanici", "sifre_degismeli"):
        db.execute(
            "ALTER TABLE kullanici "
            "ADD COLUMN sifre_degismeli INTEGER NOT NULL DEFAULT 1"
        )

    # Daha önce giriş yapmış kullanıcıları zorlamayalım.
    db.execute(
        "UPDATE kullanici "
        "SET sifre_degismeli = CASE WHEN son_giris IS NULL THEN 1 ELSE 0 END"
    )
    logger.info("v3: kullanici.sifre_degismeli alanı hazırlandı.")


def _v4(db: Database) -> None:
    """v4 — kullanici.rol alanındaki sabit CHECK kısıtını kaldırır."""
    sql = db.fetchval(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='kullanici'"
    ) or ""
    if "CHECK (rol IN ('admin','yonetici','kullanici'))" not in str(sql):
        logger.info("v4: kullanici tablosu zaten dinamik rol destekli.")
        return

    db.execute("""
    CREATE TABLE kullanici_yeni (
        id          TEXT PRIMARY KEY,
        ad          TEXT NOT NULL UNIQUE,
        sifre_hash  TEXT NOT NULL,
        personel_id TEXT REFERENCES personel(id),
        rol         TEXT NOT NULL DEFAULT 'kullanici',
        aktif       INTEGER NOT NULL DEFAULT 1,
        sifre_degismeli INTEGER NOT NULL DEFAULT 1,
        son_giris   TEXT,
        olusturuldu TEXT NOT NULL DEFAULT (date('now'))
    )
    """)

    db.execute(
        "INSERT INTO kullanici_yeni ("
        "id, ad, sifre_hash, personel_id, rol, aktif, sifre_degismeli, son_giris, olusturuldu"
        ") "
        "SELECT "
        "id, ad, sifre_hash, personel_id, rol, aktif, COALESCE(sifre_degismeli, 1), son_giris, olusturuldu "
        "FROM kullanici"
    )

    db.execute("DROP TABLE kullanici")
    db.execute("ALTER TABLE kullanici_yeni RENAME TO kullanici")
    logger.info("v4: kullanici tablosu dinamik rol desteği için yeniden oluşturuldu.")


def _rbac_modul_izin_seed(db: Database) -> None:
    from uuid import uuid4
    for rol_adi, izinler in _VARSAYILAN_MODUL_IZINLERI.items():
        for modul_id in _TUM_MODULLER:
            if db.fetchval(
                "SELECT 1 FROM rbac_modul_izin WHERE rol=? AND modul_id=?",
                (rol_adi, modul_id),
            ):
                continue  # Zaten var
            izinli = 1 if (izinler is None or modul_id in izinler) else 0
            db.execute(
                "INSERT INTO rbac_modul_izin (id, rol, modul_id, izinli) "
                "VALUES (?,?,?,?)",
                (uuid4().hex, rol_adi, modul_id, izinli),
            )


# ── Migration kaydı ───────────────────────────────────────────────

_MIGRATIONS = {1: _v1, 2: _v2, 3: _v3, 4: _v4}   # Yeni migration eklenince buraya da ekle


# ══════════════════════════════════════════════════════════════════
#  YARDIMCI FONKSİYONLAR
# ══════════════════════════════════════════════════════════════════

def _versiyon_tablosu_olustur(db: Database) -> None:
    db.execute("""
    CREATE TABLE IF NOT EXISTS _db_versiyon (
        id          INTEGER PRIMARY KEY,
        versiyon    INTEGER NOT NULL,
        tarih       TEXT NOT NULL DEFAULT (datetime('now','localtime')),
        aciklama    TEXT
    )
    """)


def _mevcut_versiyon(db: Database) -> int:
    v = db.fetchval("SELECT MAX(versiyon) FROM _db_versiyon")
    return int(v) if v else 0


def _versiyon_yaz(db: Database, versiyon: int) -> None:
    db.execute(
        "INSERT INTO _db_versiyon (versiyon, aciklama) VALUES (?, ?)",
        (versiyon, f"Migration v{versiyon} uygulandı"),
    )


def _kolon_var_mi(db: Database, tablo: str, kolon: str) -> bool:
    """Tabloda kolon varlığını kontrol eder."""
    rows = db.fetchall(f"PRAGMA table_info({tablo})")
    return any(str(r.get("name") or "") == kolon for r in rows)
