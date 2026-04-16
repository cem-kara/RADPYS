# Nobet UI Refactor Devam Notu (2026-04-16)

## Su Anki Durum
- Son tamamlanan asama:
  - Migration v12 tamamlandi.
  - Repo ve servis tarafinda vardiya sablon + max_personel destegi eklendi.
  - Testler calisti: test_nobet_service.py (10 passed), test_database.py (15 passed).
- Acik dosya/odak:
  - ui/pages/nobet/nobet_plan_page.py
  - ui/pages/yonetim/ayarlar_page.py

## Kullanici Karari (Net Istenen)
- Birim kural kartinda sadece personel ile ilgili alanlar kalsin.
- Personel disindaki tum yonetim alanlari Ayarlar sayfasina tasinsin.

## Bu Dakikada Tam Olarak Nerede Duruldu
- Kod degisikligine baslamadan once mevcut dosyalar tekrar okundu.
- Asagidaki hedef degisiklikler uygulanacak asamada duruldu.

## Sonraki Adimlar (Uygulama Listesi)
1) Nobet ekrani sadeleme
- Dosya: ui/pages/nobet/nobet_plan_page.py
- Kosullar sekmesinden sablon yonetim karti tamamen kaldirilacak.
- Birim kural kartindan personel disi alanlar kaldirilacak.
- Personel kartinda sadece personel bazli alanlar kalacak (tolerans personelden cikacak).

2) Ayarlar tarafina tasima
- Yeni sekme/widget: ui/pages/yonetim/nobet_sablon_tab.py
- Icerik:
  - Global sablon liste/ekle/pasife al
  - Birime sablon ata
  - Birim vardiya listesi + kaldir
  - Sure alani UI'da olmayacak, baslangic/bitisten otomatik hesaplanacak
- Ayarlar entegrasyonu:
  - ui/pages/yonetim/ayarlar_page.py icine yeni tab ekle: Nobet Sablonlari

3) Is kurali sadeleme
- Arefe baslangic saati UI'dan kaldirilacak, servis cagrilarinda sabit 13:00 kullanilacak.
- Personel tolerans saati UI ve kayit akisindan kaldirilacak.

4) Testler
- Nobet servis testleri tekrar kosulacak.
- Gerekirse UI tarafi smoke acilisi manuel kontrol edilecek.

## Hizli Calisma Komutlari
- Test:
  - .venv\Scripts\python.exe -m pytest tests/test_nobet_service.py -q --tb=short
  - .venv\Scripts\python.exe -m pytest tests/test_database.py -q --tb=short
- Uygulama:
  - .venv\Scripts\python.exe main.py

## Not
- Bulut tarafina dogrudan push/backup bu oturumdan otomatik yapilamiyor.
- Bu dosya uzerinden kaldigimiz yerden ayni planla devam edilebilir.
