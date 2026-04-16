# -*- coding: utf-8 -*-
"""
app/services/personel_service.py
─────────────────────────────────
Personel iş mantığı.

Kurallar:
  - TC doğrulama zorunlu
  - Aynı TC iki kez eklenemez
  - Personel ASLA silinmez → pasife_al() kullanılır
  - Bakiye (izin, şua) bu serviste değil IzinService'te hesaplanır
"""
from __future__ import annotations
from app.db.database import Database
from app.db.repos.personel_repo import PersonelRepo
from app.db.repos.lookup_repo import LookupRepo, GorevYeriRepo
from app.exceptions import CakismaHatasi, DogrulamaHatasi, KayitBulunamadi
from app.security.permissions import require_permission
from app.usecases.personel import personel_ekle, personel_guncelle, personel_pasife_al
from app.config import LookupKategori
from app.validators import parse_tarih, zorunlu


class PersonelService:
    """
    Personel tablosu iş mantığı.

    Kullanım:
        svc = PersonelService(db)
        liste = svc.listele()
        pid   = svc.ekle({"tc_kimlik": "...", "ad": "Ali", "soyad": "Kaya"})
    """

    def __init__(self, db: Database, oturum: dict | None = None):
        self._repo    = PersonelRepo(db)
        self._lookup  = LookupRepo(db)
        self._gy_repo = GorevYeriRepo(db)
        self._oturum = oturum

    def _yetki_kontrol(self, yetki: str, oturum: dict | None = None) -> None:
        aktif_oturum = oturum if oturum is not None else self._oturum
        if aktif_oturum is None:
            return
        require_permission(aktif_oturum, yetki)

    # ── Sorgular ──────────────────────────────────────────────────

    def listele(self, aktif_only: bool = True) -> list[dict]:
        """Personel listesi — soyad/ad sırası."""
        return self._repo.listele(aktif_only=aktif_only)

    def getir(self, personel_id: str) -> dict:
        """
        Tek personel kaydı.
        Raises: KayitBulunamadi
        """
        p = self._repo.getir(personel_id)
        if not p:
            raise KayitBulunamadi(f"Personel bulunamadı: {personel_id}")
        return p

    def tc_ile_getir(self, tc: str) -> dict:
        """
        TC kimlik ile personel getir.
        Raises: KayitBulunamadi
        """
        p = self._repo.tc_ile_getir(tc.strip())
        if not p:
            raise KayitBulunamadi(f"TC bulunamadı: {tc}")
        return p

    def say(self, durum: str | None = None) -> int:
        """Toplam veya duruma göre personel sayısı."""
        return self._repo.say(durum)

    def gorev_gecmisi(self, personel_id: str) -> list[dict]:
        """Personelin gorev yeri gecmis kayitlarini döner."""
        self.getir(personel_id)  # Kayit yoksa standart hata davranisi
        return self._repo.gorev_gecmisi_listele(personel_id)

    def gorev_gecmisi_ekle(
        self,
        personel_id: str,
        gorev_yeri_id: str,
        baslama_tarihi: str,
        bitis_tarihi: str | None = None,
        aciklama: str = "",
        oturum: dict | None = None,
    ) -> str:
        """Personel icin manuel gorev gecmisi kaydi olusturur."""
        self._yetki_kontrol("personel.guncelle", oturum)
        self.getir(personel_id)
        zorunlu(gorev_yeri_id, "Gorev yeri")
        zorunlu(baslama_tarihi, "Baslama tarihi")

        bas = parse_tarih(baslama_tarihi)
        if bas is None:
            raise DogrulamaHatasi("Baslama tarihi gecersiz.")

        bitis = (bitis_tarihi or "").strip() or None
        if bitis:
            bit = parse_tarih(bitis)
            if bit is None:
                raise DogrulamaHatasi("Bitis tarihi gecersiz.")
            if bit < bas:
                raise DogrulamaHatasi("Bitis tarihi baslama tarihinden once olamaz.")

        self._ensure_gorev_gecmisi_cakisma_yok(
            personel_id,
            baslama_tarihi.strip(),
            bitis,
        )

        return self._repo.gorev_gecmisi_ekle(
            personel_id,
            gorev_yeri_id.strip(),
            baslama_tarihi.strip(),
            bitis,
            aciklama,
        )

    def gorev_gecmisi_guncelle(
        self,
        personel_id: str,
        kayit_id: str,
        veri: dict,
        oturum: dict | None = None,
    ) -> None:
        """Personelin bir gorev gecmisi kaydini gunceller."""
        self._yetki_kontrol("personel.guncelle", oturum)
        self.getir(personel_id)
        kayit = self._repo.gorev_gecmisi_getir(kayit_id)
        if not kayit or str(kayit.get("personel_id") or "") != str(personel_id):
            raise KayitBulunamadi("Gorev gecmisi kaydi bulunamadi.")

        payload = dict(veri or {})
        baslama = str(payload.get("baslama_tarihi") or kayit.get("baslama_tarihi") or "").strip()
        bitis = str(payload.get("bitis_tarihi") or "").strip()
        if not bitis:
            payload["bitis_tarihi"] = None

        bas_tarih = parse_tarih(baslama)
        if bas_tarih is None:
            raise DogrulamaHatasi("Baslama tarihi gecersiz.")

        if bitis:
            bit_tarih = parse_tarih(bitis)
            if bit_tarih is None:
                raise DogrulamaHatasi("Bitis tarihi gecersiz.")
            if bit_tarih < bas_tarih:
                raise DogrulamaHatasi("Bitis tarihi baslama tarihinden once olamaz.")

        self._ensure_gorev_gecmisi_cakisma_yok(
            personel_id,
            baslama,
            bitis or None,
            haric_kayit_id=kayit_id,
        )

        self._repo.gorev_gecmisi_guncelle(kayit_id, payload)

    # ── Dropdown Verileri ──────────────────────────────────────────

    def _ensure_gorev_gecmisi_cakisma_yok(
        self,
        personel_id: str,
        baslama_tarihi: str,
        bitis_tarihi: str | None,
        haric_kayit_id: str | None = None,
    ) -> None:
        cakisan = self._repo.gorev_gecmisi_cakisma_getir(
            personel_id,
            baslama_tarihi,
            bitis_tarihi,
            haric_kayit_id=haric_kayit_id,
        )
        if not cakisan:
            return
        mevcut_baslama = str(cakisan.get("baslama_tarihi") or "")
        mevcut_bitis = str(cakisan.get("bitis_tarihi") or "") or "Aktif"
        birim = str(cakisan.get("gorev_yeri_ad") or "Bilinmeyen birim")
        raise CakismaHatasi(
            "Gorev gecmisi tarih araligi cakisiyor: "
            f"{mevcut_baslama} - {mevcut_bitis} ({birim})."
        )

    def hizmet_siniflari(self) -> list[str]:
        return self._lookup.kategori(LookupKategori.HIZMET_SINIFI)

    def kadro_unvanlari(self) -> list[str]:
        return self._lookup.kategori(LookupKategori.KADRO_UNVANI)

    def gorev_yerleri(self) -> list[dict]:
        """[{"id": ..., "ad": ..., "sua_hakki": ...}] listesi."""
        return self._gy_repo.listele()

    def gorev_yeri_adlari(self) -> list[str]:
        return self._gy_repo.ad_listesi()

    # ── Yazma ─────────────────────────────────────────────────────

    def ekle(self, veri: dict, oturum: dict | None = None) -> str:
        """
        Yeni personel ekler.

        Zorunlu alanlar: tc_kimlik, ad, soyad
        Returns: Yeni personelin ID'si

        Raises:
            TCHatasi           — geçersiz TC
            DogrulamaHatasi    — zorunlu alan boş
            KayitZatenVar      — TC zaten kayıtlı
        """
        self._yetki_kontrol("personel.ekle", oturum)
        return personel_ekle(self._repo, self._gy_repo, veri)

    def guncelle(self, personel_id: str, veri: dict, oturum: dict | None = None) -> None:
        """
        Personel bilgilerini günceller.
        tc_kimlik değiştirilemez.

        Raises: KayitBulunamadi
        """
        self._yetki_kontrol("personel.guncelle", oturum)
        self.getir(personel_id)   # Varlık kontrolü
        personel_guncelle(self._repo, self._gy_repo, personel_id, veri)

    def pasife_al(self, personel_id: str,
                  ayrilik_tarihi: str,
                  ayrilik_nedeni: str = "",
                  oturum: dict | None = None) -> None:
        """
        Personeli pasife alır — fiziksel silme yok.

        Raises: KayitBulunamadi
        """
        self._yetki_kontrol("personel.pasife_al", oturum)
        p = self.getir(personel_id)
        personel_pasife_al(
            self._repo,
            p,
            personel_id,
            ayrilik_tarihi,
            ayrilik_nedeni,
        )

    def guncelle_veya_ekle_import(self, veri: dict, oturum: dict | None = None) -> str:
        """
        Import düzeltme akışı için upsert davranışı sağlar.

        - TC ile kayıt varsa personeli günceller.
        - TC ile kayıt yoksa yeni personel ekler.
        """
        self._yetki_kontrol("personel.guncelle", oturum)
        tc = str(veri.get("tc_kimlik") or "").strip()
        mevcut = self._repo.tc_ile_getir(tc) if tc else None
        if mevcut:
            personel_id = str(mevcut.get("id") or "").strip()
            payload = dict(veri)

            # Boş gönderilen alanlar mevcut değeri silmesin; sadece dolu alanları güncelle.
            payload = {
                k: v
                for k, v in payload.items()
                if str(v or "").strip()
            }
            if payload:
                personel_guncelle(self._repo, self._gy_repo, personel_id, payload)
            return personel_id

        return personel_ekle(self._repo, self._gy_repo, veri)
