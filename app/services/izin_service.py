# -*- coding: utf-8 -*-
"""
app/services/izin_service.py
──────────────────────────────
İzin iş mantığı.

Kurallar:
  - Çakışan tarihlere izin eklenemez
  - Sadece aktif izinler iptal edilebilir
  - Bakiye hesabı DB'ye yazılmaz, çalışma anında hesaplanır
  - Memuriyet başlama tarihine göre yıllık hak belirlenir (657 SK md.102)
"""
from __future__ import annotations

from datetime import date

from app.config import (
    LookupKategori,
    PASIF_MIN_GUN,
    PASIF_TIPLER,
    SUA_HAK_GUN,
    YILLIK_HAK_1_10,
    YILLIK_HAK_10P,
)
from app.date_utils import parse_date, to_ui_date
from app.db.database import Database
from app.db.repos.izin_devir_repo import IzinDevirRepo
from app.db.repos.izin_repo import IzinRepo
from app.db.repos.lookup_repo import LookupRepo
from app.db.repos.personel_repo import PersonelRepo
from app.exceptions import DogrulamaHatasi, KayitBulunamadi, LimitHatasi
from app.text_utils import turkish_lower
from app.usecases.izin import izin_ekle, izin_iptal


class IzinService:
    """
    İzin tablosu iş mantığı.

    Kullanım:
        svc = IzinService(db)
        pk  = svc.ekle({"personel_id": "...", "tur": "yillik", ...})
    """

    @staticmethod
    def _izin_turu_norm(izin_tipi: str) -> str:
        """İzin türünü karşılaştırma için normalize eder."""
        tip = turkish_lower(str(izin_tipi or "")).strip()
        return (
            tip.replace("ü", "u")
            .replace("ı", "i")
            .replace("ş", "s")
            .replace("ğ", "g")
            .replace("ö", "o")
            .replace("ç", "c")
        )

    def __init__(self, db: Database):
        self._repo       = IzinRepo(db)
        self._p_repo     = PersonelRepo(db)
        self._lookup     = LookupRepo(db)
        self._devir_repo = IzinDevirRepo(db)

    # ── Sorgular ──────────────────────────────────────────────────

    def listele(
        self,
        personel_id: str | None = None,
        yil: int | None = None,
        durum: str | None = None,
    ) -> list[dict]:
        """İzin listesi — başlama tarihine göre azalan sıra."""
        return self._repo.listele(
            personel_id=personel_id, yil=yil, durum=durum
        )

    def getir(self, pk: str) -> dict:
        """
        Tek izin kaydı.
        Raises: KayitBulunamadi
        """
        row = self._repo.getir(pk)
        if not row:
            raise KayitBulunamadi(f"İzin kaydı bulunamadı: {pk}")
        return row

    def izin_turleri(self) -> list[str]:
        """Lookup'tan izin türü listesi."""
        return self._lookup.kategori(LookupKategori.IZIN_TUR)

    def get_izin_tipleri(self) -> list[str]:
        """Geriye dönük uyumluluk için alias."""
        return self.izin_turleri()

    def personel_listesi(self) -> list[dict]:
        """Aktif personel listesi (id, ad, soyad, kadro_unvani)."""
        return self._p_repo.listele(aktif_only=True)

    def get_personel_listesi(self) -> list[dict]:
        """Geriye dönük uyumluluk için alias."""
        return self.personel_listesi()

    def get_izin_listesi(
        self,
        ay: int | None = None,
        yil: int | None = None,
        personel_id: str | None = None,
        durum: str | None = None,
    ) -> list[dict]:
        """Listelemeyi ay/yıl/personel filtreleriyle döner."""
        rows = self.listele(personel_id=personel_id, yil=yil, durum=durum)
        if ay is None:
            return rows
        sonuc: list[dict] = []
        for row in rows:
            baslama = parse_date(row.get("baslama"))
            if baslama and baslama.month == int(ay):
                sonuc.append(row)
        return sonuc

    def bakiye_hesapla(self, personel_id: str, yil: int) -> dict:
        """
        Yıllık izin bakiyesini hesaplar.

        Önce izin_devir tablosuna bakar; kayıt varsa oradaki
        hak_gun ve devir_gun kullanılır. Kayıt yoksa memuriyet
        süresinden algoritmik hesap yapılır.

        Returns:
            {
                "hak":     int  — yıllık hak (gün)
                "devir":   int  — devir gün
                "toplam":  int  — hak + devir
                "kullanilan": int  — o yıl kullanılan (aktif kayıtlar)
                "kalan":   int  — toplam - kullanılan
            }
        """
        p = self._p_repo.getir(personel_id)
        if not p:
            raise KayitBulunamadi(f"Personel bulunamadı: {personel_id}")

        devir_kayit = self._devir_repo.getir(personel_id, yil)
        if devir_kayit:
            hak   = int(devir_kayit.get("hak_gun") or 0)
            devir = int(devir_kayit.get("devir_gun") or 0)
        else:
            hak   = int(self.yillik_hak_hesapla(p.get("memuriyet_baslama")))
            devir = 0

        toplam = hak + devir
        yillik_aktifler = [
            r for r in self._repo.listele(personel_id=personel_id, yil=yil, durum="aktif")
            if self._izin_turu_norm(r.get("tur")) == "yillik izin"
        ]
        kullanilan = sum(int(r.get("gun") or 0) for r in yillik_aktifler)
        return {
            "hak":        hak,
            "devir":      devir,
            "toplam":     toplam,
            "kullanilan": kullanilan,
            "kalan":      max(0, toplam - kullanilan),
        }

    # ── Yazma ──────────────────────────────────────────────────────

    def _ekle_ortak(
        self,
        veri: dict,
        *,
        limit_kontrol: bool,
        pasif_guncelle: bool,
    ) -> str:
        personel_id = str(veri.get("personel_id") or "").strip()
        tur = str(veri.get("tur") or "").strip()
        gun = int(veri.get("gun") or 0)
        baslama = str(veri.get("baslama") or "").strip()

        if limit_kontrol:
            self.validate_izin_sure_limit(personel_id, tur, gun, baslama)

        izin_id = izin_ekle.execute(self._repo, veri)
        if pasif_guncelle and self.should_set_pasif(tur, gun):
            personel = self._p_repo.getir(personel_id)
            if personel and str(personel.get("durum") or "") != "ayrildi":
                self._p_repo.guncelle(personel_id, {"durum": "pasif"})
        return izin_id

    def ekle(self, veri: dict) -> str:
        """
        Yeni izin kaydı ekler.
        Raises: DogrulamaHatasi, CakismaHatasi
        """
        return self._ekle_ortak(veri, limit_kontrol=True, pasif_guncelle=True)

    def ekle_arsiv(self, veri: dict) -> str:
        """
        Geçmiş toplu veri aktarımı için izin kaydı ekler.

        Not:
            - Yıllık/şua hak limiti kontrolü uygulanmaz.
            - Pasif durum güncellemesi yapılmaz.
            - Zorunlu alan ve tarih çakışma kontrolleri yine uygulanır.
        """
        return self._ekle_ortak(veri, limit_kontrol=False, pasif_guncelle=False)

    def iptal(self, pk: str) -> None:
        """
        İzni iptal eder.
        Raises: KayitBulunamadi, IsKuraliHatasi
        """
        izin_iptal.execute(self._repo, pk)

    # ── Statik yardımcılar ─────────────────────────────────────────

    @staticmethod
    def yillik_hak_hesapla(memuriyet_baslama, today: date | None = None) -> float:
        """657 SK md.102: memuriyet süresine göre yıllık hak."""
        start = parse_date(memuriyet_baslama)
        if not start:
            return 0.0
        ref = today or date.today()
        hizmet_yili = ref.year - start.year
        if (ref.month, ref.day) < (start.month, start.day):
            hizmet_yili -= 1
        if hizmet_yili < 1:
            return 0.0
        if hizmet_yili <= 10:
            return YILLIK_HAK_1_10
        return YILLIK_HAK_10P

    @staticmethod
    def should_set_pasif(izin_tipi: str, gun: int) -> bool:
        """Uzun veya ücretsiz/aylıksız izinlerde personel pasif yapılır."""
        if int(gun or 0) > PASIF_MIN_GUN:
            return True
        tip = IzinService._izin_turu_norm(izin_tipi)
        return any(k in tip for k in PASIF_TIPLER)

    @staticmethod
    def calculate_carryover(mevcut_kalan: float, yillik_hakedis: float) -> float:
        """Yıllık izin devir miktarını hesaplar."""
        try:
            kalan = float(mevcut_kalan or 0)
            hak = float(yillik_hakedis or 0)
        except (TypeError, ValueError):
            return 0.0
        if kalan <= 0 or hak <= 0:
            return 0.0
        return max(0.0, min(kalan, hak, hak * 2.0))

    def has_izin_cakisma(
        self,
        personel_id: str,
        baslama_tarihi: str,
        bitis_tarihi: str,
        ignore_izin_id: str | None = None,
    ) -> bool:
        """Verilen tarih aralığı için personelde aktif izin çakışması var mı?"""
        yeni_bas = parse_date(baslama_tarihi)
        yeni_bit = parse_date(bitis_tarihi)
        if not personel_id or not yeni_bas or not yeni_bit:
            return False
        return self._repo.cakisan_var_mi(
            personel_id=str(personel_id).strip(),
            baslama=str(yeni_bas),
            bitis=str(yeni_bit),
            haric_id=ignore_izin_id,
        )

    def get_izinli_personeller_bugun(self) -> dict[str, list[tuple[str, str]]]:
        """Bugün izinli personelleri {personel_id: [(baslama_ui, bitis_ui)]} döner."""
        today = date.today()
        rows = self.listele(durum="aktif")
        izinli_map: dict[str, list[tuple[str, str]]] = {}

        for row in rows:
            personel_id = str(row.get("personel_id") or "").strip()
            bas = parse_date(row.get("baslama"))
            bit = parse_date(row.get("bitis")) or bas
            if not personel_id or not bas or not bit:
                continue
            if bas <= today <= bit:
                bas_ui = to_ui_date(row.get("baslama"), "")
                bit_ui = to_ui_date(row.get("bitis"), bas_ui)
                izinli_map.setdefault(personel_id, []).append((bas_ui, bit_ui))

        for personel_id in izinli_map:
            izinli_map[personel_id].sort(key=lambda x: x[0])
        return izinli_map

    def validate_izin_sure_limit(
        self,
        personel_id: str,
        izin_tipi: str,
        gun: int,
        baslama_tarihi: str | None = None,
    ) -> None:
        """İzin süresi limitini doğrular, limit aşımında exception fırlatır."""
        if int(gun or 0) <= 0:
            raise DogrulamaHatasi("İzin gün sayısı 0'dan büyük olmalıdır.")

        bas = parse_date(baslama_tarihi) if baslama_tarihi else None
        yil = (bas or date.today()).year
        tip = self._izin_turu_norm(izin_tipi)

        if tip == "yillik izin":
            bakiye = self.bakiye_hesapla(personel_id, yil)
            kalan = int(bakiye.get("kalan") or 0)
            if gun > kalan:
                raise LimitHatasi(f"Yıllık izin için kalan hak {kalan} gün. Talep: {gun} gün.")
            return

        if tip == "sua izni":
            personel = self._p_repo.getir(personel_id)
            if not personel:
                raise KayitBulunamadi(f"Personel bulunamadı: {personel_id}")
            if int(personel.get("sua_hakki") or 0) != 1:
                raise LimitHatasi("Bu personelin Şua İzni hakkı bulunmuyor.")

            kullanilan = self._repo.yillik_kullanim(personel_id, yil, tur="Şua İzni")
            kalan = max(0, int(SUA_HAK_GUN) - int(kullanilan or 0))
            if gun > kalan:
                raise LimitHatasi(f"Şua İzni için kalan hak {kalan} gün. Talep: {gun} gün.")

    def hak_edis_bilgisi(self, memuriyet_baslama, today: date | None = None) -> dict:
        """Geriye dönük uyumluluk için korundu."""
        start = parse_date(memuriyet_baslama)
        ref = today or date.today()
        hizmet_yili = 0.0 if not start else max(0.0, (ref - start).days / 365.25)
        return {
            "hizmet_yili": round(hizmet_yili, 2),
            "yillik_hak": self.yillik_hak_hesapla(memuriyet_baslama, ref),
        }
