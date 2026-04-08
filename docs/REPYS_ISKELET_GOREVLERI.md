# REPYS Iskelet Gorevleri Dokumani

Bu dokuman, REPYS 2.0 projesindeki cekirdek iskelet dosyalarinin ne is yaptigini net ve hizli okunur sekilde aciklar.

Hedef: Sayfalardan bagimsiz, uzun omurlu ve genisletilebilir bir omurgayi ortak referansa donusturmek.

## 1) Genel Mimari Akis

Veri ve kontrol akisi su sirayla ilerler:

UI Widget -> Service -> UseCase -> Repository -> Database

Temel ilke:
- UI, Repository katmanina dogrudan erismez.
- Service SQL yazmaz.
- Repository is kurali vermez, sadece SQL calistirir.
- Database sinifi tek baglanti merkezidir.

## 2) Baslatma ve Uygulama Omurgasi

### main.py
Gorevi:
- Uygulamayi baslatmak.
- Bootstrap yardimcilari ile altyapiyi hazirlayip UI akisina gecmek.

Sorumluluklari:
- Baslangic hazirligini tetiklemek
- DB baglantisini almak
- Login akisini acmak
- Ana pencereyi baslatmak
- Cikis surecinde DB baglantisini kapatmak

### app/bootstrap.py
Gorevi:
- main.py icindeki baslatma adimlarini tek noktada toplamak.

Sorumluluklari:
- Zorunlu dizinleri olusturmak
- Logging altyapisini kurmak
- Database + migration + RBAC policy yuklemesini yapmak
- Qt uygulama nesnesini ve temayi hazirlamak

## 3) Konfigurasyon, Hata ve Dogrulama Omurgasi

### app/config.py
Gorevi:
- Uygulama capindaki tum sabitleri tek kaynakta tutmak.

Sorumluluklari:
- Dizin/yol sabitleri
- Is kurali sabitleri
- RBAC rol/yetki sabitleri
- Tarih formatlari
- Lookup kategori sabitleri

### app/exceptions.py
Gorevi:
- Uygulama hata hiyerarsisini standartlastirmak.

Sorumluluklari:
- Dogrulama hatalari
- Is kurali hatalari
- Kayit bulunamadi / kayit zaten var
- Sistem hatalari

### app/validators.py
Gorevi:
- Tekrarlanan dogrulama ve tarih yardimci fonksiyonlarini merkezilestirmek.

Sorumluluklari:
- TC kontrolu
- Zorunlu alan kontrolu
- Pozitif sayi kontrolu
- Tarih parse/format yardimcilari

## 4) Veritabani ve Persistans Omurgasi

### app/db/database.py
Gorevi:
- SQLite baglantisini ve temel query API'sini saglamak.

Sorumluluklari:
- fetchone/fetchall/fetchval
- execute/executemany
- transaction yonetimi
- pragma ayarlari ve baglanti omru

### app/db/migrations.py
Gorevi:
- DB sema versiyonlamasini yonetmek.

Sorumluluklari:
- Hedef versiyona kadar migrationlari sirali uygulamak
- Versiyon tablosunu tutmak
- Seed surecini migration zinciriyle uyumlu tutmak

### app/db/repos/base.py
Gorevi:
- Tum repository siniflari icin ortak taban saglamak.

Sorumluluklari:
- DB nesnesi erisimi
- ortak yardimci metotlar (or. yeni id)

### app/db/repos/*.py
Gorevi:
- Tabloya ozel SQL katmanini saglamak.

Sorumluluklari:
- Sadece SQL
- CRUD sorgulari
- JOIN ve filtreleme sorgulari
- Is kurali barindirmamak

## 5) Guvenlik ve Yetki Omurgasi

### app/security/permissions.py
Gorevi:
- Eylem bazli yetki kontrolunu tek merkezde toplamak.

Sorumluluklari:
- has_permission
- require_permission
- Oturumdaki yetkiler yoksa role fallback uygulamak

### app/security/policy.py
Gorevi:
- Rol tabanli policy yardimci kararlarini merkezilestirmek.

Sorumluluklari:
- Admin oturum kontrolu
- require_admin_session

### app/security/session.py
Gorevi:
- Standart oturum sozlesmesini tek noktada uretmek.

Sorumluluklari:
- Kullanici kaydindan session dict olusturmak
- rol/yetki listesini normalize etmek

### app/rbac.py
Gorevi:
- UI tarafinda modul gorunurlugu ve yetki sorgulari icin uyum katmani saglamak.

Sorumluluklari:
- DB policy yuklemek
- modul_gorunur_mu
- yetki_var_mi (security katmani ile uyumlu)

## 6) Modul Kayit Omurgasi

### menus.json
Gorevi:
- Modul tanimlarinin tek konfigurasyon kaynagi olmak.

Sorumluluklari:
- Modul id, etiket, icon, bolum, sira
- Sayfa sinifi baglantisi
- Badge tanimlari

### app/module_registry.py
Gorevi:
- menus.json verisini runtime nesnelerine cevirmek.

Sorumluluklari:
- Modul listesi ve bolum gruplari uretmek
- Varsayilan modul id belirlemek
- Lazy import ile sayfa olusturmak

## 7) Service ve UseCase Omurgasi

### app/services/*.py
Gorevi:
- Uygulamanin disa acik is katmani API'sini sunmak.

Sorumluluklari:
- Yetki kontrolunu uygulamak
- Varlik kontrolu yapmak
- UseCase fonksiyonlarina delege etmek
- UI tarafina stabil metod imzalari saglamak

### app/usecases/personel/*.py
Gorevi:
- Personel yazma is akislarini servislerden ayirmak.

Sorumluluklari:
- personel_ekle
- personel_guncelle
- personel_pasife_al
- Ortak helper: gorev yeri adi -> id cozumu

### app/usecases/auth/*.py
Gorevi:
- Kullanici yonetimi yazma akislarini ayirmak.

Sorumluluklari:
- kullanici_ekle
- kullanici_rol_guncelle
- kullanici_aktiflik_guncelle

### app/usecases/policy/*.py
Gorevi:
- Policy hesaplama ve kaydetme akislarini ayirmak.

Sorumluluklari:
- tum_rol_modulleri_getir
- rol_modullerini_kaydet

## 8) Test Omurgasi

### tests/test_database.py
Gorevi:
- DB API ve migration davranisini dogrulamak.

### tests/test_validators.py
Gorevi:
- Dogrulama yardimcilarinin kurallara uygun calistigini dogrulamak.

### tests/test_rbac.py
Gorevi:
- Rol/modul/eylem kararlarinin regresyonunu yakalamak.

### tests/test_module_registry.py
Gorevi:
- Modul kayit yukleme ve sayfa olusturma davranisini dogrulamak.

### tests/test_personel_service.py
Gorevi:
- Personel servisinin dis API davranisini dogrulamak.

### tests/test_auth_service.py
Gorevi:
- Auth servisinin dis API davranisini dogrulamak.

### tests/test_policy_service.py
Gorevi:
- Policy servisinin dis API davranisini dogrulamak.

### tests/test_bootstrap.py
Gorevi:
- Baslatma omurgasinin (dizin, logging, db hazirlik) davranisini dogrulamak.

### tests/test_security_permissions.py
Gorevi:
- Merkezi yetki kontrollerini dogrulamak.

### tests/test_security_session.py
Gorevi:
- Oturum sozlesmesi uretimini dogrulamak.

### tests/test_personel_usecases.py
Gorevi:
- Personel use-case akislarinin kurallarini dogrulamak.

### tests/test_auth_usecases.py
Gorevi:
- Auth use-case akislarini dogrulamak.

### tests/test_policy_usecases.py
Gorevi:
- Policy use-case akislarini dogrulamak.

## 9) Bu Iskelette Degisiklik Kurallari

Yeni ozellik eklerken izlenecek sira:
1. Gerekliyse migration yaz
2. Repository SQL ekle
3. UseCase is akisini yaz
4. Service metodunu use-case'e bagla
5. UI sayfasini servis uzerinden bagla
6. Testleri ekle

Bu siralama korunursa UI degisse bile cekirdek omurga stabil kalir.

## 10) Guncel Durum

Bu dokumanin kapsadigi cekirdek iskelet guncellemeleri asagidaki omurgayi aktif olarak kullanir:
- Bootstrap omurgasi (app/bootstrap.py)
- Security omurgasi (app/security/*)
- UseCase omurgasi (app/usecases/personel, app/usecases/auth, app/usecases/policy)
- Servislerin use-case delegasyonu (app/services/*)

Test kapsami:
- Servis testleri
- Use-case testleri
- RBAC ve module registry testleri
- Bootstrap ve security testleri

Not:
- data/repys.db ve logs/repys.log calisma zamani artefaktlaridir.
- Mimari dokuman kapsaminda kaynak kod omurgasi referans alinmistir.
