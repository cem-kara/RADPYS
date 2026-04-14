# Lookup Dogrulama ve Import Stratejisi - Detayli TODO

Bu planin amaci: programi hem esnek hem saglam hale getirmek.
Prensip: sistem her seyi otomatik yutmasin; kritik konularda kullaniciya net kural koysun.

## Kural Seviyeleri (Tum Modullerde Standart)

1. Kirmizi Kural: gecmezse kayit yok (zorunlu alan, kimlik eslesmesi, kritik FK).
2. Sari Kural: kullanici onayi ile devam (alias eslesmesi, supheli metin eslesmesi).
3. Yesil Kural: otomatik duzeltme (bosluk, harf buyukluk, karakter normalize).

## Faz 1 - Cekirdek Altyapi (Oncelik: 1)

### 1. Merkezi ReferenceValidationService olustur
1. Tek giris metodu: kategori + ham deger + politika.
2. Ic akis: normalize -> kanonik eslestirme -> politika karari.
3. Donus modeli: durum, kanonik_deger, uyarilar, aksiyon.
4. Kabul Kriteri: Izin import tarafinda tek noktadan cagriliyor olmali.

### 2. Alias modeli ekle
1. Yeni tablo: lookup_alias (id, kategori, alias, lookup_deger, aktif, kaynak, olusturuldu).
2. Alias ve lookup cakisma kurali netlestir (alias unique kategori+alias).
3. Kabul Kriteri: "Rapor izni" gibi varyasyonlar kanonik degere iniyor olmali.

### 3. Politika yonetimi ekle
1. Politika enum: strict, review, permissive.
2. Kategori bazli varsayilan politika tablosu veya config ekle.
3. Import ekraninda kategori politikasini gosteren bilgi satiri ekle.
4. Kabul Kriteri: ayni veri strict modda reddedilirken permissive modda islenebilmeli.

## Faz 2 - Kullanici Kontrolu ve Izlenebilirlik (Oncelik: 2)

### 4. Onay bekleyen deger havuzu
1. Yeni tablo: reference_pending (id, kategori, ham_deger, onerilen_deger, kaynak_modul, satir_no, durum, olusturuldu).
2. "review" politikasinda kayit buraya duser.
3. Kabul Kriteri: yonetim ekranindan onay/ret verilebilmeli.

### 5. Audit log standardi
1. Her import satiri icin referans eslesme sonucu loglanmali.
2. Kayit alanlari: modul, kategori, ham_deger, kanonik_deger, karar_tipi, kullanici.
3. Kabul Kriteri: bir degerin neden reddedildigi sonradan izlenebilmeli.

### 6. Hata raporu kalitesi
1. Hata kodu standardi ekle (REF001, REF002 vb.).
2. Mesaj + onerilen cozum birlikte yazilsin.
3. Kabul Kriteri: son kullanici teknik destek olmadan raporu anlayabilmeli.

## Faz 3 - Moduller Arasi Yayginlastirma (Oncelik: 3)

### 7. Izin modulunu referans modeline tam gecir
1. Mevcut lookup/otomatik ekleme akislarini yeni servise tasit.
2. Gecis sirasinda davranis farklarini kisa migration notu ile sabitle.
3. Kabul Kriteri: izin import mevcut fonksiyonlarini kaybetmeden yeni servisi kullanmali.

### 8. Saglik veya Dozimetre modulunde pilot
1. Ikinci modul sec ve ayni motoru uygula.
2. Modullerde tekrar eden normalize kodlarini kaldir.
3. Kabul Kriteri: iki farkli modul ayni referans motorundan geciyor olmali.

### 9. Cihaz envanteri hazirligi
1. Cihaz modu icin kategori listesi cikar (cihaz_tipi, marka, model, durum, birim).
2. Her kategoriye kural seviyesi ata (kirmizi/sari/yesil).
3. Kabul Kriteri: cihaz import baslamadan once referans haritasi hazir olmali.

## Faz 4 - Kurumlar Arasi Tasinabilirlik (Oncelik: 4)

### 10. Kurum profili modeli
1. Kurum bazli lookup paketi yukleme (json/csv).
2. Kurum bazli alias seti ve politika override destegi.
3. Kabul Kriteri: kod degistirmeden yeni kuruma geciste temel referanslar yuklenebilmeli.

### 11. Versiyonlama
1. lookup_set_version mantigi ekle.
2. Her import sonucuna hangi versiyonla dogrulandigi yazilsin.
3. Kabul Kriteri: gecmis importu yeniden oynatirken ayni sonuc alinmali.

## Operasyonel Kurallar (Kesin Karar Listesi)

1. Kimlik/FK alanlari otomatik ekleme yapmaz (daima kirmizi).
2. Lookup degeri otomatik ekleme sadece permissive politikada calisir.
3. Otomatik eklenen her yeni deger audit loga duser.
4. "review" modunda kayit DB ana tablosuna yazilmaz, pendinge gider.

## Ilk 2 Haftalik Uygulama Sirasi

1. Hafta 1: Faz 1 (1,2,3) tamamla.
2. Hafta 2: Faz 2 (4,5,6) + Faz 3/7 baslat.
3. Cihaz envanteri baslamadan once Faz 3/9 mutlaka bitmis olsun.

## Done Kriteri (Proje Seviyesi)

1. En az iki modul ayni referans dogrulama motorunu kullaniyor.
2. Politika degisikligi kod degisimi olmadan yapilabiliyor.
3. Hata raporlari son kullanicinin anlayacagi seviyede net.
4. Yeni kurum gecisinde sadece profil/lookup importu ile sistem ayaga kalkabiliyor.
