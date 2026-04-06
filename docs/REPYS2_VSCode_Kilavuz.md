# REPYS 2.0 — VSCode Geliştirme Ortamı Kurulum ve Kullanım Kılavuzu

---

## 1. KURULUM

### 1.1 Gerekli Programlar

Sırayla kur, her birini bitirmeden diğerine geçme:

**Python 3.12**
- https://www.python.org/downloads/ → "Windows installer (64-bit)"
- Kurulum sırasında **"Add Python to PATH"** kutusunu işaretle
- Kurulduktan sonra `Win+R` → `cmd` → `python --version` yaz, `Python 3.12.x` görünmeli

**Git**
- https://git-scm.com/download/win → varsayılan seçeneklerle kur

**VSCode**
- https://code.visualstudio.com/ → "Download for Windows"
- Kurulum sırasında "Add to PATH" seçeneğini işaretle

---

### 1.2 Projeyi Aç

```
1. repys2_sprint1.zip dosyasını çıkart
   Örnek: C:\Projeler\repys2\

2. VSCode'u aç
   Dosya → Klasör Aç → C:\Projeler\repys2\ seç
```

---

### 1.3 VSCode Eklentileri

VSCode açıkken sol kenar çubuğunda **Extensions** ikonuna tıkla (veya `Ctrl+Shift+X`).
Arama kutusuna her birini yazıp "Install" düğmesine bas:

| Eklenti | Kimden | Neden |
|---------|--------|-------|
| `Python` | Microsoft | Temel Python desteği |
| `Pylance` | Microsoft | Otomatik tamamlama, tip denetimi |
| `Ruff` | Astral Software | Hızlı linter + formatter |
| `Even Better TOML` | tamasfe | pyproject.toml desteği |
| `GitLens` | GitKraken | Git geçmişi görselleştirme |
| `Todo Tree` | Gruntfuggly | # TODO yorumları listesi |

---

### 1.4 Virtual Environment Oluştur

VSCode'da terminal aç: **Terminal → New Terminal** (veya `Ctrl+Backtick`)

```bash
# Proje klasöründe olduğunu doğrula
# C:\Projeler\repys2> görünmeli

# venv oluştur
python -m venv .venv

# Aktive et (Windows)
.venv\Scripts\activate

# Prompt değişmeli: (.venv) C:\Projeler\repys2>
# Aktive olduğunu gösterir

# Bağımlılıkları yükle
pip install -r requirements.txt

# Test et
python -m pytest tests/ -v
# 44 passed görünmeli
```

---

### 1.5 VSCode'u venv ile Tanıştır

`Ctrl+Shift+P` → **Python: Select Interpreter** yaz → Enter
`.venv\Scripts\python.exe` seçeneğini seç

---

### 1.6 Workspace Ayarları

Proje kökünde `.vscode/settings.json` dosyasını oluştur:

```
repys2/
└── .vscode/
    └── settings.json   ← bu dosyayı oluşturacaksın
```

İçeriği:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,

    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": "explicit",
            "source.organizeImports.ruff": "explicit"
        }
    },

    "python.analysis.typeCheckingMode": "basic",
    "python.analysis.autoImportCompletions": true,
    "python.analysis.extraPaths": ["${workspaceFolder}"],

    "editor.rulers": [88],
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "files.eol": "\n",
    "files.encoding": "utf8",

    "editor.minimap.enabled": false,
    "editor.stickyScroll.enabled": true,
    "breadcrumbs.enabled": true,

    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "python.testing.unittestEnabled": false
}
```

---

### 1.7 Hata Ayıklama Yapılandırması

`.vscode/launch.json` dosyasını oluştur:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "REPYS Çalıştır",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "Testleri Hata Ayıkla",
            "type": "debugpy",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v", "--tb=short"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

---

### 1.8 pyproject.toml (Ruff + pytest yapılandırması)

Proje kökünde `pyproject.toml` oluştur:

```toml
[tool.ruff]
target-version = "py312"
line-length = 88
src = ["app", "ui", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"]   # uzun satırları Ruff halleder

[tool.ruff.lint.isort]
known-first-party = ["app", "ui"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

---

## 2. GÜNLÜK KULLANIM

### 2.1 Projeyi Her Gün Açarken

```bash
# Terminal aç (Ctrl+Backtick)
# venv aktif olup olmadığına bak — (.venv) görünmeli
# Görünmüyorsa:
.venv\Scripts\activate
```

---

### 2.2 Uygulamayı Çalıştır

**Yöntem 1 — F5 tuşu** (önerilen)
- Sol kenar çubuğunda **Run and Debug** ikonu (▶ ile böcek)
- Üstte "REPYS Çalıştır" seçili olmalı
- **F5** bas

**Yöntem 2 — Terminal**
```bash
python main.py
```

---

### 2.3 Testleri Çalıştır

**Hızlı — Terminal:**
```bash
# Tüm testler
python -m pytest tests/ -v

# Tek dosya
python -m pytest tests/test_validators.py -v

# Tek test
python -m pytest tests/test_validators.py::TestTCDogrula::test_gecerli_tc -v

# Başarısız testler tekrar
python -m pytest tests/ --lf

# Çıktıyla birlikte (print görmek için)
python -m pytest tests/ -v -s
```

**VSCode Test Paneli:**
- Sol kenar çubuğunda **Testing** ikonu (şişe şeklinde)
- Testleri listeler, tek tek veya hepsini çalıştırabilirsin

---

### 2.4 Klavye Kısayolları (Önemli Olanlar)

| Kısayol | Ne yapar |
|---------|----------|
| `Ctrl+P` | Dosya ara ve aç |
| `Ctrl+Shift+P` | Komut paleti |
| `Ctrl+Backtick` | Terminal aç/kapat |
| `Ctrl+Shift+E` | Dosya gezgini |
| `Ctrl+Shift+F` | Tüm dosyalarda ara |
| `Ctrl+Shift+G` | Git paneli |
| `F5` | Hata ayıklayıcıyla çalıştır |
| `F9` | Breakpoint ekle/kaldır |
| `F10` | Adım adım ilerle (step over) |
| `F11` | Fonksiyon içine gir (step into) |
| `Shift+F5` | Hata ayıklamayı durdur |
| `Ctrl+.` | Hızlı düzeltme önerisi |
| `Alt+Shift+F` | Dosyayı formatla |
| `Ctrl+K Ctrl+C` | Satırı yorum yap |
| `Ctrl+K Ctrl+U` | Yorum kaldır |
| `Ctrl+D` | Aynı kelimeyi seç (çoklu imleç) |
| `Alt+↑/↓` | Satırı yukarı/aşağı taşı |
| `F2` | Yeniden adlandır (tüm dosyalarda) |
| `F12` | Tanıma git |
| `Alt+F12` | Tanımı önizle |
| `Shift+F12` | Tüm kullanımları bul |

---

### 2.5 Breakpoint ile Hata Ayıklama

1. Hata araştırmak istediğin satırın soluna tıkla → kırmızı nokta çıkar
2. `F5` ile çalıştır
3. Program o satırda durunca:
   - **Variables** panelinde tüm değişkenleri gör
   - **Watch** paneline `veri["personel_id"]` gibi ifadeler ekle
   - **Debug Console**'a kod yaz: `db.fetchall("SELECT * FROM personel")`
   - `F10` → bir sonraki satıra geç
   - `F11` → fonksiyon içine gir
   - `Shift+F5` → durdur

---

## 3. YENİ KOD YAZARKEN İZLENECEK YOLLAR

### 3.1 Yeni Sprint — Yeni Dosyalar

**Örnek: Sprint 2 — PersonelRepo ekleyeceğiz**

```
repys2/
└── app/
    └── db/
        └── repos/
            └── personel_repo.py   ← yeni dosya
```

Her yeni repo için şablon:

```python
# app/db/repos/personel_repo.py
from app.db.repos.base import BaseRepo


class PersonelRepo(BaseRepo):

    def listele(self, aktif_only: bool = True) -> list[dict]:
        sql = "SELECT * FROM personel"
        if aktif_only:
            sql += " WHERE durum = 'aktif'"
        sql += " ORDER BY soyad, ad"
        return self._db.fetchall(sql)

    def getir(self, personel_id: str) -> dict | None:
        return self._db.fetchone(
            "SELECT * FROM personel WHERE id = ?",
            (personel_id,)
        )

    def tc_ile_getir(self, tc: str) -> dict | None:
        return self._db.fetchone(
            "SELECT * FROM personel WHERE tc_kimlik = ?",
            (tc,)
        )

    def ekle(self, veri: dict) -> str:
        pid = self._new_id()
        self._db.execute(
            """INSERT INTO personel
               (id, tc_kimlik, ad, soyad, durum)
               VALUES (?, ?, ?, ?, 'aktif')""",
            (pid, veri["tc_kimlik"], veri["ad"], veri["soyad"]),
        )
        return pid

    def guncelle(self, personel_id: str, veri: dict) -> None:
        from app.validators import bugun
        alanlar = [f"{k} = ?" for k in veri if k != "id"]
        degerler = [v for k, v in veri.items() if k != "id"]
        degerler.append(bugun())
        degerler.append(personel_id)
        self._db.execute(
            f"UPDATE personel SET {', '.join(alanlar)}, guncellendi = ?"
            f" WHERE id = ?",
            tuple(degerler),
        )
```

---

### 3.2 Yeni Servis — Şablon

```python
# app/services/personel_service.py
from app.db.database import Database
from app.db.repos.personel_repo import PersonelRepo
from app.exceptions import KayitBulunamadi, DogrulamaHatasi, KayitZatenVar
from app.validators import tc_dogrula_veya_hata, zorunlu


class PersonelService:

    def __init__(self, db: Database):
        self._repo = PersonelRepo(db)

    def listele(self, aktif_only: bool = True) -> list[dict]:
        return self._repo.listele(aktif_only=aktif_only)

    def getir(self, personel_id: str) -> dict:
        p = self._repo.getir(personel_id)
        if not p:
            raise KayitBulunamadi(f"Personel bulunamadı: {personel_id}")
        return p

    def ekle(self, veri: dict) -> str:
        tc = tc_dogrula_veya_hata(veri.get("tc_kimlik", ""))
        zorunlu(veri.get("ad"), "Ad")
        zorunlu(veri.get("soyad"), "Soyad")
        if self._repo.tc_ile_getir(tc):
            raise KayitZatenVar(f"Bu TC zaten kayıtlı: {tc}")
        return self._repo.ekle(veri)
```

---

### 3.3 Yeni Test — Şablon

Her yeni servis/repo için mutlaka test yaz:

```python
# tests/test_personel_service.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.db.database import Database
from app.db.migrations import run as migration_calistir
from app.services.personel_service import PersonelService
from app.exceptions import KayitZatenVar, TCHatasi


@pytest.fixture
def svc(tmp_path):
    db = Database(tmp_path / "test.db")
    migration_calistir(db)
    yield PersonelService(db)
    db.close()


def test_personel_ekle(svc):
    pid = svc.ekle({
        "tc_kimlik": "10000000146",
        "ad":        "Ali",
        "soyad":     "Kaya",
    })
    assert pid is not None
    p = svc.getir(pid)
    assert p["ad"] == "Ali"
    assert p["tc_kimlik"] == "10000000146"


def test_ayni_tc_tekrar_eklenemez(svc):
    svc.ekle({"tc_kimlik": "10000000146", "ad": "Ali", "soyad": "Kaya"})
    with pytest.raises(KayitZatenVar):
        svc.ekle({"tc_kimlik": "10000000146", "ad": "Veli", "soyad": "Kaya"})


def test_gecersiz_tc(svc):
    with pytest.raises(TCHatasi):
        svc.ekle({"tc_kimlik": "12345678900", "ad": "X", "soyad": "Y"})
```

---

### 3.4 Yeni UI Sayfası — Şablon

```python
# ui/pages/personel/personel_page.py
from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from ui.components import PrimaryButton, SearchBar, DataTable, AlertBar
from ui.components.async_runner import AsyncRunner
from ui.theme import T
from app.db.database import Database
from app.services.personel_service import PersonelService


class PersonelPage(QWidget):

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self._svc   = PersonelService(db)
        self._alert = AlertBar(self)
        self._build()
        self._yukle()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        # Üst bar: başlık + arama + yeni buton
        ust = QHBoxLayout()
        self._arama = SearchBar("Personel ara…")
        self._arama.textChanged.connect(self._tablo.ara)
        btn_yeni = PrimaryButton("+ Yeni Personel")
        btn_yeni.clicked.connect(self._yeni_personel)
        ust.addWidget(self._arama, 1)
        ust.addWidget(btn_yeni)
        lay.addLayout(ust)

        # Uyarı bandı
        lay.addWidget(self._alert)

        # Tablo
        self._tablo = DataTable()
        self._tablo.kur_kolonlar([
            ("tc_kimlik", "TC Kimlik",   120),
            ("ad",        "Ad",          120),
            ("soyad",     "Soyad",       120),
            ("kadro_unvani", "Unvan",    160),
            ("durum",     "Durum",        80),
        ], geren="kadro_unvani")
        self._tablo.doubleClicked.connect(self._detay_ac)
        lay.addWidget(self._tablo, 1)

    def _yukle(self):
        def _cek():
            return self._svc.listele()

        def _goster(veri):
            self._tablo.set_veri(veri)

        def _hata(msg):
            self._alert.goster(f"Yükleme hatası: {msg}")

        AsyncRunner(fn=_cek, on_done=_goster, on_error=_hata, parent=self).start()

    def _yeni_personel(self):
        # Sprint 2'de PersonelForm dialog açılacak
        pass

    def _detay_ac(self):
        satir = self._tablo.secili_satir()
        if satir:
            # Sprint 2'de PersonelDetay sayfasına yönlendirecek
            pass
```

---

## 4. SPRINT ÇALIŞMA DÜZENİ

Her sprint başında:

```bash
# 1. Testlerin geçtiğini doğrula
python -m pytest tests/ -v

# 2. Yeni branch aç (Git kullanıyorsan)
git checkout -b sprint-2-personel-crud
```

Sprint boyunca:

```bash
# Her dosya kaydedildiğinde Ruff otomatik formatlıyor
# (settings.json'da formatOnSave: true)

# Yazan her yeni fonksiyon için hemen test yaz
# Test önce başarısız olmalı, sonra kodu yaz, test geçmeli (TDD)

# Düzenli çalıştır
python -m pytest tests/ -v --tb=short
```

Sprint bitiminde:

```bash
# Tüm testler geçiyor mu?
python -m pytest tests/ -v

# Uygulama açılıyor mu?
python main.py

# Git commit
git add .
git commit -m "sprint-2: personel CRUD tamamlandı"
```

---

## 5. SIK KARŞILAŞILAN SORUNLAR

### "ModuleNotFoundError: No module named 'app'"
```bash
# PYTHONPATH ayarlanmamış — ya:
# a) Terminalde proje kökündeyken çalıştır
# b) settings.json'daki extraPaths doğru mu kontrol et
# c) Ya da:
cd C:\Projeler\repys2
python main.py
```

### "venv aktif değil"
```bash
.venv\Scripts\activate
# Sonra tekrar dene
```

### "PySide6 kurulu değil"
```bash
# venv aktifken:
pip install PySide6
```

### "sqlite3.OperationalError: no such table"
```bash
# Migration çalışmamış — data/ klasöründeki repys.db'yi sil
# Uygulama yeniden açılınca migration otomatik çalışır
del data\repys.db
python main.py
```

### "Test görünmüyor VSCode'da"
```
Ctrl+Shift+P → Python: Configure Tests → pytest → tests klasörü seç
```

---

## 6. DOSYA YAPISINDAKİ KURALLAR

```
app/config.py          → Sabitler buraya, başka yere yazılmaz
app/exceptions.py      → Tüm exception'lar buraya
app/validators.py      → Doğrulama fonksiyonları buraya
app/db/repos/          → Tek tablo = tek dosya, SQL burada
app/services/          → İş mantığı burada, SQL yok
ui/components/         → Reusable widget'lar buraya
ui/pages/              → Sayfa widget'ları buraya

YASAK:
  × ui/ dosyasında direkt SQL yazmak
  × repo/ dosyasında if/else iş mantığı
  × SonucYonetici — try/except + exception kullan
  × setProperty("style-role") — artık yok
  × 20. farklı QThread subclass — AsyncRunner kullan
```

---

## 7. SPRINT PLANI HATIRLATICI

```
Sprint 1 ✅  Altyapı (bu sprint — 44 test geçti)
Sprint 2     PersonelRepo + PersonelService + PersonelPage + KimlikPanel
Sprint 3     IzinRepo + IzinService (bakiye hesaplama) + IzinPanel
Sprint 4     MuayeneRepo/Service + DozimetreRepo/Service + FHSZ
Sprint 5     NobetService (algoritma) + PlanPage + TakvimWidget
Sprint 6     Dashboard + BelgeService + Auth + Raporlar
```

Her sprint başında bu kılavuza dön, "Sprint Çalışma Düzeni" bölümünden başla.
