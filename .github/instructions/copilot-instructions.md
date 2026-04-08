# RADPYS 2.0 — GitHub Copilot Yönergesi

Bu dosya Copilot'a projenin tüm kurallarını, mimarisini ve
kod üretim beklentilerini anlatır.
Öneri üretmeden önce bu dosyanın tamamını oku.

---

## 1. PROJE KİMLİĞİ

**RADPYS 2.0** — Radyoloji Bölümü Yönetim Sistemi.
Python 3.12 + PySide6 masaüstü uygulaması.
Hastane radyoloji birimindeki personel, cihaz, nöbet,
izin ve dozimetre takibini yönetir.

```
Teknoloji: Python 3.12 · PySide6 6.6+ · SQLite 3.40+
Test:      pytest
Veritabanı: data/radpys.db (SQLite, WAL modu)
```

---

## 2. KLASÖR YAPISI

```
radpys2/
├── main.py                  ← Giriş noktası
├── menus.json               ← Sidebar menü tanımları (BURAYA ekle yeni modül)
│
├── app/
│   ├── bootstrap.py         ← Başlatma omurgası (dizin/logging/db/qt)
│   ├── config.py            ← Tüm sabitler (iş kuralları dahil)
│   ├── exceptions.py        ← Exception hiyerarşisi
│   ├── validators.py        ← TC, tarih, zorunlu alan doğrulayıcıları
│   ├── module_registry.py   ← menus.json okuyucu + lazy sayfa yükleyici
│   ├── badge_functions.py   ← Sidebar badge DB sorguları
│   ├── security/            ← Yetki/policy/oturum yardımcıları
│   │   ├── permissions.py
│   │   ├── policy.py
│   │   └── session.py
│   ├── usecases/            ← İş akışları (service delegasyonu)
│   │   ├── personel/
│   │   ├── auth/
│   │   └── policy/
│   ├── services/
│   │   ├── personel_service.py
│   │   ├── auth_service.py
│   │   └── policy_service.py
│   └── db/
│       ├── database.py      ← Database sınıfı (tek bağlantı)
│       ├── migrations.py    ← Versiyonlu migration sistemi
│       ├── seed.py          ← Başlangıç verileri
│       └── repos/
│           ├── base.py      ← BaseRepo (sadece _db ve _new_id)
│           ├── personel_repo.py
│           ├── lookup_repo.py
│           ├── kullanici_repo.py
│           └── policy_repo.py
│
├── ui/
│   ├── theme.py             ← T nesnesi — tüm renkler buradan
│   ├── app_window.py        ← AppWindow (registry-driven, dokunma)
│   ├── components/          ← Reusable widget'lar
│   │   ├── buttons.py       ← PrimaryButton, DangerButton, GhostButton, IconButton
│   │   ├── cards.py         ← Card, StatCard
│   │   ├── badges.py        ← Badge
│   │   ├── alerts.py        ← AlertBar
│   │   ├── tables.py        ← DataTable
│   │   ├── forms.py         ← FormRow, SearchBar, LookupCombo
│   │   └── async_runner.py  ← AsyncRunner (tek QThread implementasyonu)
│   └── pages/
│       ├── placeholder.py   ← Henüz yazılmamış modüller için
│       ├── dashboard/
│       └── personel/
│           ├── panels/
│           │   └── kimlik_panel.py
│           ├── personel_detay.py
│           ├── personel_form.py
│           ├── personel_listesi.py
│           └── personel_page.py
│
└── tests/
    ├── test_validators.py
    ├── test_database.py
    ├── test_personel_service.py
    ├── test_auth_service.py
    ├── test_policy_service.py
    ├── test_personel_usecases.py
    ├── test_auth_usecases.py
    ├── test_policy_usecases.py
    └── test_security_permissions.py
```

---

## 3. MİMARİ KATMANLAR

### Katman sırası (yukarıdan aşağıya veri akar)

```
UI Widget  →  Service  →  UseCase  →  Repository  →  Database
```

**Kesin kurallar:**
- UI, Repository'e **hiç** erişmez. Sadece Service çağırır.
- Service, ham SQL yazmaz. UseCase/Repository delegasyonu yapar.
- UseCase, ham SQL yazmaz. Sadece Repository çağırır.
- Repository, iş mantığı içermez. Sadece SQL çalıştırır.
- `Database` sınıfı uygulama genelinde **tek** bağlantıdır.

---

## 4. VERİTABANI KATMANI

### 4.1 Database API

```python
from app.db.database import Database

db = Database("data/radpys.db")

# Tek kayıt — dict | None döner
row = db.fetchone("SELECT * FROM personel WHERE id=?", (pid,))

# Çok kayıt — list[dict] döner
rows = db.fetchall("SELECT * FROM personel WHERE durum=?", ("aktif",))

# Tek değer — skaler
count = db.fetchval("SELECT COUNT(*) FROM personel")

# Yazma (autocommit)
db.execute("INSERT INTO personel (id, tc_kimlik, ad) VALUES (?,?,?)", (pid, tc, ad))

# Atomik blok
with db.transaction():
    db.execute("INSERT INTO izin ...")
    db.execute("UPDATE personel ...")
    # hata → otomatik ROLLBACK
```

### 4.2 Tablo Listesi

| Tablo | PK | Açıklama |
|---|---|---|
| `personel` | `id` (UUID hex) | Tüm personel |
| `gorev_yeri` | `id` | Birimler + Koşul A/B |
| `izin` | `id` | İzin kayıtları |
| `muayene` | `id` | Sağlık muayeneleri |
| `fhsz` | `id` | FHSZ puantaj |
| `dozimetre` | `id` | Dozimetre ölçümleri |
| `doz_form` | `id` | Doz araştırma formu meta |
| `nb_birim` | `id` | Nöbet birimleri |
| `nb_birim_ayar` | `id` | Birim nöbet ayarları |
| `nb_vardiya` | `id` | Vardiya tanımları |
| `nb_personel` | `id` | Birim-personel ataması |
| `nb_tercih` | `id` | Personel nöbet tercihleri |
| `nb_plan` | `id` | Aylık nöbet planı |
| `nb_satir` | `id` | Plan satırları |
| `belge` | `id` | Belge arşivi (genel) |
| `lookup` | `id` | Dropdown verileri |
| `tatil` | `tarih` | Resmi + dini tatiller |
| `kullanici` | `id` | Auth kullanıcıları |

**UUID üretimi:**
```python
from uuid import uuid4
pk = uuid4().hex   # 32 karakterlik hex string
```

**Tarih formatı her zaman ISO-8601:**
```python
from app.validators import bugun, format_tarih
tarih_str = bugun()          # "2026-04-07"
tarih_str = format_tarih(d)  # date → "2026-04-07"
```

### 4.3 Repository Şablonu

```python
# app/db/repos/ornek_repo.py
from app.db.repos.base import BaseRepo
from app.validators import bugun


class OrnekRepo(BaseRepo):
    """ornek tablosu CRUD. Sadece SQL — iş mantığı yok."""

    def listele(self) -> list[dict]:
        return self._db.fetchall("SELECT * FROM ornek ORDER BY ad")

    def getir(self, pk: str) -> dict | None:
        return self._db.fetchone(
            "SELECT * FROM ornek WHERE id=?", (pk,)
        )

    def var_mi(self, benzersiz_alan: str) -> bool:
        return bool(self._db.fetchval(
            "SELECT 1 FROM ornek WHERE benzersiz_alan=?",
            (benzersiz_alan,)
        ))

    def ekle(self, veri: dict) -> str:
        pk = self._new_id()
        self._db.execute(
            "INSERT INTO ornek (id, ad, ...) VALUES (?,?,...)",
            (pk, veri["ad"], ...),
        )
        return pk

    def guncelle(self, pk: str, veri: dict) -> None:
        korunan = {"id", "olusturuldu"}
        v = {k: val for k, val in veri.items() if k not in korunan}
        if not v:
            return
        v["guncellendi"] = bugun()
        alanlar  = ", ".join(f"{k}=?" for k in v)
        degerler = list(v.values()) + [pk]
        self._db.execute(
            f"UPDATE ornek SET {alanlar} WHERE id=?",
            tuple(degerler),
        )
```

---

## 5. SERVİS KATMANI

### 5.1 Exception Hiyerarşisi

```
AppHatasi
├── DogrulamaHatasi          ← Girdi geçersiz
│   └── TCHatasi             ← TC Kimlik No hatalı
├── IsKuraliHatasi           ← İş kuralı ihlali
│   ├── LimitHatasi          ← İzin limiti aşıldı
│   ├── CakismaHatasi        ← Tarih çakışması
│   ├── PasifPersonelHatasi  ← Ayrılmış personel üzerinde işlem
│   └── YetkiHatasi          ← Yetki yetersiz
├── KayitBulunamadi          ← ID/TC DB'de yok
├── KayitZatenVar            ← UNIQUE ihlali
├── VTHatasi                 ← DB erişim sorunu
└── DosyaHatasi              ← Dosya okuma/yazma sorunu
```

**Servis metodları exception fırlatır, None/bool DÖNMEZ:**
```python
# DOĞRU — exception fırlatılır
def getir(self, pk: str) -> dict:
    row = self._repo.getir(pk)
    if not row:
        raise KayitBulunamadi(f"Kayıt bulunamadı: {pk}")
    return row

# YANLIŞ — None dönme
def getir(self, pk: str) -> dict | None:
    return self._repo.getir(pk)   # ← bunu yazma
```

### 5.2 Servis Şablonu

```python
# app/services/ornek_service.py
from app.db.database import Database
from app.db.repos.ornek_repo import OrnekRepo
from app.usecases.ornek.ornek_ekle import execute as ornek_ekle
from app.exceptions import KayitBulunamadi, KayitZatenVar, DogrulamaHatasi
from app.validators import zorunlu


class OrnekService:

    def __init__(self, db: Database):
        self._repo = OrnekRepo(db)

    def listele(self) -> list[dict]:
        return self._repo.listele()

    def getir(self, pk: str) -> dict:
        row = self._repo.getir(pk)
        if not row:
            raise KayitBulunamadi(f"Kayıt bulunamadı: {pk}")
        return row

    def ekle(self, veri: dict) -> str:
        return ornek_ekle(self._repo, veri)

    def guncelle(self, pk: str, veri: dict) -> None:
        self.getir(pk)          # varlık kontrolü
        self._repo.guncelle(pk, veri)
```

### 5.4 UseCase Şablonu

```python
# app/usecases/ornek/ornek_ekle.py
from app.exceptions import KayitZatenVar
from app.validators import zorunlu


def execute(repo, veri: dict) -> str:
    zorunlu(veri.get("ad"), "Ad")
    if repo.var_mi(veri["benzersiz_alan"]):
        raise KayitZatenVar("Bu kayıt zaten mevcut.")
    return repo.ekle(veri)
```

### 5.3 İş Kuralı Sabitleri

**Değerleri asla servis/repo dosyasına yazma — `app/config.py`'den oku:**

```python
from app.config import (
    # İzin (657 SK)
    YILLIK_HAK_1_10,    # = 20.0 gün
    YILLIK_HAK_10P,     # = 30.0 gün
    YILLIK_MAX_DEVIR,   # = 2.0  (devir katsayısı)
    PASIF_MIN_GUN,      # = 30   (bu günü aşanlar pasife alınır)
    PASIF_TIPLER,       # = {"ucretsiz", "ayliksiz"}
    SUA_HAK_GUN,        # = 30.0 iş günü (Koşul A)

    # Dozimetre (Radyasyon Güvenliği Yönetmeliği)
    HP10_UYARI,              # = 2.0  mSv/periyot
    HP10_TEHLIKE,            # = 5.0  mSv/periyot
    NDK_YILLIK,              # = 20.0 mSv
    NDK_BES_YILLIK,          # = 100.0 mSv
    NDK_CALISMA_A,           # = 6.0  mSv/yıl
    DOZIMETRE_PERIYOT_SAYISI,# = 4
    TAEK_BILDIRIM_GUN,       # = 30

    # Nöbet
    NOBET_GUNLUK_HEDEF_SAAT, # = 7.0
    NOBET_GONULLU_KATSAYI,   # = 1.2

    # FHSZ
    FHSZ_DONEM_SAYISI,       # = 6
)
```

---

## 6. UI KATMANI

### 6.1 Tema Sistemi

Tüm renkler `ui/theme.py` içindeki `T` nesnesinden gelir.
**Hiçbir yerde hex renk kodu veya inline CSS yazma.**

```python
from ui.theme import T

# DOĞRU
label.setStyleSheet(f"color:{T.text2}; background:{T.bg2};")
frame.setStyleSheet(f"border:1px solid {T.border};border-radius:{T.radius}px;")

# YANLIŞ — sabit renk
label.setStyleSheet("color:#6e88b0;")   # ← bunu yazma
```

**Renk referansı:**

| Değişken | Hex | Kullanım |
|---|---|---|
| `T.bg0` | `#0b0f14` | Uygulama zemini |
| `T.bg1` | `#101722` | Topbar, sidebar |
| `T.bg2` | `#141e2b` | Kart, panel |
| `T.bg3` | `#1a2636` | Hover, seçili satır |
| `T.bg4` | `#223247` | Input, progress track |
| `T.border` | `rgba(255,255,255,0.06)` | İnce kenarlık |
| `T.border2` | `rgba(255,255,255,0.12)` | Hover kenarlık |
| `T.text` | `#e6edf6` | Birincil metin |
| `T.text2` | `#b6c2d2` | İkincil metin |
| `T.text3` | `#7e8ca3` | Soluk metin |
| `T.text4` | `#4a5b73` | En soluk metin |
| `T.accent` | `#23c5b8` | Teal — primary action |
| `T.accent2` | `#45d7cd` | Teal açık |
| `T.green2` | `#34e58b` | Başarı |
| `T.red` | `#e24d5f` | Tehlike/hata |
| `T.red2` | `#ff6f84` | Tehlike açık |
| `T.amber` | `#e0a73a` | Uyarı |
| `T.amber2` | `#f6c356` | Uyarı açık |
| `T.purple` | `#2f7dd1` | Mavi vurgu |
| `T.teal2` | `#2cc8bf` | Bilgi/sağlık |

**`T.radius`, `T.radius_sm`, `T.input_h`, `T.icon_md`:**
```python
f"border-radius:{T.radius}px;"     # büyük kart: 12px
f"border-radius:{T.radius_sm}px;"  # buton/input: 9px
# T.input_h = 34  — tüm input kontrolleri bu yüksekliği kullanır
# T.icon_sm = 14, T.icon_md = 16, T.icon_lg = 20
```

### 6.2 Hazır Bileşenler

**Her zaman önce bunları kullan, sıfırdan yazma:**

```python
from ui.components import (
    PrimaryButton,   # Primary aksiyon
    DangerButton,    # Tehlikeli işlem
    SuccessButton,   # Onay/tamamlama
    GhostButton,     # İkincil/şeffaf işlem
    IconButton,      # Kare ikon butonu
    Card,            # Basit kart container
    SectionCard,     # Başlık + içerik bölüm kartı
    InfoCard,        # Etiket-değer satır kartı
    StatCard,        # İstatistik kartı (başlık + büyük sayı)
    Badge,           # Durum rozeti (aktif/pasif/uyarı...)
    AlertBar,        # Satır içi uyarı bandı (dialog açmaz)
    DataTable,       # Sıralanabilir + filtrelenebilir tablo
    TextField,       # Metin girişi (+ ikon)
    PasswordField,   # Şifre alanı (göster/gizle)
    DateField,       # Tarih alanı (QDateEdit)
    ComboField,      # Standart seçim alanı
    TextAreaField,   # Çok satırlı metin
    IntField,        # QSpinBox
    FloatField,      # QDoubleSpinBox
    ReadonlyField,   # Salt-okunur alan
    CheckField,      # QCheckBox alanı
    RadioGroup,      # Radyo grup alanı
    FormGroup,       # Form bölüm container'ı
    SearchBar,       # Arama kutusu (+ ikon)
    FormRow,         # Legacy yatay satır (geriye uyumluluk)
    LookupCombo,     # Legacy dropdown (geriye uyumluluk)
    AsyncRunner,     # Arkaplan işlem — TEK QThread implementasyonu
)
```

### 6.3 AsyncRunner — QThread Kuralı

**Projede yalnızca `AsyncRunner` kullanılır.**
`class XyzLoader(QThread)` veya `class XyzWorker(QThread)` yazma.

```python
from ui.components.async_runner import AsyncRunner

# DOĞRU
def _yukle(self):
    AsyncRunner(
        fn       = lambda: self._svc.listele(),
        on_done  = self._goster,
        on_error = lambda msg: self._alert.goster(msg),
        parent   = self,
    ).start()

def _goster(self, veri: list[dict]):
    self._tablo.set_veri(veri)

# YANLIŞ — özel QThread subclass
class _PersonelLoader(QThread):   # ← bunu yazma
    ...
```

### 6.4 AlertBar — Hata Gösterimi

Dialog açma. `AlertBar` ile satır içinde göster.

```python
# DOĞRU
self._alert = AlertBar(self)
try:
    pid = self._svc.ekle(veri)
except AppHatasi as e:
    self._alert.goster(str(e), "warning")
except Exception as e:
    self._alert.goster(f"Beklenmeyen hata: {e}", "danger")

# AlertBar türleri: "danger" | "warning" | "success" | "info"

# YANLIŞ — dialog açma
QMessageBox.critical(self, "Hata", str(e))   # ← bunu yazma
```

### 6.5 Sayfa Widget Şablonu

```python
# ui/pages/ornek/ornek_page.py
from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from ui.theme import T
from ui.components import PrimaryButton, SearchBar, DataTable, AlertBar
from ui.components.async_runner import AsyncRunner
from app.db.database import Database
from app.services.ornek_service import OrnekService


class OrnekPage(QWidget):

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self._svc   = OrnekService(db)
        self._alert = AlertBar(self)
        self.setStyleSheet(f"background:{T.bg0};")
        self._build()
        self._yukle()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)
        lay.addWidget(self._alert)
        # ... widget'lar ekle

    def _yukle(self):
        AsyncRunner(
            fn       = lambda: self._svc.listele(),
            on_done  = self._goster,
            on_error = lambda m: self._alert.goster(m),
            parent   = self,
        ).start()

    def _goster(self, veri: list[dict]):
        self._tablo.set_veri(veri)
```

---

## 7. YENİ MODÜL EKLEME (COPILOT İÇİN ADIM ADIM)

### Adım 1 — `menus.json`'a ekle

```json
{
  "id":       "stok",
  "label":    "Stok Takip",
    "icon":     "belgeler",
  "bolum":    "sistem",
  "sira":     15,
  "page_cls": "ui.pages.stok.stok_page.StokPage"
}
```

### Adım 2 — Repository yaz

```
app/db/repos/stok_repo.py
```
Şablon: `BaseRepo` miras al, sadece SQL.

### Adım 3 — Servis yaz

```
app/services/stok_service.py
```
Şablon: service, use-case fonksiyonlarına delege eder.

### Adım 4 — UseCase yaz

```
app/usecases/stok/__init__.py
app/usecases/stok/stok_ekle.py
app/usecases/stok/stok_guncelle.py
```
Şablon: iş akışları burada toplanır; SQL yok, sadece repo çağrısı.

### Adım 5 — Sayfa yaz

```
ui/pages/stok/__init__.py
ui/pages/stok/stok_page.py
```
Şablon: `QWidget`, constructor'da `StokService(db)`, `AsyncRunner` ile yükle.

### Adım 6 — Test yaz

```
tests/test_stok_service.py
tests/test_stok_usecases.py
```
Service + use-case public akışları için test yaz.

### Badge gerekiyorsa — Adım 7

`app/badge_functions.py`'e ekle:
```python
def stok_kritik(db) -> str | None:
    n = db.fetchval("SELECT COUNT(*) FROM stok WHERE miktar < esik")
    return str(n) if n else None

BADGE_FN["stok_kritik"] = stok_kritik
```

`menus.json`'da:
```json
"badge_id":   "stok_kritik",
"badge_renk": "#e83a5a"
```

**`app_window.py`, `main.py` — normal modül ekleme akışında dokunma.**
`module_registry.py` sadece kayıt sistemiyle ilgili zorunlu ihtiyaçta güncellenir.

---

## 8. YASAK KALIPLAR

Copilot bu kalıpları **hiçbir zaman** üretmez:

```python
# ❌ Sabit renk — T nesnesini kullan
widget.setStyleSheet("color:#6e88b0;")

# ❌ Özel QThread subclass — AsyncRunner kullan
class _Loader(QThread): ...

# ❌ QMessageBox — AlertBar kullan
QMessageBox.critical(self, "Hata", msg)

# ❌ None dönen getir — exception fırlat
def getir(self, pk) -> dict | None:
    return self._repo.getir(pk)

# ❌ Serviste ham SQL
class OrnekService:
    def listele(self):
        return self._db.fetchall("SELECT ...")  # SQL servise girmez

# ❌ Menüde emoji ikon kullanımı
{"icon": "📦"}  # menus.json için yasak, ui/icons.py anahtarı kullan

# ❌ Serviste ağır iş akışı
def ekle(self, veri):
    # 80+ satır doğrulama, dönüşüm, kural
    ...  # use-case katmanına taşı

# ❌ UI'da repo erişimi
class OrnekPage(QWidget):
    def __init__(self, db):
        self._repo = PersonelRepo(db)  # UI repo'ya erişemez

# ❌ Hesaplanan değer DB'ye yazma
db.execute("UPDATE izin_bilgi SET kalan=? WHERE tc=?", (kalan, tc))
# Bakiye, yaş, kalan gün — bunlar serviste hesaplanır, DB'ye yazılmaz

# ❌ Magic number iş kuralı sabiti
if gun > 30:   # 30 nedir? PASIF_MIN_GUN kullan
    ...

# ❌ Personeli fiziksel silme
self._repo.sil(pid)   # pasife_al() kullan

# ❌ AdSoyad DB'ye kopyalama
db.execute("INSERT INTO fhsz (..., ad_soyad) VALUES (..., ?)", (personel["ad"],))
# JOIN kullan, kopyalama
```

---

## 9. ZORUNLU KALIPLAR

Copilot her zaman bu kalıpları üretir:

```python
# ✅ Primary key
pk = self._new_id()   # uuid4().hex

# ✅ Tarih
from app.validators import bugun, format_tarih, parse_tarih
tarih = bugun()                        # "2026-04-07"
goruntule = format_tarih(d, ui=True)   # "07.04.2026"

# ✅ İş kuralı sabiti
from app.config import PASIF_MIN_GUN, HP10_UYARI
if gun > PASIF_MIN_GUN: ...

# ✅ Exception fırlat
if not row:
    raise KayitBulunamadi(f"Personel bulunamadı: {pk}")

# ✅ Tema rengi
self.setStyleSheet(f"background:{T.bg2}; border:1px solid {T.border};")

# ✅ Async işlem
AsyncRunner(fn=lambda: svc.listele(), on_done=self._goster, parent=self).start()

# ✅ Atomik yazma
with db.transaction():
    db.execute("INSERT ...")
    db.execute("UPDATE ...")

# ✅ FK JOIN
rows = db.fetchall(
    "SELECT p.*, gy.ad AS gorev_yeri_ad "
    "FROM personel p "
    "LEFT JOIN gorev_yeri gy ON p.gorev_yeri_id = gy.id"
)

# ✅ Service -> UseCase delegasyonu
from app.usecases.personel.personel_ekle import execute as personel_ekle

def ekle(self, veri: dict) -> str:
    return personel_ekle(self._repo, self._gy_repo, veri)
```

---

## 10. TEST YAZMA KURALLARI

```python
# tests/test_ornek_service.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.db.database import Database
from app.db.migrations import run as migrate
from app.services.ornek_service import OrnekService
from app.exceptions import KayitBulunamadi, KayitZatenVar


@pytest.fixture
def db(tmp_path):
    d = Database(tmp_path / "test.db")
    migrate(d)
    yield d
    d.close()

@pytest.fixture
def svc(db):
    return OrnekService(db)


class TestEkle:
    def test_basarili(self, svc): ...
    def test_ayni_kayit_tekrar_eklenemez(self, svc): ...
    def test_bos_zorunlu_alan(self, svc): ...

class TestGetir:
    def test_var_olan(self, svc): ...
    def test_olmayan_hata_firlatir(self, svc):
        with pytest.raises(KayitBulunamadi):
            svc.getir("olmayan-id")
```

Her public servis metodu için en az 2 test yazılır:
- Başarılı senaryo
- Hata/edge case senaryosu

Use-case katmanı için de aynı kural geçerlidir.

---

## 11. MIGRATION YAZMA KURALI

Yeni tablo eklenince `app/db/migrations.py`'deki `HEDEF_VERSIYON` artırılır
ve yeni `_vN(db)` fonksiyonu eklenir:

```python
HEDEF_VERSIYON = 2   # 1'den 2'ye artır

def _v2(db: Database) -> None:
    """v2 — Stok tablosu eklendi."""
    db.execute("""
    CREATE TABLE stok (
        id      TEXT PRIMARY KEY,
        ad      TEXT NOT NULL,
        miktar  INTEGER NOT NULL DEFAULT 0,
        esik    INTEGER NOT NULL DEFAULT 5,
        olusturuldu TEXT NOT NULL DEFAULT (date('now'))
    )
    """)

_MIGRATIONS = {1: _v1, 2: _v2}   # buraya da ekle
```

---

## 12. COPILOT KISA BAŞVURU

| İstersen... | Şunu kullan |
|---|---|
| Renk | `T.bg0` … `T.teal2` |
| Birincil buton | `PrimaryButton("Kaydet")` |
| Tehlike butonu | `DangerButton("Sil")` |
| Hata göster | `self._alert.goster(str(e))` |
| Arkaplan işlem | `AsyncRunner(fn=..., on_done=...).start()` |
| Tablo | `DataTable()` + `set_veri([...])` |
| Exception | `raise KayitBulunamadi(...)` |
| Tarih bugün | `bugun()` → `"2026-04-07"` |
| Yeni UUID | `self._new_id()` |
| DB tek kayıt | `db.fetchone(sql, params)` |
| DB çok kayıt | `db.fetchall(sql, params)` |
| DB skaler | `db.fetchval(sql, params)` |
| Atomik yazma | `with db.transaction():` |
| İş kuralı sabiti | `from app.config import ...` |
