# RADPYS 2.0

RADPYS 2.0, radyoloji bolumu operasyonlarini yoneten Python tabanli masaustu uygulamadir.

Temel teknolojiler:
- Python 3.12
- PySide6
- SQLite (WAL)
- pytest

## Mimari

Proje cekirdegi katmanli yapiya gore organize edilir:

UI Widget -> Service -> UseCase -> Repository -> Database

Temel kurallar:
- UI, repository katmanina dogrudan erismez.
- Service SQL yazmaz, use-case ve repository uzerinden ilerler.
- Repository sadece SQL calistirir, is kurali barindirmez.
- Database sinifi uygulama genelinde tek baglanti merkezidir.

## Iskelet Dizin Yapisi

- main.py: uygulama giris noktasi
- app/bootstrap.py: baslatma omurgasi (dizin, logging, db, Qt hazirlik)
- app/config.py: sabitler ve is kurali konfigurasyonu
- app/exceptions.py: uygulama hata hiyerarsisi
- app/validators.py: dogrulama yardimcilari
- app/security/: yetki, policy ve oturum yardimcilari
- app/usecases/: is akisi katmani
- app/services/: UI'nin kullandigi servis API katmani
- app/db/: database, migration ve repository katmani
- app/module_registry.py + menus.json: modul kayit sistemi
- ui/: PySide6 bileşenleri ve sayfalar
- tests/: servis/use-case/cekirdek regresyon testleri

## Kurulum

### 1) Sanal ortam

```powershell
uv python install 3.12
uv venv .venv --python 3.12
.\.venv\Scripts\activate
```

### 2) Bagimliliklar

```powershell
python -m pip install -r requirements.txt
```

### 3) Uygulamayi calistirma

```powershell
python main.py
```

## Test Calistirma

```powershell
python -m pytest -v
```

## Dokumanlar

Bu repository icinde ayri bir `docs/` klasoru bulunmamaktadir.
Teknik yonergeler ve mimari beklentiler icin su dosyalara bakin:

- .github/instructions/copilot-instructions.md
- README.md (bu dosya)

## Katki ve Guvenlik

- Katki sureci: CONTRIBUTING.md
- Guvenlik bildirimi: SECURITY.md

## Lisans

MIT License. Ayrinti icin LICENSE dosyasina bakiniz.
