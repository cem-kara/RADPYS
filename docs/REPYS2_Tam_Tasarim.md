# REPYS 2.0 — Tam Tasarım Belgesi
## Geriye uyumluluk yok. Her şey sıfırdan.

---

## ESKİDE NEYİ YANLIŞ YAPTIK

Eski kodu yazarken bizi kısıtlayan kalıplar — bunların hiçbiri yeni kodda olmayacak:

| Eski Kalıp | Sorun | Yeni Yaklaşım |
|---|---|---|
| `setProperty("style-role", "action")` | 1263 yerde, QSS runtime parse, hata ayırlanamaz | Python'dan direkt stil metodu |
| `SonucYonetici` | Her servis metodunda `if sonuc.basarili:` wrapper | Exception fırlatır, try/except kullanılır |
| `RepositoryRegistry` | Tablo adı string ile arama (`_r.get("Personel")`) | Her servis kendi repo'sunu direkt import eder |
| `table_config.py` | 477 satır meta tanımı, her tablo için elle bakım | Repo class'ı şemayı bilir |
| 20+ farklı `_Loader(QThread)` | Her sayfada aynı kodu yeniden yaz | Tek generic `AsyncRunner` |
| `QMessageBox` yasak ama `MesajKutusu` import yükü | Dialog için 3 katmanlı soyutlama | Direkt Qt dialog veya native |
| 1121 satır QSS template + placeholder replace | Runtime string manipülasyonu | Compile-time CSS sabitleri |
| `get_personel_listesi` 4 serviste kopya | DRY ihlali | Mixin veya shared utility |
| `Izin_Bilgi` mutation | Bakiye tutarsız kalır | Hesaplama, asla saklama |
| `di.py` factory fonksiyonları | Her servis için elle `get_xxx_service(db)` yaz | Constructor injection |

---

## 1. MİMARİ

### 1.1 Katmanlar

```
┌─────────────────────────────────────────┐
│  UI Layer                               │
│  QWidget subclass'ları                  │
│  Sadece görüntüleme + kullanıcı girişi  │
│  Servis metodlarını çağırır             │
├─────────────────────────────────────────┤
│  Service Layer                          │
│  İş kuralları burada                    │
│  Exception fırlatır                     │
│  Repository'leri çağırır               │
├─────────────────────────────────────────┤
│  Repository Layer                       │
│  Ham SQL — iş mantığı yok              │
│  Tek sorumluluk: DB okuma/yazma        │
├─────────────────────────────────────────┤
│  SQLite 3.40+                           │
│  WAL mode, FK aktif                     │
└─────────────────────────────────────────┘
```

### 1.2 Bağımlılık akışı

```python
# Her şey constructor'da inject edilir — di.py yok

# Uygulama açılışında:
db   = Database("repys.db")
svc  = PersonelService(db)
page = PersonelPage(svc)

# Servis doğrudan repo'yu çağırır:
class PersonelService:
    def __init__(self, db: Database):
        self._repo = PersonelRepo(db)

# Test edilebilirlik:
mock_db = MockDatabase()
svc     = PersonelService(mock_db)  # bağımlılık dışarıdan
```

---

## 2. VERİTABANI

### 2.1 Database sınıfı

```python
# db/database.py
import sqlite3
from pathlib import Path
from contextlib import contextmanager

class Database:
    """
    Uygulama genelinde tek DB bağlantısı.
    WAL mode + FK aktif.
    Context manager ile transaction desteği.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._conn = sqlite3.connect(
            str(self.path),
            check_same_thread=False,
            timeout=30,
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.execute("PRAGMA synchronous=NORMAL")

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        cur = self._conn.execute(sql, params)
        if not sql.strip().upper().startswith("SELECT"):
            self._conn.commit()
        return cur

    def fetchall(self, sql: str, params: tuple = ()) -> list[dict]:
        return [dict(r) for r in self._conn.execute(sql, params).fetchall()]

    def fetchone(self, sql: str, params: tuple = ()) -> dict | None:
        r = self._conn.execute(sql, params).fetchone()
        return dict(r) if r else None

    @contextmanager
    def transaction(self):
        """Birden fazla yazma işlemi atomik olsun."""
        try:
            self._conn.execute("BEGIN")
            yield self
            self._conn.execute("COMMIT")
        except Exception:
            self._conn.execute("ROLLBACK")
            raise

    def close(self):
        self._conn.close()
```

### 2.2 Repository Base

```python
# db/base_repo.py
from dataclasses import dataclass
from typing import TypeVar, Generic
from uuid import uuid4

T = TypeVar("T")

class BaseRepo:
    """
    Minimal base — SQL string'leri subclass'ta.
    Generic metod yok, her sorgu açıkça yazılır.
    """

    def __init__(self, db: Database):
        self._db = db

    def _new_id(self) -> str:
        return uuid4().hex
```

### 2.3 Tablo Şeması — Tam Liste

```sql
-- ═══════════════════════════════════════
--  ÇEKIRDEK TABLOLAR
-- ═══════════════════════════════════════

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
    memuriyet_baslama   TEXT,      -- yıllık hak hesabı için
    telefon             TEXT,
    e_posta             TEXT,
    fotograf            TEXT,      -- lokal dosya yolu
    durum               TEXT NOT NULL DEFAULT 'aktif'
                            CHECK (durum IN ('aktif','pasif','ayrildi')),
    ayrilik_tarihi      TEXT,
    ayrilik_nedeni      TEXT,
    -- Eğitim
    okul_1              TEXT,
    fakulte_1           TEXT,
    mezuniyet_1         TEXT,
    diploma_no_1        TEXT,
    okul_2              TEXT,
    fakulte_2           TEXT,
    mezuniyet_2         TEXT,
    diploma_no_2        TEXT,
    -- Meta
    olusturuldu         TEXT NOT NULL DEFAULT (date('now')),
    guncellendi         TEXT
);

CREATE TABLE gorev_yeri (
    id              TEXT PRIMARY KEY,
    ad              TEXT NOT NULL UNIQUE,
    kisaltma        TEXT,
    sua_hakki       INTEGER NOT NULL DEFAULT 0,
    -- 1 = Koşul A (30 iş günü şua), 0 = Koşul B (şua yok)
    aktif           INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE izin (
    id              TEXT PRIMARY KEY,
    personel_id     TEXT NOT NULL REFERENCES personel(id),
    tur             TEXT NOT NULL,
    -- 'yillik' | 'sua' | 'ucretsiz' | 'ayliksiz'
    -- | 'rapor' | 'mazeret' | 'dogum' | 'olum' | 'evlilik' | 'baba'
    baslama         TEXT NOT NULL,
    gun             INTEGER NOT NULL CHECK (gun > 0),
    bitis           TEXT NOT NULL,
    durum           TEXT NOT NULL DEFAULT 'aktif'
                        CHECK (durum IN ('aktif','iptal')),
    aciklama        TEXT,
    olusturuldu     TEXT NOT NULL DEFAULT (date('now'))
);

CREATE TABLE muayene (
    id              TEXT PRIMARY KEY,
    personel_id     TEXT NOT NULL REFERENCES personel(id),
    uzmanlik        TEXT NOT NULL,
    -- 'genel' | 'dermatoloji' | 'dahiliye' | 'goz' | 'goruntuleme'
    tarih           TEXT NOT NULL,
    sonraki_tarih   TEXT,
    sonuc           TEXT CHECK (sonuc IN ('uygun','uygun_degil','takip', NULL)),
    notlar          TEXT,
    belge_id        TEXT REFERENCES belge(id),
    olusturuldu     TEXT NOT NULL DEFAULT (date('now'))
);

CREATE TABLE fhsz (
    id              TEXT PRIMARY KEY,
    personel_id     TEXT NOT NULL REFERENCES personel(id),
    yil             INTEGER NOT NULL,
    donem           INTEGER NOT NULL CHECK (donem BETWEEN 1 AND 6),
    aylik_gun       INTEGER,
    izin_gun        INTEGER DEFAULT 0,
    fiili_saat      REAL,
    calisma_kosulu  TEXT,   -- anlık snapshot: 'A' veya 'B'
    notlar          TEXT,
    olusturuldu     TEXT NOT NULL DEFAULT (date('now')),
    UNIQUE (personel_id, yil, donem)
);

CREATE TABLE dozimetre (
    id              TEXT PRIMARY KEY,
    personel_id     TEXT NOT NULL REFERENCES personel(id),
    rapor_no        TEXT,
    yil             INTEGER NOT NULL,
    periyot         INTEGER NOT NULL CHECK (periyot BETWEEN 1 AND 4),
    periyot_adi     TEXT,
    dozimetre_no    TEXT,
    tur             TEXT,       -- 'TLD' | 'OSL' | 'Nötron' | 'Elektronik'
    bolge           TEXT,       -- 'Tüm Vücut' | 'El/Bilek' | 'Göz'
    hp10            REAL,       -- mSv — derin doz
    hp007           REAL,       -- mSv — yüzeysel doz
    durum           TEXT,       -- 'normal' | 'asim' | 'iade_edilmedi'
    olusturuldu     TEXT NOT NULL DEFAULT (date('now')),
    UNIQUE (personel_id, yil, periyot, dozimetre_no)
);

CREATE TABLE doz_form (
    id              TEXT PRIMARY KEY,
    dozimetre_id    TEXT NOT NULL REFERENCES dozimetre(id),
    personel_id     TEXT NOT NULL REFERENCES personel(id),
    pdf_yolu        TEXT,
    olusturuldu     TEXT NOT NULL DEFAULT (date('now')),
    UNIQUE (dozimetre_id)
);

-- ═══════════════════════════════════════
--  NÖBET TABLOLARI
-- ═══════════════════════════════════════

CREATE TABLE nb_birim (
    id          TEXT PRIMARY KEY,
    ad          TEXT NOT NULL UNIQUE,
    kisaltma    TEXT,
    aktif       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE nb_birim_ayar (
    id                  TEXT PRIMARY KEY,
    birim_id            TEXT NOT NULL REFERENCES nb_birim(id),
    slot_personel       INTEGER NOT NULL DEFAULT 2,
    max_ardisik_gun     INTEGER NOT NULL DEFAULT 3,
    hafta_sonu          INTEGER NOT NULL DEFAULT 1,
    resmi_tatil         INTEGER NOT NULL DEFAULT 1,
    dini_tatil          INTEGER NOT NULL DEFAULT 0,
    gecerli_bastan      TEXT NOT NULL,
    gecerli_bitis       TEXT,
    UNIQUE (birim_id, gecerli_bastan)
);

CREATE TABLE nb_vardiya (
    id          TEXT PRIMARY KEY,
    birim_id    TEXT NOT NULL REFERENCES nb_birim(id),
    ad          TEXT NOT NULL,      -- 'Gündüz' | 'Gece'
    saat_suresi REAL NOT NULL,
    ana         INTEGER NOT NULL DEFAULT 1,
    aktif       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE nb_personel (
    id          TEXT PRIMARY KEY,
    birim_id    TEXT NOT NULL REFERENCES nb_birim(id),
    personel_id TEXT NOT NULL REFERENCES personel(id),
    baslama     TEXT NOT NULL,
    bitis       TEXT,
    aktif       INTEGER NOT NULL DEFAULT 1,
    UNIQUE (birim_id, personel_id, baslama)
);

CREATE TABLE nb_tercih (
    id              TEXT PRIMARY KEY,
    birim_id        TEXT NOT NULL REFERENCES nb_birim(id),
    personel_id     TEXT NOT NULL REFERENCES personel(id),
    hedef_tipi      TEXT NOT NULL DEFAULT 'normal',
    -- 'normal' | 'gonullu' | 'rapor' | 'muaf'
    max_gun         INTEGER,
    tercih_vardiya  TEXT,   -- JSON: ["Gündüz"]
    kacin_tarihler  TEXT,   -- JSON: ["2026-01-15"]
    gecerli_bastan  TEXT NOT NULL,
    gecerli_bitis   TEXT,
    UNIQUE (birim_id, personel_id, gecerli_bastan)
);

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
);

CREATE TABLE nb_satir (
    id          TEXT PRIMARY KEY,
    plan_id     TEXT NOT NULL REFERENCES nb_plan(id),
    personel_id TEXT NOT NULL REFERENCES personel(id),
    vardiya_id  TEXT NOT NULL REFERENCES nb_vardiya(id),
    tarih       TEXT NOT NULL,
    saat_suresi REAL NOT NULL,
    kaynak      TEXT NOT NULL DEFAULT 'algoritma',
    -- 'algoritma' | 'manuel' | 'degisim'
    olusturuldu TEXT NOT NULL DEFAULT (date('now'))
);

-- ═══════════════════════════════════════
--  DESTEK TABLOLARI
-- ═══════════════════════════════════════

CREATE TABLE belge (
    id              TEXT PRIMARY KEY,
    entity_turu     TEXT NOT NULL,
    -- 'personel' | 'muayene' | 'cihaz' | 'rke'
    entity_id       TEXT NOT NULL,
    tur             TEXT NOT NULL,
    -- 'diploma' | 'rapor' | 'doz_formu' | 'sertifika' | ...
    dosya_adi       TEXT NOT NULL,
    lokal_yol       TEXT,
    drive_link      TEXT,
    aciklama        TEXT,
    yuklendi        TEXT NOT NULL DEFAULT (date('now'))
);

CREATE TABLE tatil (
    tarih   TEXT PRIMARY KEY,       -- YYYY-MM-DD
    ad      TEXT NOT NULL,
    tur     TEXT NOT NULL DEFAULT 'resmi'
                CHECK (tur IN ('resmi','dini'))
);

CREATE TABLE lookup (
    id          TEXT PRIMARY KEY,
    kategori    TEXT NOT NULL,
    deger       TEXT NOT NULL,
    siralama    INTEGER DEFAULT 0,
    aktif       INTEGER NOT NULL DEFAULT 1,
    UNIQUE (kategori, deger)
);

CREATE TABLE kullanici (
    id              TEXT PRIMARY KEY,
    ad              TEXT NOT NULL UNIQUE,
    sifre_hash      TEXT NOT NULL,
    personel_id     TEXT REFERENCES personel(id),
    rol             TEXT NOT NULL DEFAULT 'kullanici'
                        CHECK (rol IN ('admin','yonetici','kullanici')),
    aktif           INTEGER NOT NULL DEFAULT 1,
    son_giris       TEXT,
    olusturuldu     TEXT NOT NULL DEFAULT (date('now'))
);

-- İndeksler
CREATE INDEX idx_izin_personel    ON izin(personel_id);
CREATE INDEX idx_izin_baslama     ON izin(baslama);
CREATE INDEX idx_muayene_personel ON muayene(personel_id);
CREATE INDEX idx_muayene_sonraki  ON muayene(sonraki_tarih);
CREATE INDEX idx_doz_personel     ON dozimetre(personel_id);
CREATE INDEX idx_fhsz_personel    ON fhsz(personel_id);
CREATE INDEX idx_satir_plan       ON nb_satir(plan_id);
CREATE INDEX idx_satir_personel   ON nb_satir(personel_id);
CREATE INDEX idx_satir_tarih      ON nb_satir(tarih);
CREATE INDEX idx_belge_entity     ON belge(entity_turu, entity_id);
```

---

## 3. SERVİS KATMANI

### 3.1 Exception Tasarımı

```python
# app/exceptions.py
class AppHatasi(Exception):
    """Tüm uygulama hatalarının tabanı."""

class DogrulamaHatasi(AppHatasi):
    """Girdi doğrulama hatası — kullanıcıya gösterilir."""

class IsKuraliHatasi(AppHatasi):
    """İş kuralı ihlali — kullanıcıya gösterilir."""

class KayitBulunamadi(AppHatasi):
    """İstenen kayıt DB'de yok."""

class CakismaHatasi(IsKuraliHatasi):
    """Tarih çakışması."""

class LimitHatasi(IsKuraliHatasi):
    """İzin limiti aşıldı."""
```

### 3.2 PersonelService

```python
# app/services/personel_service.py
from app.db.repos.personel_repo import PersonelRepo
from app.exceptions import DogrulamaHatasi, KayitBulunamadi
from app.validators import tc_dogrula

class PersonelService:

    def __init__(self, db):
        self._repo = PersonelRepo(db)

    # ── Sorgular ──────────────────────────────────────────────

    def listele(self, aktif_only: bool = True) -> list[dict]:
        return self._repo.listele(aktif_only=aktif_only)

    def getir(self, personel_id: str) -> dict:
        p = self._repo.getir(personel_id)
        if not p:
            raise KayitBulunamadi(f"Personel bulunamadı: {personel_id}")
        return p

    def tc_ile_getir(self, tc: str) -> dict:
        p = self._repo.tc_ile_getir(tc)
        if not p:
            raise KayitBulunamadi(f"TC bulunamadı: {tc}")
        return p

    # ── Yazma ─────────────────────────────────────────────────

    def ekle(self, veri: dict) -> str:
        """
        Personel ekler, ID döner.
        Raises: DogrulamaHatasi — geçersiz TC
        """
        tc = str(veri.get("tc_kimlik") or "").strip()
        if not tc_dogrula(tc):
            raise DogrulamaHatasi(f"Geçersiz TC Kimlik No: {tc}")
        if self._repo.tc_var_mi(tc):
            raise DogrulamaHatasi(f"Bu TC zaten kayıtlı: {tc}")
        return self._repo.ekle(veri)

    def guncelle(self, personel_id: str, veri: dict) -> None:
        self.getir(personel_id)  # varlık kontrolü
        self._repo.guncelle(personel_id, veri)

    def pasife_al(self, personel_id: str, tarih: str, neden: str) -> None:
        """Silme yok. Personel asla fiziksel olarak silinmez."""
        self._repo.guncelle(personel_id, {
            "durum":          "pasif",
            "ayrilik_tarihi": tarih,
            "ayrilik_nedeni": neden,
        })
```

### 3.3 IzinService

```python
# app/services/izin_service.py
from datetime import date
from app.db.repos.izin_repo import IzinRepo
from app.db.repos.personel_repo import PersonelRepo
from app.db.repos.tatil_repo import TatilRepo
from app.exceptions import LimitHatasi, CakismaHatasi

class IzinService:

    def __init__(self, db):
        self._repo    = IzinRepo(db)
        self._p_repo  = PersonelRepo(db)
        self._t_repo  = TatilRepo(db)

    # ── İş Kuralları — 657 Sayılı Kanun ──────────────────────

    def bakiye(self, personel_id: str) -> dict:
        """
        Anlık bakiye hesabı. DB'ye YAZILMAZ.

        Yıllık hak (657 SK md.102):
          < 1 yıl  → 0
          1-10 yıl → 20
          > 10 yıl → 30

        Şua hakkı (Rad. Güvenliği Yönetmeliği):
          gorev_yeri.sua_hakki=1 → 30 iş günü/yıl
          gorev_yeri.sua_hakki=0 → 0
        """
        p        = self._p_repo.getir(personel_id)
        izinler  = self._repo.listele(personel_id=personel_id, durum='aktif')

        yillik_hak = self._yillik_hak(p.get('memuriyet_baslama'))
        sua_hak    = self._sua_hak(p.get('gorev_yeri_id'))

        yillik_kul = sum(i['gun'] for i in izinler if i['tur'] == 'yillik')
        sua_kul    = sum(i['gun'] for i in izinler if i['tur'] == 'sua')
        rapor_top  = sum(i['gun'] for i in izinler
                        if i['tur'] in ('rapor', 'mazeret'))

        return {
            'yillik_hak':      yillik_hak,
            'yillik_kullanilan': yillik_kul,
            'yillik_kalan':    max(0.0, yillik_hak - yillik_kul),
            'sua_hak':         sua_hak,
            'sua_kullanilan':  sua_kul,
            'sua_kalan':       max(0.0, sua_hak - sua_kul),
            'rapor_toplam':    rapor_top,
        }

    def devir_hesapla(self, yillik_hak: float, kalan: float) -> float:
        """657 SK md.102: min(kalan, hak, hak×2)"""
        return min(kalan, yillik_hak, yillik_hak * 2)

    # ── Kayıt İşlemleri ───────────────────────────────────────

    def kaydet(self, veri: dict) -> str:
        """
        İzin kaydeder.
        Raises: CakismaHatasi, LimitHatasi
        """
        pid  = veri['personel_id']
        tur  = veri['tur']
        gun  = int(veri['gun'])
        bas  = veri['baslama']
        bit  = veri['bitis']

        self._kontrol_cakisma(pid, bas, bit)
        self._kontrol_limit(pid, tur, gun)

        kayit_id = self._repo.ekle(veri)
        self._guncelle_durum(pid, tur, gun)
        return kayit_id

    def iptal(self, izin_id: str) -> None:
        self._repo.guncelle(izin_id, {'durum': 'iptal'})

    # ── Özel ──────────────────────────────────────────────────

    def _yillik_hak(self, baslama: str | None) -> float:
        if not baslama:
            return 0.0
        from app.validators import parse_tarih
        bas = parse_tarih(baslama)
        if not bas:
            return 0.0
        bugun = date.today()
        yil   = bugun.year - bas.year
        if (bugun.month, bugun.day) < (bas.month, bas.day):
            yil -= 1
        if yil < 1:   return 0.0
        if yil <= 10: return 20.0
        return 30.0

    def _sua_hak(self, gorev_yeri_id: str | None) -> float:
        if not gorev_yeri_id:
            return 0.0
        from app.db.repos.lookup_repo import GorevYeriRepo
        gy = GorevYeriRepo(self._repo._db).getir(gorev_yeri_id)
        return 30.0 if (gy and gy.get('sua_hakki')) else 0.0

    def _kontrol_cakisma(self, pid: str, bas: str, bit: str,
                          hariç_id: str = None) -> None:
        cakisan = self._repo.cakisan_bul(pid, bas, bit, hariç_id)
        if cakisan:
            raise CakismaHatasi(
                f"Bu tarih aralığında başka bir izin var: "
                f"{cakisan['baslama']} – {cakisan['bitis']}"
            )

    def _kontrol_limit(self, pid: str, tur: str, gun: int) -> None:
        b = self.bakiye(pid)
        if tur == 'yillik' and gun > b['yillik_kalan']:
            raise LimitHatasi(
                f"Yıllık izin kalan: {b['yillik_kalan']:.0f} gün, "
                f"talep: {gun} gün"
            )
        if tur == 'sua' and gun > b['sua_kalan']:
            raise LimitHatasi(
                f"Şua izni kalan: {b['sua_kalan']:.0f} gün, "
                f"talep: {gun} gün"
            )

    def _guncelle_durum(self, pid: str, tur: str, gun: int) -> None:
        """Uzun/ücretsiz izinlerde personeli pasife al."""
        pasif_kosul = (
            gun > 30 or
            tur in ('ucretsiz', 'ayliksiz')
        )
        if pasif_kosul:
            self._p_repo.guncelle(pid, {'durum': 'pasif'})
```

### 3.4 NobetService

```python
# app/services/nobet_service.py
"""
Nöbet algoritması:
  1. Ay iş günleri = takvim günleri - tatiller - hafta sonları (ayara göre)
  2. Her personel: hedef_saat = (is_gunu - izin_gunu) × vardiya_saat
     hedef_tipi:
       normal   → standart
       gonullu  → × 1.2
       rapor    → izin hesaplamaya dahil
       muaf     → 0
  3. Her gün slot_personel kadar ata:
     - Kalan bakiyesi en fazla olan önce
     - Max ardışık gün kuralını kontrol et
     - Tercih varsa önceliklendir
  4. Sonuç: nb_satir tablosuna yaz
"""
```

---

## 4. UI VE TEMA

### 4.1 Tema Felsefesi — QSS değil, Python

Eski kod 1121 satır QSS + runtime string replace kullanıyordu.
Yeni kodda her şey Python'da — derleme zamanında tip güvenli.

```python
# ui/theme.py

from dataclasses import dataclass
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

@dataclass(frozen=True)
class Palette:
    # ── Arka planlar ─────────────────────────
    bg_app:     str = "#0d1117"   # en koyu — uygulama zemini
    bg_panel:   str = "#161b22"   # panel, sidebar
    bg_card:    str = "#1c2128"   # kart, groupbox
    bg_input:   str = "#21262d"   # input alanları
    bg_hover:   str = "#2d333b"   # hover durumu

    # ── Kenarlıklar ──────────────────────────
    border:     str = "#30363d"
    border_focus: str = "#4f8ef7"

    # ── Renkler ──────────────────────────────
    accent:     str = "#4f8ef7"   # mavi — primary action
    success:    str = "#3fb950"   # yeşil
    warning:    str = "#d29922"   # sarı
    danger:     str = "#f85149"   # kırmızı

    # ── Metin ────────────────────────────────
    text_primary:  str = "#e6edf3"
    text_secondary: str = "#8b949e"
    text_muted:    str = "#484f58"
    text_link:     str = "#58a6ff"

    # ── Özel ─────────────────────────────────
    sidebar_w:  int = 72          # sidebar genişliği (px)


DARK = Palette()  # Tek tema, dark-first


def build_stylesheet(p: Palette = DARK) -> str:
    """
    Python f-string ile QSS üretir.
    Template dosyası yok, placeholder replace yok.
    """
    return f"""
    /* Uygulama zemini */
    QWidget {{
        background-color: {p.bg_app};
        color: {p.text_primary};
        font-family: "Segoe UI", "SF Pro Text", system-ui, sans-serif;
        font-size: 13px;
    }}

    /* Kart / GroupBox */
    QGroupBox {{
        background-color: {p.bg_card};
        border: 1px solid {p.border};
        border-radius: 8px;
        margin-top: 8px;
        padding: 12px 8px 8px 8px;
    }}
    QGroupBox::title {{
        color: {p.text_secondary};
        subcontrol-origin: margin;
        left: 12px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* Input alanları */
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
        background-color: {p.bg_input};
        border: 1px solid {p.border};
        border-radius: 6px;
        padding: 6px 10px;
        color: {p.text_primary};
        selection-background-color: {p.accent};
    }}
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
        border-color: {p.border_focus};
        outline: none;
    }}

    /* Butonlar */
    QPushButton {{
        background-color: {p.bg_input};
        border: 1px solid {p.border};
        border-radius: 6px;
        padding: 7px 16px;
        color: {p.text_primary};
        font-weight: 500;
    }}
    QPushButton:hover {{ background-color: {p.bg_hover}; }}
    QPushButton:pressed {{ background-color: {p.bg_panel}; }}

    /* Primary buton — action */
    QPushButton[primary=true] {{
        background-color: {p.accent};
        border-color: {p.accent};
        color: white;
        font-weight: 600;
    }}
    QPushButton[primary=true]:hover {{
        background-color: #6ea8ff;
    }}

    /* Tablo */
    QTableView {{
        background-color: {p.bg_card};
        border: 1px solid {p.border};
        border-radius: 6px;
        gridline-color: {p.border};
        alternate-background-color: {p.bg_input};
    }}
    QTableView::item:selected {{
        background-color: {p.accent}33;
        color: {p.text_primary};
    }}
    QHeaderView::section {{
        background-color: {p.bg_panel};
        color: {p.text_secondary};
        border: none;
        border-bottom: 1px solid {p.border};
        padding: 8px 12px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }}

    /* Scrollbar */
    QScrollBar:vertical {{
        background: {p.bg_panel};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {p.border};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    """


def apply(app: QApplication):
    app.setStyleSheet(build_stylesheet())
```

### 4.2 Reusable Bileşenler

```python
# ui/components/__init__.py
# Projenin her yerinde kullanılan hazır widget'lar

class PrimaryButton(QPushButton):
    """Mavi aksiyon butonu."""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setProperty("primary", True)
        # Başka özellik ayarı yok — QSS halleder


class Card(QFrame):
    """Kenarlıklı kart container."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        # bg_card rengi QSS'den gelir


class StatCard(QFrame):
    """Başlık + büyük değer + alt bilgi."""
    def __init__(self, baslik: str, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        self._lbl_baslik = QLabel(baslik)
        self._lbl_deger  = QLabel("—")
        self._lbl_alt    = QLabel("")
        # font boyutları burada Python'da set edilir:
        font = self._lbl_deger.font()
        font.setPointSize(22)
        font.setBold(True)
        self._lbl_deger.setFont(font)
        lay.addWidget(self._lbl_baslik)
        lay.addWidget(self._lbl_deger)
        lay.addWidget(self._lbl_alt)

    def set(self, deger: str, renk: str = None, alt: str = ""):
        self._lbl_deger.setText(deger)
        self._lbl_alt.setText(alt)
        if renk:
            self._lbl_deger.setStyleSheet(f"color: {renk};")
        else:
            self._lbl_deger.setStyleSheet("")


class Badge(QLabel):
    """Renkli durum rozeti."""
    RENKLER = {
        "aktif":   ("#3fb950", "#0d1117"),
        "pasif":   ("#8b949e", "#21262d"),
        "ayrildi": ("#f85149", "#0d1117"),
        "asim":    ("#f85149", "#2d1319"),
        "uyari":   ("#d29922", "#0d1117"),
    }

    def __init__(self, durum: str, parent=None):
        super().__init__(parent)
        self.set_durum(durum)
        self.setAlignment(Qt.AlignCenter)

    def set_durum(self, durum: str):
        bg, fg = self.RENKLER.get(durum.lower(), ("#8b949e", "#0d1117"))
        self.setText(durum.title())
        self.setStyleSheet(
            f"background:{bg}; color:{fg}; "
            f"border-radius:10px; padding:2px 8px; "
            f"font-size:11px; font-weight:600;"
        )


class AsyncRunner(QThread):
    """
    Tek generic QThread — 20+ farklı _Loader yerine.

    Kullanım:
        self._runner = AsyncRunner(
            fn=lambda: self._svc.listele(),
            on_done=self._on_data_loaded,
            on_error=self._on_error,
        )
        self._runner.start()
    """
    done  = Signal(object)
    error = Signal(str)

    def __init__(self, fn, on_done=None, on_error=None, parent=None):
        super().__init__(parent)
        self._fn = fn
        if on_done:  self.done.connect(on_done)
        if on_error: self.error.connect(on_error)

    def run(self):
        try:
            result = self._fn()
            self.done.emit(result)
        except Exception as exc:
            self.error.emit(str(exc))
```

### 4.3 Ana Pencere

```python
# ui/app_window.py

class AppWindow(QMainWindow):
    """
    Özel çerçeve (frameless).
    Sol sidebar + içerik alanı.
    """

    def __init__(self, db, kullanici):
        super().__init__()
        self._db = db
        self._kullanici = kullanici
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(1440, 900)
        self._build()

    def _build(self):
        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar: 72px sabit
        self._sidebar = Sidebar(self)
        self._sidebar.setFixedWidth(72)
        self._sidebar.page_changed.connect(self._goto)
        root.addWidget(self._sidebar)

        # İçerik
        self._stack = QStackedWidget()
        root.addWidget(self._stack, 1)

        # Sayfaları yükle
        self._pages = {
            "dashboard": DashboardPage(self._db),
            "personel":  PersonelPage(self._db),
            "nobet":     NobetPage(self._db),
            "cihaz":     CihazPage(self._db),
            "rapor":     RaporPage(self._db),
            "ayarlar":   AyarlarPage(self._db),
        }
        for page in self._pages.values():
            self._stack.addWidget(page)

        widget = QWidget()
        widget.setLayout(root)
        self.setCentralWidget(widget)

    def _goto(self, sayfa: str):
        self._stack.setCurrentWidget(self._pages[sayfa])


class Sidebar(QWidget):
    page_changed = Signal(str)

    MENU = [
        ("dashboard", "⊞", "Panel"),
        ("personel",  "👥", "Personel"),
        ("nobet",     "📅", "Nöbet"),
        ("cihaz",     "🔧", "Cihaz"),
        ("rapor",     "📊", "Rapor"),
        ("ayarlar",   "⚙",  "Ayarlar"),
    ]
```

---

## 5. PROJE KLASÖR YAPISI

```
repys/
│
├── main.py                  ← QApplication + login + AppWindow
│
├── app/
│   ├── config.py            ← Sabitler (DB yolu, log yolu, NDK limitleri)
│   ├── exceptions.py        ← AppHatasi, IsKuraliHatasi, LimitHatasi, ...
│   ├── validators.py        ← tc_dogrula(), parse_tarih(), format_tarih()
│   │
│   ├── db/
│   │   ├── database.py      ← Database sınıfı
│   │   ├── migrations.py    ← Migration runner
│   │   ├── seed.py          ← Lookup, tatil, gorev_yeri seed
│   │   └── repos/
│   │       ├── base.py
│   │       ├── personel_repo.py
│   │       ├── izin_repo.py
│   │       ├── muayene_repo.py
│   │       ├── fhsz_repo.py
│   │       ├── dozimetre_repo.py
│   │       ├── belge_repo.py
│   │       ├── nobet_repo.py       ← Tüm nb_* tabloları
│   │       ├── lookup_repo.py
│   │       └── kullanici_repo.py
│   │
│   └── services/
│       ├── personel_service.py
│       ├── izin_service.py
│       ├── muayene_service.py
│       ├── fhsz_service.py
│       ├── dozimetre_service.py
│       ├── belge_service.py
│       ├── nobet_service.py
│       ├── rapor_service.py     ← PDF üretimi
│       └── auth_service.py
│
├── ui/
│   ├── theme.py             ← Palette + build_stylesheet() + apply()
│   ├── app_window.py        ← Ana pencere
│   ├── login_window.py      ← Giriş ekranı
│   │
│   ├── components/          ← Reusable widget kütüphanesi
│   │   ├── buttons.py       ← PrimaryButton, DangerButton, IconButton
│   │   ├── cards.py         ← Card, StatCard
│   │   ├── tables.py        ← DataTable (QTableView wrapper)
│   │   ├── forms.py         ← FormRow, DateField, SearchBar, LookupCombo
│   │   ├── badges.py        ← Badge
│   │   ├── alerts.py        ← AlertBar (danger/warning/info/success)
│   │   ├── sidebar.py       ← Sidebar, SidebarButton
│   │   └── async_runner.py  ← AsyncRunner (tek QThread implementasyonu)
│   │
│   └── pages/
│       ├── dashboard/
│       │   └── dashboard_page.py
│       │
│       ├── personel/
│       │   ├── personel_page.py      ← Liste + detay routing
│       │   ├── personel_listesi.py   ← Tablo, arama, filtre
│       │   ├── personel_detay.py     ← Tab container
│       │   ├── personel_form.py      ← Ekle/düzenle formu
│       │   └── panels/
│       │       ├── kimlik_panel.py   ← Kişisel bilgiler
│       │       ├── izin_panel.py     ← İzin geçmişi + bakiye
│       │       ├── muayene_panel.py  ← Sağlık muayeneleri
│       │       ├── dozimetre_panel.py
│       │       ├── fhsz_panel.py
│       │       └── belge_panel.py
│       │
│       ├── nobet/
│       │   ├── nobet_page.py
│       │   ├── plan_listesi.py
│       │   ├── plan_detay.py        ← Takvim görünümü
│       │   └── birim_ayar.py
│       │
│       ├── cihaz/
│       ├── rapor/
│       └── ayarlar/
│
├── data/
│   ├── repys.db
│   └── belgeler/
│       ├── personel/
│       │   └── {tc}/
│       │       ├── diplomalar/
│       │       ├── raporlar/
│       │       └── dozimetre/
│       ├── cihaz/
│       └── rke/
│
├── tests/
│   ├── conftest.py
│   ├── test_izin_service.py
│   ├── test_nobet_service.py
│   └── test_validators.py
│
└── requirements.txt
    PySide6>=6.6
    reportlab>=4.0
    bcrypt>=4.0
    google-api-python-client>=2.0   # drive sync için
```

---

## 6. KODLAMA KURALLARI

```
GENEL:
  ✓  Exception fırlatılır, SonucYonetici döndürülmez
  ✓  Tür ipuçları (type hints) her yerde
  ✓  Docstring: ne yapar, ne fırlatır
  ✓  Servis → repo çağırır, direkt SQL yok
  ✓  UUID primary key (uuid4().hex)
  ✓  Tarihler: "YYYY-MM-DD" string

VERİTABANI:
  ✓  Hesaplanan değer (bakiye, yaş) saklanmaz
  ✓  AdSoyad JOIN ile gelir, kopyalanmaz
  ✓  Soft delete: durum='iptal' veya aktif=0
  ✓  Foreign key her zaman açık
  ✓  Transaction: atomik işlemler için db.transaction()

UI:
  ✓  setStyleSheet sadece dinamik renk için (badge vs.)
  ✓  Sabit fontlar: Python'da set edilir, QSS'de tanımlanmaz
  ✓  QThread → her zaman AsyncRunner kullanılır
  ✓  Dialog: native Qt dialog veya QDialog subclass
  ✓  Exception yakalanır, kullanıcıya anlaşılır mesaj gösterilir

YASAK:
  ✗  setProperty("style-role", ...) — artık yok
  ✗  SonucYonetici — artık yok
  ✗  RepositoryRegistry — artık yok
  ✗  table_config.py — artık yok
  ✗  di.py get_xxx_service() — artık yok
  ✗  QMessageBox.critical/warning doğrudan — try/except + alert widget
  ✗  Personel.sil() — sadece pasife_al()
  ✗  DB'ye bakiye yazma — sadece hesapla
```

---

## 7. SPRINT PLANI

```
Sprint 1 (1 hafta): Temel Altyapı
  app/config.py, exceptions.py, validators.py
  db/database.py + migration sistemi + seed
  Tüm tablo şemaları
  ui/theme.py + components/ kütüphanesi
  Boş AppWindow çerçevesi

Sprint 2 (1 hafta): Personel CRUD
  PersonelRepo + PersonelService
  PersonelPage → Listesi + Form
  KimlikPanel (görüntüleme + düzenleme)

Sprint 3 (1 hafta): İzin Modülü
  IzinRepo + IzinService (bakiye, limit, çakışma)
  IzinPanel → Liste + Bakiye widget + Dialog

Sprint 4 (1 hafta): Sağlık + Dozimetre
  MuayeneRepo/Service + MuayenePanel
  DozimetreRepo/Service + DozimetrePanel
  Doz araştırma formu (PDF)
  FhszPanel

Sprint 5 (1 hafta): Nöbet
  Tüm nb_ repo'ları
  NobetService + algoritma
  PlanPage + TakvimWidget

Sprint 6 (1 hafta): Tamamlama
  Dashboard (istatistikler, uyarılar)
  BelgeService + lokal dosya yönetimi
  Auth + login
  RaporService (PDF/Excel)
  Test kapsamı

TOPLAM: 6 Sprint × 1 hafta = 6 hafta
```

---

## 8. KORUNAN İŞ KURALLARI

```
İzin (657 SK):
  Yıllık hak:  <1yıl=0 | 1-10yıl=20 | >10yıl=30 gün
  Devir limiti: min(kalan, hak, hak×2)
  Şua izni:    Koşul A=30 iş günü | Koşul B=0
  Pasif koşul: >30 gün VEYA ücretsiz/aylıksız izin
  Çakışma:     (yeni_bas ≤ mevcut_bit) AND (yeni_bit ≥ mevcut_bas)

Dozimetre (Rad. Güv. Yönetmeliği):
  Hp(10) uyarı:  ≥ 2.0 mSv/periyot
  Hp(10) tehlike: ≥ 5.0 mSv/periyot
  Yıllık NDK:    20.0 mSv
  5 yıllık NDK:  100.0 mSv
  Koşul A eşiği: 6.0 mSv/yıl
  Periyot:       4/yıl (RADAT sistemi)
  Doz aşımı →    TAEK bildirimi 30 gün içinde zorunlu

Nöbet:
  Hedef = (ay_is - izin) × vardiya_saat
  Gonullu: hedef × 1.2 | Muaf: 0
  Max ardışık gün: birim ayarından
  Slot: birim ayarından (genellikle 2 kişi/gün)
  Tolerans: ±1 slot

FHSZ:
  Dönem: 2 aylık | 6 dönem/yıl
  Şua hakkı hesabı girdisi: fiili_saat
```
