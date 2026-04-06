# REPYS 2.0 — Sıfırdan Tasarım Belgesi

> Mevcut kod yalnızca iş akışlarını anlamak için kullanıldı.
> Her karar temiz sayfa üzerinden alındı.

---

## 1. GENEL MİMARİ KARARLARI

### 1.1 Teknoloji Seçimleri

| Katman | Teknoloji | Neden |
|--------|-----------|-------|
| Dil | Python 3.12 | Mevcut ekip bilgisi |
| UI | PySide6 (Qt 6) | Cross-platform, native görünüm |
| DB | SQLite 3.40+ | Kurulum gerektirmez, dosya taşınabilir |
| ORM | Yok — ham SQL | Basit → performans → hata ayıklama kolaylığı |
| Async | QThread + Signal/Slot | Qt ekosistemiyle uyumlu |
| Test | pytest + pytest-qt | Mevcut |
| Raporlama | reportlab | PDF; mevcut |
| Sync | Google Sheets API | Mevcut iş gereksinimi |

### 1.2 Uygulama Katmanları

```
┌─────────────────────────────────────┐
│  UI (PySide6 Widget'ları)           │  ← Sadece görüntüleme + kullanıcı girişi
├─────────────────────────────────────┤
│  Servis Katmanı                     │  ← İş kuralları burada
├─────────────────────────────────────┤
│  Repository Katmanı                 │  ← SQL sorguları burada
├─────────────────────────────────────┤
│  SQLite                             │  ← Veri
└─────────────────────────────────────┘
```

**Katmanlar arası kurallar:**
- UI → Servis çağırır, Repository'ye hiç erişmez
- Servis → Repository çağırır, widget import etmez
- Repository → Ham SQL çalıştırır, iş mantığı yoktur
- Migration → Tablo oluşturur, seed data yazar

---

## 2. VERİTABANI TASARIMI

### 2.1 Tasarım İlkeleri

1. **Hesaplanan değer saklanmaz.** İzin bakiyesi, yaş, hizmet yılı vb.
   her zaman servis katmanında hesaplanır.
2. **Denormalizasyon yasak.** `AdSoyad` yalnızca `personel` tablosunda.
   JOIN kullanılır.
3. **Soft delete.** Hiçbir kayıt fiziksel olarak silinmez.
   `silinmis_mi` veya `durum` alanı kullanılır.
4. **UUID primary key.** Tüm kayıtlar `TEXT UUID` PK kullanır.
   Anlamlı bileşik PK'lar (örn. TC+Yıl+Periyot) yalnızca
   UNIQUE constraint olarak tanımlanır.
5. **Tarihler ISO-8601 TEXT.** `YYYY-MM-DD` formatında saklanır.
6. **Foreign key'ler aktif.** `PRAGMA foreign_keys = ON`

---

### 2.2 Tam Tablo Şeması

#### ÇEKIRDEK: `personel`

```sql
CREATE TABLE personel (
    id                      TEXT PRIMARY KEY,          -- UUID
    tc_kimlik               TEXT NOT NULL UNIQUE,      -- 11 hane
    ad                      TEXT NOT NULL,
    soyad                   TEXT NOT NULL,
    dogum_tarihi            TEXT,
    dogum_yeri              TEXT,
    hizmet_sinifi           TEXT,                      -- Akademik / Hemşire / Radyasyon Görevlisi ...
    kadro_unvani            TEXT,                      -- Teknisyen / Uzman Doktor ...
    gorev_yeri_id           TEXT REFERENCES gorev_yeri(id),
    kurum_sicil_no          TEXT,
    memuriyet_baslama       TEXT,                      -- ISO-8601, yıllık hak hesabı için
    cep_telefonu            TEXT,
    e_posta                 TEXT,
    fotograf_yolu           TEXT,                      -- lokal dosya yolu
    durum                   TEXT NOT NULL DEFAULT 'aktif'
                                CHECK (durum IN ('aktif','pasif','ayrildi')),
    ayrilik_tarihi          TEXT,
    ayrilik_nedeni          TEXT,
    olusturma_tarihi        TEXT NOT NULL DEFAULT (date('now')),
    guncelleme_tarihi       TEXT,
    -- Eğitim (2 diploma desteği)
    mezun_okul_1            TEXT,
    mezun_fakulte_1         TEXT,
    mezuniyet_tarihi_1      TEXT,
    diploma_no_1            TEXT,
    mezun_okul_2            TEXT,
    mezun_fakulte_2         TEXT,
    mezuniyet_tarihi_2      TEXT,
    diploma_no_2            TEXT
);
CREATE INDEX idx_personel_tc     ON personel(tc_kimlik);
CREATE INDEX idx_personel_durum  ON personel(durum);
```

---

#### `gorev_yeri`

```sql
-- Sabitler tablosundan kurtulup bağımsız tablo
CREATE TABLE gorev_yeri (
    id                TEXT PRIMARY KEY,
    ad                TEXT NOT NULL UNIQUE,
    kisaltma          TEXT,
    calisma_kosulu    TEXT CHECK (calisma_kosulu IN ('A','B','Yok')),
    -- Koşul A: Şua izni hakkı var (30 iş günü)
    -- Koşul B: Şua izni yok
    aktif             INTEGER NOT NULL DEFAULT 1
);
-- Seed: Acil Radyoloji → A, Girişimsel → A, Gögüs Hast. → B ...
```

---

#### `izin_kayit`

```sql
CREATE TABLE izin_kayit (
    id              TEXT PRIMARY KEY,
    personel_id     TEXT NOT NULL REFERENCES personel(id),
    izin_tipi       TEXT NOT NULL,
    -- Yıllık İzin | Şua İzni | Ücretsiz İzin | Hastalık Raporu
    -- Mazeret İzni | Aylıksız İzin | Doğum İzni | Ölüm İzni
    baslama_tarihi  TEXT NOT NULL,
    gun             INTEGER NOT NULL CHECK (gun > 0),
    bitis_tarihi    TEXT NOT NULL,       -- baslama + gun - 1
    durum           TEXT NOT NULL DEFAULT 'aktif'
                        CHECK (durum IN ('aktif','iptal')),
    aciklama        TEXT,
    olusturma_tarihi TEXT NOT NULL DEFAULT (date('now')),
    guncelleme_tarihi TEXT,
    UNIQUE (personel_id, baslama_tarihi, izin_tipi)
    -- Aynı kişi aynı günde aynı türde iki izin giremez
);
CREATE INDEX idx_izin_personel ON izin_kayit(personel_id);
CREATE INDEX idx_izin_tarih    ON izin_kayit(baslama_tarihi);
-- NOT: YillikKalan, SuaKalan vs. SAKLANMAZ → servis hesaplar
```

---

#### `muayene` (eski Personel_Saglik_Takip yerine)

```sql
CREATE TABLE muayene (
    id                  TEXT PRIMARY KEY,
    personel_id         TEXT NOT NULL REFERENCES personel(id),
    uzmanlik            TEXT NOT NULL,
    -- 'Genel' | 'Dermatoloji' | 'Dahiliye' | 'Göz' | 'Görüntüleme' | 'Diğer'
    muayene_tarihi      TEXT NOT NULL,
    sonraki_tarih       TEXT,
    sonuc               TEXT CHECK (sonuc IN ('Uygun','Uygun Değil','Takipte',NULL)),
    notlar              TEXT,
    belge_id            TEXT REFERENCES belge(id),    -- rapor dosyası
    olusturma_tarihi    TEXT NOT NULL DEFAULT (date('now')),
    UNIQUE (personel_id, uzmanlik, muayene_tarihi)
);
CREATE INDEX idx_muayene_personel ON muayene(personel_id);
CREATE INDEX idx_muayene_sonraki  ON muayene(sonraki_tarih);
```

---

#### `fhsz_puantaj`

```sql
CREATE TABLE fhsz_puantaj (
    id              TEXT PRIMARY KEY,
    personel_id     TEXT NOT NULL REFERENCES personel(id),
    yil             INTEGER NOT NULL,
    donem           INTEGER NOT NULL CHECK (donem BETWEEN 1 AND 6),
    -- Dönem 1=Ocak-Şubat, 2=Mart-Nisan, ..., 6=Kasım-Aralık
    aylik_gun       INTEGER,
    kullanilan_izin INTEGER DEFAULT 0,
    fiili_calisma_saat REAL,
    calisma_kosulu  TEXT,    -- Koşul A veya B (anlık, personelden kopyalanır)
    notlar          TEXT,
    olusturma_tarihi TEXT NOT NULL DEFAULT (date('now')),
    UNIQUE (personel_id, yil, donem)
);
```

---

#### `dozimetre_olcum`

```sql
CREATE TABLE dozimetre_olcum (
    id              TEXT PRIMARY KEY,
    personel_id     TEXT NOT NULL REFERENCES personel(id),
    rapor_no        TEXT,
    yil             INTEGER NOT NULL,
    periyot         INTEGER NOT NULL CHECK (periyot BETWEEN 1 AND 4),
    periyot_adi     TEXT,   -- 'Ocak-Mart' gibi
    dozimetre_no    TEXT,
    dozimetri_tipi  TEXT,   -- TLD | OSL | Nötron | Elektronik
    vucut_bolgesi   TEXT,
    hp10            REAL,   -- mSv
    hp007           REAL,   -- mSv
    durum           TEXT,   -- 'Normal' | 'Doz Aşımı' | 'İade Edilmedi'
    olusturma_tarihi TEXT NOT NULL DEFAULT (date('now')),
    UNIQUE (personel_id, yil, periyot, dozimetre_no)
);
CREATE INDEX idx_doz_personel ON dozimetre_olcum(personel_id);
```

---

#### `doz_arastirma_formu`

```sql
CREATE TABLE doz_arastirma_formu (
    id              TEXT PRIMARY KEY,
    olcum_id        TEXT NOT NULL REFERENCES dozimetre_olcum(id),
    personel_id     TEXT NOT NULL REFERENCES personel(id),
    yil             INTEGER NOT NULL,
    periyot         INTEGER NOT NULL,
    olculen_doz     REAL,
    pdf_yolu        TEXT,           -- lokal dosya yolu
    olusturma_tarihi TEXT NOT NULL DEFAULT (date('now')),
    UNIQUE (personel_id, yil, periyot)
);
```

---

#### NÖBET MODÜLÜ

```sql
CREATE TABLE nb_birim (
    id          TEXT PRIMARY KEY,
    ad          TEXT NOT NULL UNIQUE,
    kisaltma    TEXT,
    aktif       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE nb_birim_ayar (
    id                  TEXT PRIMARY KEY,
    birim_id            TEXT NOT NULL REFERENCES nb_birim(id),
    slot_basi_personel  INTEGER NOT NULL DEFAULT 2,
    max_ardisik_gun     INTEGER NOT NULL DEFAULT 3,
    hafta_sonu_aktif    INTEGER NOT NULL DEFAULT 1,
    resmi_tatil_aktif   INTEGER NOT NULL DEFAULT 1,
    gecerlilik_basi     TEXT NOT NULL,
    gecerlilik_sonu     TEXT,
    UNIQUE (birim_id, gecerlilik_basi)
);

CREATE TABLE nb_vardiya (
    id          TEXT PRIMARY KEY,
    birim_id    TEXT NOT NULL REFERENCES nb_birim(id),
    ad          TEXT NOT NULL,          -- 'Gündüz' | 'Gece'
    saat_suresi REAL NOT NULL,          -- 7.0, 12.0 gibi
    ana_vardiya INTEGER NOT NULL DEFAULT 1,
    aktif       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE nb_birim_personel (
    id          TEXT PRIMARY KEY,
    birim_id    TEXT NOT NULL REFERENCES nb_birim(id),
    personel_id TEXT NOT NULL REFERENCES personel(id),
    gorev_basi  TEXT NOT NULL,
    gorev_sonu  TEXT,
    aktif       INTEGER NOT NULL DEFAULT 1,
    UNIQUE (birim_id, personel_id, gorev_basi)
);

CREATE TABLE nb_tercih (
    id              TEXT PRIMARY KEY,
    birim_id        TEXT NOT NULL REFERENCES nb_birim(id),
    personel_id     TEXT NOT NULL REFERENCES personel(id),
    hedef_tipi      TEXT NOT NULL DEFAULT 'normal',
    -- 'normal' | 'gonullu' | 'rapor' | 'muaf'
    max_nobet_gun   INTEGER,
    tercih_vardiyas TEXT,           -- JSON liste: ["Gündüz"]
    kacin_gunler    TEXT,           -- JSON liste: ["2026-01-15"]
    notlar          TEXT,
    gecerlilik_basi TEXT NOT NULL,
    gecerlilik_sonu TEXT,
    UNIQUE (birim_id, personel_id, gecerlilik_basi)
);

CREATE TABLE nb_plan (
    id                  TEXT PRIMARY KEY,
    birim_id            TEXT NOT NULL REFERENCES nb_birim(id),
    yil                 INTEGER NOT NULL,
    ay                  INTEGER NOT NULL CHECK (ay BETWEEN 1 AND 12),
    durum               TEXT NOT NULL DEFAULT 'taslak'
                            CHECK (durum IN ('taslak','onaylandi','iptal')),
    algoritma_versiyonu TEXT,
    notlar              TEXT,
    onaylayan_id        TEXT,
    onay_tarihi         TEXT,
    olusturma_tarihi    TEXT NOT NULL DEFAULT (date('now')),
    UNIQUE (birim_id, yil, ay)
);

CREATE TABLE nb_plan_satir (
    id          TEXT PRIMARY KEY,
    plan_id     TEXT NOT NULL REFERENCES nb_plan(id),
    personel_id TEXT NOT NULL REFERENCES personel(id),
    vardiya_id  TEXT NOT NULL REFERENCES nb_vardiya(id),
    nobet_tarihi TEXT NOT NULL,
    saat_suresi REAL NOT NULL,
    kaynak      TEXT NOT NULL DEFAULT 'algoritma',
    -- 'algoritma' | 'manuel' | 'degisim'
    notlar      TEXT,
    olusturma_tarihi TEXT NOT NULL DEFAULT (date('now'))
);
CREATE INDEX idx_satir_plan    ON nb_plan_satir(plan_id);
CREATE INDEX idx_satir_personel ON nb_plan_satir(personel_id);
CREATE INDEX idx_satir_tarih   ON nb_plan_satir(nobet_tarihi);
```

---

#### DESTEK TABLOLARI

```sql
-- Belge arşivi (personel, cihaz, RKE için ortak)
CREATE TABLE belge (
    id              TEXT PRIMARY KEY,
    entity_turu     TEXT NOT NULL,  -- 'personel' | 'cihaz' | 'rke' | 'muayene'
    entity_id       TEXT NOT NULL,
    belge_turu      TEXT NOT NULL,  -- Diploma | Rapor | Doz Araştırma Formu ...
    dosya_adi       TEXT NOT NULL,
    lokal_yol       TEXT,
    drive_link      TEXT,
    aciklama        TEXT,
    yukleme_tarihi  TEXT NOT NULL DEFAULT (date('now'))
);
CREATE INDEX idx_belge_entity ON belge(entity_turu, entity_id);

-- Lookup tablosu (eski Sabitler yerine — kategorize edilmiş)
CREATE TABLE lookup (
    id          TEXT PRIMARY KEY,
    kategori    TEXT NOT NULL,
    -- 'izin_tipi' | 'hizmet_sinifi' | 'kadro_unvani' | 'uzmanlik' | ...
    deger       TEXT NOT NULL,
    aciklama    TEXT,
    siralama    INTEGER DEFAULT 0,
    aktif       INTEGER NOT NULL DEFAULT 1,
    UNIQUE (kategori, deger)
);

-- Tatil günleri
CREATE TABLE tatil (
    tarih       TEXT PRIMARY KEY,   -- YYYY-MM-DD
    ad          TEXT NOT NULL,
    tur         TEXT NOT NULL DEFAULT 'resmi'
                    CHECK (tur IN ('resmi','dini'))
);

-- Kullanıcılar (auth)
CREATE TABLE kullanici (
    id              TEXT PRIMARY KEY,
    kullanici_adi   TEXT NOT NULL UNIQUE,
    sifre_hash      TEXT NOT NULL,
    personel_id     TEXT REFERENCES personel(id),
    rol             TEXT NOT NULL DEFAULT 'kullanici'
                        CHECK (rol IN ('admin','yonetici','kullanici')),
    aktif           INTEGER NOT NULL DEFAULT 1,
    son_giris       TEXT,
    olusturma_tarihi TEXT NOT NULL DEFAULT (date('now'))
);

-- Uygulama ayarları
CREATE TABLE ayar (
    anahtar     TEXT PRIMARY KEY,
    deger       TEXT,
    aciklama    TEXT,
    guncelleme  TEXT
);
```

---

### 2.3 Lookup Kategorileri (seed data)

```python
LOOKUP_SEED = [
    # Kategori: izin_tipi
    ('izin_tipi', 'Yıllık İzin'),
    ('izin_tipi', 'Şua İzni'),
    ('izin_tipi', 'Hastalık Raporu'),
    ('izin_tipi', 'Mazeret İzni'),
    ('izin_tipi', 'Ücretsiz İzin'),
    ('izin_tipi', 'Aylıksız İzin'),
    ('izin_tipi', 'Doğum İzni'),
    ('izin_tipi', 'Ölüm İzni'),
    ('izin_tipi', 'Evlilik İzni'),
    ('izin_tipi', 'Babalık İzni'),

    # Kategori: hizmet_sinifi
    ('hizmet_sinifi', 'Akademik Personel'),
    ('hizmet_sinifi', 'Asistan Doktor'),
    ('hizmet_sinifi', 'Hemşire'),
    ('hizmet_sinifi', 'Radyasyon Görevlisi'),

    # Kategori: kadro_unvani
    ('kadro_unvani', 'Araştırma Görevlisi'),
    ('kadro_unvani', 'Doçent Doktor'),
    ('kadro_unvani', 'Uzman Doktor'),
    ('kadro_unvani', 'Radyoloji Teknikeri'),
    ('kadro_unvani', 'Radyoloji Teknisyeni'),
    ('kadro_unvani', 'Teknisyen'),
    # ...

    # Kategori: uzmanlik (muayene)
    ('uzmanlik', 'Genel'),
    ('uzmanlik', 'Dermatoloji'),
    ('uzmanlik', 'Dahiliye'),
    ('uzmanlik', 'Göz'),
    ('uzmanlik', 'Görüntüleme'),

    # Kategori: nobet_hedef_tipi
    ('nobet_hedef_tipi', 'normal'),
    ('nobet_hedef_tipi', 'gonullu'),
    ('nobet_hedef_tipi', 'rapor'),
    ('nobet_hedef_tipi', 'muaf'),
]
```

---

## 3. SERVİS KATMANI

### 3.1 Klasör Yapısı

```
app/
├── db/
│   ├── connection.py       ← SQLite bağlantı yönetimi
│   ├── migrations.py       ← Versiyonlu migration sistemi
│   └── repositories/
│       ├── base.py         ← BaseRepository (execute, fetch_one, fetch_all)
│       ├── personel.py
│       ├── izin.py
│       ├── muayene.py
│       ├── fhsz.py
│       ├── dozimetre.py
│       └── nobet.py
│
├── services/
│   ├── personel_service.py
│   ├── izin_service.py
│   ├── muayene_service.py
│   ├── fhsz_service.py
│   ├── dozimetre_service.py
│   ├── nobet_service.py    ← Tek nöbet servisi
│   └── belge_service.py
│
└── ui/ ...
```

### 3.2 `IzinService` — Bakiye Hesaplama

```python
class IzinService:

    def bakiye(self, personel_id: str) -> IzinBakiye:
        """
        Anlık bakiye — DB'ye yazılmaz.

        İş kuralları (657 SK):
        ┌─────────────────────────────────────────────────────┐
        │ Yıllık Hak:                                         │
        │   < 1 yıl hizmet → 0 gün                          │
        │   1–10 yıl       → 20 gün                          │
        │   > 10 yıl       → 30 gün                          │
        │                                                     │
        │ Şua Hakkı:                                          │
        │   Çalışma Koşulu A → 30 iş günü/yıl               │
        │   Çalışma Koşulu B → 0 gün                         │
        │                                                     │
        │ Devir (657 SK md.102):                              │
        │   min(kalan, yıllık_hak, yıllık_hak × 2)          │
        └─────────────────────────────────────────────────────┘
        """
        personel = self._repo_personel.get_by_id(personel_id)
        izinler  = self._repo_izin.list_by_personel(
                       personel_id, durum='aktif')

        yillik_hak = self._hesapla_yillik_hak(
            personel['memuriyet_baslama'])
        sua_hak    = self._hesapla_sua_hak(
            personel.get('gorev_yeri_id'))

        yillik_kul = sum(i['gun'] for i in izinler
                         if i['izin_tipi'] == 'Yıllık İzin')
        sua_kul    = sum(i['gun'] for i in izinler
                         if i['izin_tipi'] == 'Şua İzni')

        return IzinBakiye(
            yillik_hak=yillik_hak,
            yillik_kullanilan=yillik_kul,
            yillik_kalan=max(0, yillik_hak - yillik_kul),
            sua_hak=sua_hak,
            sua_kullanilan=sua_kul,
            sua_kalan=max(0, sua_hak - sua_kul),
        )

    def kaydet(self, veri: dict) -> str:
        """
        İzin kaydeder; çakışma + limit kontrolü yapar.
        Pasif statüsü burada güncellenir.

        Pasif kuralı:
          - İzin süresi > 30 gün
          - İzin tipi: Aylıksız veya Ücretsiz
        """
        self._kontrol_cakisma(veri)
        self._kontrol_limit(veri)
        kayit_id = self._repo.insert(veri)
        self._guncelle_personel_durumu(veri)
        return kayit_id
```

---

### 3.3 `NobetService` — Tek Servis

```python
class NobetService:
    """
    Algoritma mantığı:
    ┌─────────────────────────────────────────────────────────┐
    │ 1. Ay için iş günlerini hesapla (tatiller çıkar)        │
    │ 2. Her personelin aylık hedef saatini hesapla           │
    │    hedef = (ay_is_gunu - izin_gunu) × vardiya_saat      │
    │    Hedef tipi gonullu → hedef × 1.2                     │
    │    Hedef tipi rapor   → hedef (izin düşülür)            │
    │    Hedef tipi muaf    → 0                               │
    │ 3. Her gün slot sayısı kadar personel ata               │
    │    - Max ardışık gün kuralını uygula                    │
    │    - Bakiye az olandan başla (adil dağılım)             │
    │    - Tercih varsa önceliklendir                         │
    │ 4. Sonuçları nb_plan_satir'e yaz                        │
    └─────────────────────────────────────────────────────────┘
    """

    def plan_olustur(self, birim_id: str, yil: int, ay: int) -> PlanSonucu:
        ...

    def plan_duzenle(self, satir_id: str, yeni_personel_id: str) -> None:
        """Manuel değişiklik → kaynak='manuel'"""

    def mesai_hesapla(self, plan_id: str) -> list[MesaiOzet]:
        """Plan satırlarından kişi bazlı mesai toplamı"""
```

---

## 4. UI TASARIMI VE TEMA

### 4.1 Tasarım Dili

**Ana renk sistemi:**
```
Arka plan (koyu)  : #0f1117  ← Neredeyse siyah
Panel             : #1a1d2e  ← Koyu lacivert
Kart              : #1e2235  ← Biraz daha açık
Kenarlık          : #2a2f45  ← Çok ince çizgi
Vurgu (mavi)      : #4f8ef7  ← Parlak mavi
Başarı (yeşil)    : #22c55e
Uyarı (sarı)      : #f59e0b
Tehlike (kırmızı) : #ef4444
Metin (birincil)  : #e2e8f0
Metin (ikincil)   : #94a3b8
Metin (soluk)     : #475569
```

**Font:**
```
Başlıklar : Inter / Segoe UI   16–24px, 600 ağırlık
Gövde     : Inter / Segoe UI   13px, 400 ağırlık
Sayısal   : JetBrains Mono     12px (tablolar, dozimetre değerleri)
```

### 4.2 Ana Pencere Yapısı

```
┌────────────────────────────────────────────────────────────┐
│  ░ REPYS                         🔔  👤 Admin     [─][□][×] │  ← Başlık çubuğu
├──────────┬─────────────────────────────────────────────────┤
│          │                                                  │
│  📋      │  [İçerik Alanı]                                 │
│  Personel│                                                  │
│          │                                                  │
│  🔧      │                                                  │
│  Cihaz   │                                                  │
│          │                                                  │
│  📅      │                                                  │
│  Nöbet   │                                                  │
│          │                                                  │
│  📊      │                                                  │
│  Rapor   │                                                  │
│          │                                                  │
│  ⚙️      │                                                  │
│  Ayarlar │                                                  │
│          │                                                  │
└──────────┴─────────────────────────────────────────────────┘
     80px            Kalan genişlik
```

**Sol sidebar:** İkon + etiket, hover'da parlama, aktif'te vurgu çubuğu.
**Başlık çubuğu:** Özel — işletim sistemi başlığı gizli.

### 4.3 Personel Modülü UI

```
Personel Listesi
├── [+ Yeni Personel]  [🔍 Ara]  [Filtre ▾]  [📤 Dışa Aktar]
│
├── Tablo: Ad Soyad | TC | Görev Yeri | Durum | Eylemler
│
└── Satıra tıklanınca → PersonelDetay açılır (sağda panel veya yeni sekme)
         ├── [Kimlik]  [İzin]  [Sağlık]  [Dozimetre]  [FHSZ]  [Belgeler]
         └── Her sekme bağımsız widget
```

### 4.4 Bileşen Kütüphanesi

Sıfırdan yazılacak, `setProperty("style-role", ...)` yerine:

```python
# Tüm bileşenler merkezi stylesheet'ten stil alır
class Theme:
    CARD_BG     = "#1e2235"
    ACCENT      = "#4f8ef7"
    SUCCESS     = "#22c55e"
    DANGER      = "#ef4444"
    WARNING     = "#f59e0b"
    TEXT_PRIMARY = "#e2e8f0"
    TEXT_MUTED   = "#94a3b8"

# Reusable bileşenler:
class Card(QFrame)           # Kenarlıklı, gölgeli kart kutusu
class StatCard(QFrame)       # Başlık + büyük sayı + alt metin
class Badge(QLabel)          # Renkli etiket (Aktif / Pasif)
class AlertBar(QFrame)       # Uyarı bandı (danger/warning/info)
class DataTable(QTableView)  # Standart tablo
class FormRow(QHBoxLayout)   # Etiket + widget çifti
class DateField(QLineEdit)   # Tarih girişi (YYYY-MM-DD)
class SearchBar(QLineEdit)   # Arama kutusu
```

---

## 5. KLASÖR YAPISI

```
repys/
│
├── main.py                     ← Giriş noktası
│
├── app/
│   ├── __init__.py
│   ├── config.py               ← Sabitler, yollar
│   │
│   ├── db/
│   │   ├── connection.py       ← get_connection(), pragma ayarları
│   │   ├── migrations.py       ← run_migrations()
│   │   └── repos/
│   │       ├── base.py
│   │       ├── personel_repo.py
│   │       ├── izin_repo.py
│   │       ├── muayene_repo.py
│   │       ├── fhsz_repo.py
│   │       ├── dozimetre_repo.py
│   │       ├── nobet_repo.py
│   │       └── belge_repo.py
│   │
│   ├── services/
│   │   ├── personel_service.py
│   │   ├── izin_service.py
│   │   ├── muayene_service.py
│   │   ├── fhsz_service.py
│   │   ├── dozimetre_service.py
│   │   ├── nobet_service.py
│   │   ├── belge_service.py
│   │   └── rapor_service.py    ← PDF üretimi
│   │
│   ├── models.py               ← Dataclass'lar (IzinBakiye, PlanSonucu vs.)
│   ├── validators.py           ← TC doğrulama, tarih parse
│   └── exceptions.py           ← İş kuralı hataları (IzinLimitHatasi vs.)
│
├── ui/
│   ├── app_window.py           ← Ana pencere
│   ├── theme.py                ← Renkler, fontlar, stylesheet
│   │
│   ├── components/             ← Reusable widget kütüphanesi
│   │   ├── card.py
│   │   ├── table.py
│   │   ├── form.py
│   │   ├── badge.py
│   │   ├── alert.py
│   │   └── loader.py           ← QThread wrapper
│   │
│   ├── pages/
│   │   ├── dashboard/
│   │   │   └── dashboard_page.py
│   │   │
│   │   ├── personel/
│   │   │   ├── liste_page.py
│   │   │   ├── detay_page.py
│   │   │   ├── ekle_dialog.py
│   │   │   └── panels/
│   │   │       ├── kimlik_panel.py
│   │   │       ├── izin_panel.py
│   │   │       ├── muayene_panel.py
│   │   │       ├── dozimetre_panel.py
│   │   │       ├── fhsz_panel.py
│   │   │       └── belge_panel.py
│   │   │
│   │   ├── nobet/
│   │   │   ├── plan_page.py
│   │   │   ├── takvim_widget.py
│   │   │   └── ayar_dialog.py
│   │   │
│   │   ├── cihaz/
│   │   └── ayarlar/
│   │
│   └── dialogs/
│       ├── izin_dialog.py
│       ├── muayene_dialog.py
│       └── doz_arastirma_dialog.py
│
├── data/
│   ├── repys.db                ← SQLite veritabanı
│   ├── belgeler/               ← Lokal dosya arşivi
│   └── exports/                ← Geçici PDF/Excel çıktıları
│
├── tests/
│   ├── conftest.py
│   ├── test_izin_service.py
│   ├── test_nobet_service.py
│   └── test_dozimetre_service.py
│
└── requirements.txt
```

---

## 6. GELİŞTİRME KURALLARI

```
1. Her Repository dosyası yalnızca bir tablo için SQL içerir
2. Servis katmanı iş mantığını içerir, SQL içermez
3. UI katmanı servis çağırır, Repository'ye doğrudan erişmez
4. Hesaplanan değer (bakiye, yaş, kalan gün) DB'ye yazılmaz
5. Soft delete: durum='iptal' veya aktif=0, fiziksel silme yok
6. Tüm primary key'ler UUID (uuid.uuid4().hex)
7. Tarih string'leri ISO-8601 formatında (YYYY-MM-DD)
8. İş kuralı ihlalleri exception fırlatır, None döndürmez
9. Her servis metodu docstring içerir (ne yapar, ne döndürür)
10. UI'da setStyleSheet(f"...") yasak; Theme.apply(widget) kullanılır
```

---

## 7. SPRINT PLANI

### Sprint 1 (1 hafta) — Temel Altyapı
- [ ] Klasör yapısı + `main.py`
- [ ] `db/connection.py` + migration sistemi
- [ ] Tüm tablo şemaları + seed data
- [ ] `BaseRepository` + 3 temel repo (personel, izin, belge)
- [ ] `Theme` sınıfı + ana pencere iskeleti

### Sprint 2 (1 hafta) — Personel CRUD
- [ ] `PersonelRepo` + `PersonelService`
- [ ] `PersonelListePage` + `PersonelEkleDialog`
- [ ] `KimlikPanel` (görüntüleme + düzenleme)
- [ ] TC doğrulama + validatörler

### Sprint 3 (1 hafta) — İzin Modülü
- [ ] `IzinRepo` + `IzinService` (bakiye hesaplama)
- [ ] `IzinPanel` + `IzinDialog`
- [ ] Çakışma kontrolü + limit kontrolü
- [ ] Pasif durum otomasyonu

### Sprint 4 (1 hafta) — Sağlık + Dozimetre
- [ ] `MuayeneRepo/Service` + `MuayenePanel`
- [ ] `DozimetreRepo/Service` + `DozimetrePanel`
- [ ] Doz araştırma formu PDF
- [ ] FHSZ puantaj

### Sprint 5 (1 hafta) — Nöbet
- [ ] Tüm nb_* repo'ları
- [ ] `NobetService` + algoritma
- [ ] Plan sayfası + takvim widget

### Sprint 6 (1 hafta) — Tamamlama
- [ ] Dashboard
- [ ] Belge yönetimi (lokal + Drive sync)
- [ ] Rapor (PDF/Excel çıktıları)
- [ ] Auth + kullanıcı yönetimi
- [ ] Testler

---

## 8. KORUNAN İŞ KURALLARI (DEĞIŞMEYECEKLER)

Mevcut koddan çıkarılan iş mantığı — yeni kodda da aynı:

```
İzin:
  657 SK md.102 yıllık hak: <1yıl=0, 1-10yıl=20, >10yıl=30 gün
  657 SK md.102 devir: min(kalan, hak, hak×2)
  Şua izni: Koşul A=30 iş günü, Koşul B=yok
  Ücretsiz/aylıksız izin veya >30 gün → personel pasif
  Çakışma kontrolü: (yeni_bas<=mevcut_bit) AND (yeni_bit>=mevcut_bas)

Dozimetre (Radyasyon Güvenliği Yönetmeliği):
  Hp(10) uyarı eşiği: 2.0 mSv/periyot
  Hp(10) tehlike eşiği: 5.0 mSv/periyot
  Yıllık limit (NDK): 20.0 mSv
  5 yıllık limit (NDK): 100.0 mSv
  Çalışma Koşulu A eşiği: 6.0 mSv/yıl
  Periyot sayısı: 4/yıl (RADAT)
  Doz aşımı → TAEK bildirimi zorunlu (30 gün)

Nöbet:
  Slot başı personel sayısı: birimine göre ayarlanır (genellikle 2)
  Aylık hedef = (iş günü - izin günü) × vardiya saati
  Tolerans: ±1 slot
  Max ardışık gün: birim ayarından gelir (genellikle 3)
  Tatil/hafta sonu: birim ayarına göre dahil/hariç

FHSZ:
  Dönem: 2 aylık, yılda 6 dönem
  Fiili çalışma saati: SUA hesabının girdisi
```
