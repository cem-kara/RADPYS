# -*- coding: utf-8 -*-
"""app/services/nobet_service.py - Nöbet planı hazırlık servis katmanı."""
from __future__ import annotations

from calendar import monthrange
from collections import defaultdict
import sqlite3
from datetime import date, datetime, timedelta

from app.db.database import Database
from app.db.repos.nobet_repo import NobetRepo
from app.exceptions import DogrulamaHatasi, KayitBulunamadi, KayitZatenVar


class NobetService:
    """Nobet birim ve plan tablolari icin temel is kurallari."""

    def __init__(self, db: Database):
        self._repo = NobetRepo(db)

    def birimler_listele(self, aktif_only: bool = True) -> list[dict]:
        return self._repo.birimler_listele(aktif_only=aktif_only)

    def birim_kural_getir(self, birim_id: str) -> dict:
        bid = str(birim_id or "").strip()
        if not bid:
            raise DogrulamaHatasi("Birim secimi zorunludur.")
        if self._repo.birim_getir(bid) is None:
            raise KayitBulunamadi("Birim bulunamadi.")
        kural = self._repo.birim_kural_getir(bid) or {}
        if not kural:
            return {
                "birim_id": bid,
                "min_dinlenme_saat": 12.0,
                "resmi_tatil_calisma": 1,
                "dini_tatil_calisma": 1,
                "arefe_baslangic_saat": "13:00",
                "max_fazla_mesai_saat": 0.0,
                "tolerans_saat": 7.0,
                "max_devreden_saat": 12.0,
                "max_ardisik_nobet": 2,
                "manuel_limit_asimina_izin": 1,
            }
        return kural

    def birim_kural_kaydet(self, birim_id: str, veri: dict) -> None:
        bid = str(birim_id or "").strip()
        if not bid:
            raise DogrulamaHatasi("Birim secimi zorunludur.")
        if self._repo.birim_getir(bid) is None:
            raise KayitBulunamadi("Birim bulunamadi.")

        min_dinlenme = float(veri.get("min_dinlenme_saat") or 12)
        tolerans = float(veri.get("tolerans_saat") or 7)
        devreden = float(veri.get("max_devreden_saat") or 12)
        raw_max_ardisik = veri.get("max_ardisik_nobet")
        max_ardisik = 2 if raw_max_ardisik is None or str(raw_max_ardisik).strip() == "" else int(raw_max_ardisik)
        max_fazla = float(veri.get("max_fazla_mesai_saat") or 0)
        arefe = str(veri.get("arefe_baslangic_saat") or "13:00").strip()
        if min_dinlenme < 0:
            raise DogrulamaHatasi("Dinlenme suresi negatif olamaz.")
        if tolerans < 0:
            raise DogrulamaHatasi("Tolerans negatif olamaz.")
        if devreden < 0:
            raise DogrulamaHatasi("Devreden saat negatif olamaz.")
        if max_ardisik < 1:
            raise DogrulamaHatasi("Ardisik nobet limiti en az 1 olmalidir.")
        if max_fazla < 0:
            raise DogrulamaHatasi("Fazla mesai limiti negatif olamaz.")
        if len(arefe) != 5 or arefe[2] != ":":
            raise DogrulamaHatasi("Arefe baslangic saati HH:MM formatinda olmalidir.")

        self._repo.birim_kural_upsert(
            bid,
            {
                "min_dinlenme_saat": min_dinlenme,
                "resmi_tatil_calisma": 1 if bool(veri.get("resmi_tatil_calisma")) else 0,
                "dini_tatil_calisma": 1 if bool(veri.get("dini_tatil_calisma")) else 0,
                "arefe_baslangic_saat": arefe,
                "max_fazla_mesai_saat": max_fazla,
                "tolerans_saat": tolerans,
                "max_devreden_saat": devreden,
                "max_ardisik_nobet": max_ardisik,
                "manuel_limit_asimina_izin": 1 if bool(veri.get("manuel_limit_asimina_izin")) else 0,
            },
        )

    def vardiya_listele(self, birim_id: str, aktif_only: bool = True) -> list[dict]:
        bid = str(birim_id or "").strip()
        if not bid:
            return []
        return self._repo.vardiya_listele(bid, aktif_only=aktif_only)

    def sablon_listele(self, aktif_only: bool = True) -> list[dict]:
        return self._repo.sablon_listele(aktif_only=aktif_only)

    def sablon_ekle(
        self,
        ad: str,
        baslangic_saat: str,
        bitis_saat: str,
        saat_suresi: float,
        aciklama: str = "",
    ) -> str:
        txt_ad = str(ad or "").strip()
        if not txt_ad:
            raise DogrulamaHatasi("Sablon adi zorunludur.")
        sure = float(saat_suresi)
        if sure <= 0:
            raise DogrulamaHatasi("Vardiya suresi pozitif olmalidir.")
        bas = str(baslangic_saat or "").strip()
        bit = str(bitis_saat or "").strip()
        if len(bas) != 5 or len(bit) != 5 or bas[2] != ":" or bit[2] != ":":
            raise DogrulamaHatasi("Saat formati HH:MM olmalidir.")
        try:
            return self._repo.sablon_ekle(txt_ad, bas, bit, sure, aciklama)
        except Exception as exc:
            if "UNIQUE" in str(exc).upper():
                raise KayitZatenVar(f"'{txt_ad}' adinda sablon zaten mevcut.") from exc
            raise

    def sablon_pasife_al(self, sablon_id: str) -> None:
        sid = str(sablon_id or "").strip()
        if not sid:
            raise DogrulamaHatasi("Sablon secimi zorunludur.")
        if self._repo.sablon_getir(sid) is None:
            raise KayitBulunamadi("Sablon bulunamadi.")
        self._repo.sablon_pasife_al(sid)

    def sablon_birime_ata(self, birim_id: str, sablon_id: str, max_personel: int) -> str:
        bid = str(birim_id or "").strip()
        sid = str(sablon_id or "").strip()
        if not bid:
            raise DogrulamaHatasi("Birim secimi zorunludur.")
        if not sid:
            raise DogrulamaHatasi("Sablon secimi zorunludur.")
        if self._repo.birim_getir(bid) is None:
            raise KayitBulunamadi("Birim bulunamadi.")
        if self._repo.sablon_getir(sid) is None:
            raise KayitBulunamadi("Sablon bulunamadi.")
        mp = int(max_personel)
        if mp < 1:
            raise DogrulamaHatasi("Max personel en az 1 olmalidir.")
        return self._repo.sablon_birime_ata(bid, sid, mp)

    def vardiya_pasife_al(self, vardiya_id: str) -> None:
        vid = str(vardiya_id or "").strip()
        if not vid:
            raise DogrulamaHatasi("Vardiya secimi zorunludur.")
        self._repo.vardiya_pasife_al(vid)

    def vardiya_ekle(
        self,
        birim_id: str,
        ad: str,
        saat_suresi: float,
        baslangic_saat: str,
        bitis_saat: str,
        max_personel: int = 1,
    ) -> str:
        bid = str(birim_id or "").strip()
        txt_ad = str(ad or "").strip()
        if not bid:
            raise DogrulamaHatasi("Birim secimi zorunludur.")
        if not txt_ad:
            raise DogrulamaHatasi("Vardiya adi zorunludur.")
        sure = float(saat_suresi)
        if sure <= 0:
            raise DogrulamaHatasi("Vardiya suresi pozitif olmalidir.")
        bas = str(baslangic_saat or "").strip()
        bit = str(bitis_saat or "").strip()
        if len(bas) != 5 or len(bit) != 5 or bas[2] != ":" or bit[2] != ":":
            raise DogrulamaHatasi("Saat formati HH:MM olmalidir.")
        mp = int(max_personel)
        if mp < 1:
            raise DogrulamaHatasi("Max personel en az 1 olmalidir.")
        return self._repo.vardiya_ekle(bid, txt_ad, sure, bas, bit, max_personel=mp)

    def birim_personellerini_esitle(self, birim_id: str) -> int:
        bid = str(birim_id or "").strip()
        if not bid:
            raise DogrulamaHatasi("Birim secimi zorunludur.")
        if self._repo.birim_getir(bid) is None:
            raise KayitBulunamadi("Birim bulunamadi.")
        return self._repo.birim_personellerini_esitle(bid)

    def birim_personel_kosullari_listele(self, birim_id: str) -> list[dict]:
        bid = str(birim_id or "").strip()
        if not bid:
            return []
        return self._repo.birim_personel_listele(bid)

    def personel_kosul_kaydet(self, birim_id: str, personel_id: str, veri: dict) -> None:
        bid = str(birim_id or "").strip()
        pid = str(personel_id or "").strip()
        if not bid or not pid:
            raise DogrulamaHatasi("Birim ve personel secimi zorunludur.")
        if float(veri.get("max_fazla_mesai_saat") or 0) < 0:
            raise DogrulamaHatasi("Fazla mesai limiti negatif olamaz.")
        if float(veri.get("tolerans_saat") or 7) < 0:
            raise DogrulamaHatasi("Tolerans negatif olamaz.")
        if float(veri.get("max_devreden_saat") or 12) < 0:
            raise DogrulamaHatasi("Devreden saat negatif olamaz.")

        self._repo.personel_kural_upsert(
            bid,
            pid,
            {
                "ister_24_saat": 1 if bool(veri.get("ister_24_saat")) else 0,
                "mesai_istemiyor": 1 if bool(veri.get("mesai_istemiyor")) else 0,
                "max_fazla_mesai_saat": float(veri.get("max_fazla_mesai_saat") or 0),
                "tolerans_saat": float(veri.get("tolerans_saat") or 7),
                "max_devreden_saat": float(veri.get("max_devreden_saat") or 12),
            },
        )

    def personel_kanuni_mesai_listele(self, birim_id: str, aktif_only: bool = True) -> list[dict]:
        bid = str(birim_id or "").strip()
        if not bid:
            return []
        return self._repo.personel_kanuni_mesai_listele(bid, aktif_only=aktif_only)

    def personel_kanuni_mesai_ekle(
        self,
        birim_id: str,
        personel_id: str,
        baslangic_tarih: str,
        bitis_tarih: str | None,
        duzenleme_tipi: str,
        deger: float,
        aciklama: str = "",
    ) -> str:
        bid = str(birim_id or "").strip()
        pid = str(personel_id or "").strip()
        if not bid or not pid:
            raise DogrulamaHatasi("Birim ve personel secimi zorunludur.")
        if self._repo.birim_getir(bid) is None:
            raise KayitBulunamadi("Birim bulunamadi.")
        if not self._repo.birim_personel_var_mi(bid, pid):
            raise DogrulamaHatasi("Secilen personel bu birimin aktif personel listesinde degil.")

        bas = str(baslangic_tarih or "").strip()
        bit = str(bitis_tarih or "").strip()
        if len(bas) != 10:
            raise DogrulamaHatasi("Baslangic tarihi YYYY-AA-GG formatinda olmalidir.")
        if bit and len(bit) != 10:
            raise DogrulamaHatasi("Bitis tarihi YYYY-AA-GG formatinda olmalidir.")

        tip = str(duzenleme_tipi or "").strip()
        if tip not in {"saat_dusum", "oran", "manuel_hedef", "sut_0_6", "sut_6_12", "yarim_zamanli"}:
            raise DogrulamaHatasi("Duzenleme tipi gecersiz.")

        val = float(deger)
        if tip in {"saat_dusum", "manuel_hedef"} and val < 0:
            raise DogrulamaHatasi("Saat degeri negatif olamaz.")
        if tip == "oran" and (val < 0 or val > 100):
            raise DogrulamaHatasi("Oran degeri 0-100 araliginda olmalidir.")
        if tip in {"sut_0_6", "sut_6_12", "yarim_zamanli"} and val < 0:
            raise DogrulamaHatasi("Deger negatif olamaz.")

        return self._repo.personel_kanuni_mesai_ekle(
            bid,
            pid,
            bas,
            bit or None,
            tip,
            val,
            aciklama,
        )

    def personel_kanuni_mesai_pasife_al(self, kayit_id: str) -> None:
        kid = str(kayit_id or "").strip()
        if not kid:
            raise DogrulamaHatasi("Kayit secimi zorunludur.")
        self._repo.personel_kanuni_mesai_pasife_al(kid)

    def aylik_calisma_gunu_hesapla(self, yil: int, ay: int) -> float:
        y = int(yil)
        m = int(ay)
        if m < 1 or m > 12:
            raise DogrulamaHatasi("Ay 1-12 araliginda olmalidir.")
        son_gun = monthrange(y, m)[1]
        ay_bas = date(y, m, 1)
        ay_bit = date(y, m, son_gun)

        calisma = 0.0
        gun = ay_bas
        while gun <= ay_bit:
            if gun.weekday() < 5:
                calisma += 1.0
            gun += timedelta(days=1)

        tatiller = self._repo.tatil_aralik_listele(ay_bas.isoformat(), ay_bit.isoformat())
        for t in tatiller:
            try:
                tg = date.fromisoformat(str(t.get("tarih") or ""))
            except ValueError:
                continue
            if tg.weekday() >= 5:
                continue
            if int(t.get("yarim_gun") or 0) == 1:
                calisma -= 0.5
            else:
                calisma -= 1.0

        return max(0.0, round(calisma, 2))

    def _calisma_gunu_aralik_hesapla(self, bas_tarih: date, bit_tarih: date) -> float:
        if bit_tarih < bas_tarih:
            return 0.0

        calisma = 0.0
        gun = bas_tarih
        while gun <= bit_tarih:
            if gun.weekday() < 5:
                calisma += 1.0
            gun += timedelta(days=1)

        tatiller = self._repo.tatil_aralik_listele(bas_tarih.isoformat(), bit_tarih.isoformat())
        for t in tatiller:
            try:
                tg = date.fromisoformat(str(t.get("tarih") or ""))
            except ValueError:
                continue
            if tg < bas_tarih or tg > bit_tarih or tg.weekday() >= 5:
                continue
            if int(t.get("yarim_gun") or 0) == 1:
                calisma -= 0.5
            else:
                calisma -= 1.0

        return max(0.0, round(calisma, 2))

    @staticmethod
    def _saat_str_dakika(saat_text: str) -> int:
        saat = str(saat_text or "").strip()
        parcalar = saat.split(":")
        if len(parcalar) != 2:
            raise ValueError("Saat formati gecersiz.")
        saat_no = int(parcalar[0])
        dakika_no = int(parcalar[1])
        if saat_no < 0 or saat_no > 23 or dakika_no < 0 or dakika_no > 59:
            raise ValueError("Saat formati gecersiz.")
        return (saat_no * 60) + dakika_no

    def _vardiya_zaman_araligi(self, tarih_text: str, baslangic_saat: str, bitis_saat: str) -> tuple[datetime, datetime]:
        gun = date.fromisoformat(str(tarih_text or "").strip())
        bas_dakika = self._saat_str_dakika(baslangic_saat)
        bit_dakika = self._saat_str_dakika(bitis_saat)
        bas = datetime.combine(gun, datetime.min.time()) + timedelta(minutes=bas_dakika)
        bit = datetime.combine(gun, datetime.min.time()) + timedelta(minutes=bit_dakika)
        if bit <= bas:
            bit += timedelta(days=1)
        return bas, bit

    def _vardiya_etkin_sure_ve_aralik(
        self,
        tarih_text: str,
        vardiya: dict,
        arefe_baslangic_saat: str,
        yarim_gun: bool,
    ) -> tuple[float, datetime, datetime] | None:
        bas, bit = self._vardiya_zaman_araligi(
            tarih_text,
            str(vardiya.get("baslangic_saat") or "00:00"),
            str(vardiya.get("bitis_saat") or "00:00"),
        )
        etkin_bas = bas
        if yarim_gun:
            arefe_dakika = self._saat_str_dakika(arefe_baslangic_saat)
            arefe_bas = datetime.combine(bas.date(), datetime.min.time()) + timedelta(minutes=arefe_dakika)
            etkin_bas = max(etkin_bas, arefe_bas)
        if bit <= etkin_bas:
            return None
        saat = round((bit - etkin_bas).total_seconds() / 3600.0, 2)
        if saat <= 0:
            return None
        return saat, etkin_bas, bit

    @staticmethod
    def _dinlenme_yeterli_mi(
        onceki_bitis: datetime | None,
        yeni_baslangic: datetime,
        min_dinlenme_saat: float,
    ) -> bool:
        if onceki_bitis is None:
            return True
        fark_saat = (yeni_baslangic - onceki_bitis).total_seconds() / 3600.0
        return fark_saat >= float(min_dinlenme_saat or 0.0)

    def personel_aylik_hedef_ve_devir_hesapla(
        self,
        birim_id: str,
        personel_id: str,
        yil: int,
        ay: int,
        gerceklesen_saat: float = 0.0,
    ) -> dict:
        bid = str(birim_id or "").strip()
        pid = str(personel_id or "").strip()
        y = int(yil)
        m = int(ay)
        if not bid or not pid:
            raise DogrulamaHatasi("Birim ve personel secimi zorunludur.")

        calisma_gunu = self.aylik_calisma_gunu_hesapla(y, m)
        standart_hedef = round(calisma_gunu * 7.0, 2)

        son_gun = monthrange(y, m)[1]
        ay_bas_d = date(y, m, 1)
        ay_bit_d = date(y, m, son_gun)
        duzenlemeler = self._repo.personel_kanuni_mesai_donem_listele(
            bid,
            pid,
            ay_bas_d.isoformat(),
            ay_bit_d.isoformat(),
        )

        kanuni_hedef = standart_hedef
        manuel = [d for d in duzenlemeler if str(d.get("duzenleme_tipi") or "") == "manuel_hedef"]
        if manuel:
            kanuni_hedef = max(0.0, round(float((manuel[0] or {}).get("deger") or 0.0), 2))
        else:
            oran_toplam = 0.0
            saat_dusum = 0.0
            gunluk_dusum = 0.0
            for d in duzenlemeler:
                tip = str(d.get("duzenleme_tipi") or "")
                val = float(d.get("deger") or 0.0)
                if tip == "oran":
                    oran_toplam += val
                elif tip == "saat_dusum":
                    saat_dusum += val
                elif tip in {"sut_0_6", "sut_6_12", "yarim_zamanli"}:
                    try:
                        d_bas = date.fromisoformat(str(d.get("baslangic_tarih") or ""))
                    except ValueError:
                        continue
                    try:
                        d_bit = (
                            date.fromisoformat(str(d.get("bitis_tarih") or ""))
                            if d.get("bitis_tarih")
                            else ay_bit_d
                        )
                    except ValueError:
                        d_bit = ay_bit_d

                    kesisim_bas = max(ay_bas_d, d_bas)
                    kesisim_bit = min(ay_bit_d, d_bit)
                    if kesisim_bit < kesisim_bas:
                        continue
                    etkin_gun = self._calisma_gunu_aralik_hesapla(kesisim_bas, kesisim_bit)
                    if tip == "sut_0_6":
                        # Gunluk 3 saat sut izni
                        gunluk_dusum += 3.0 * etkin_gun
                    elif tip == "sut_6_12":
                        # Gunluk 1.5 saat sut izni
                        gunluk_dusum += 1.5 * etkin_gun
                    elif tip == "yarim_zamanli":
                        # 7 saatlik gunun yarisi kadar dusum (3.5 saat)
                        gunluk_dusum += 3.5 * etkin_gun

            oran_toplam = min(100.0, max(0.0, oran_toplam))
            kanuni_hedef = kanuni_hedef * (1.0 - oran_toplam / 100.0)
            kanuni_hedef = max(0.0, kanuni_hedef - saat_dusum)
            kanuni_hedef = max(0.0, kanuni_hedef - gunluk_dusum)
            kanuni_hedef = round(kanuni_hedef, 2)

        onceki_devir = float(self._repo.personel_devir_onceki_getir(bid, pid, y, m) or 0.0)
        devirli_hedef = round(kanuni_hedef + onceki_devir, 2)

        gerceklesen = float(gerceklesen_saat or 0.0)
        yeni_devir_ham = devirli_hedef - gerceklesen
        yeni_devir = round(max(-12.0, min(12.0, yeni_devir_ham)), 2)

        return {
            "calisma_gunu": calisma_gunu,
            "standart_hedef_saat": standart_hedef,
            "kanuni_hedef_saat": kanuni_hedef,
            "onceki_devir_saat": round(onceki_devir, 2),
            "devirli_hedef_saat": devirli_hedef,
            "gerceklesen_saat": gerceklesen,
            "yeni_devir_saat": yeni_devir,
        }

    def personel_aylik_devir_kaydet(self, birim_id: str, personel_id: str, yil: int, ay: int, devir_saat: float) -> None:
        bid = str(birim_id or "").strip()
        pid = str(personel_id or "").strip()
        if not bid or not pid:
            raise DogrulamaHatasi("Birim ve personel secimi zorunludur.")
        val = float(devir_saat)
        val = max(-12.0, min(12.0, val))
        self._repo.personel_devir_upsert(bid, pid, int(yil), int(ay), round(val, 2))

    def birimleri_gorev_yerinden_esitle(self) -> int:
        return self._repo.birimleri_gorev_yerinden_esitle()

    def planlari_listele(self, yil: int | None = None, ay: int | None = None) -> list[dict]:
        return self._repo.plan_listele(yil=yil, ay=ay)

    def plan_satir_detay_listele(self, plan_id: str) -> list[dict]:
        pid = str(plan_id or "").strip()
        if not pid:
            return []
        rows = self._repo.plan_satir_detay_listele(pid)
        for r in rows:
            ad = str(r.get("ad") or "").strip()
            soyad = str(r.get("soyad") or "").strip()
            r["ad_soyad"] = f"{ad} {soyad}".strip()
        return rows

    def plan_satir_manuel_ekle(
        self,
        plan_id: str,
        personel_id: str,
        vardiya_id: str,
        tarih: str,
    ) -> str:
        pid_plan = str(plan_id or "").strip()
        pid_per = str(personel_id or "").strip()
        vid = str(vardiya_id or "").strip()
        tarih_str = str(tarih or "").strip()
        if not pid_plan:
            raise DogrulamaHatasi("Plan secimi zorunludur.")
        if not pid_per:
            raise DogrulamaHatasi("Personel secimi zorunludur.")
        if not vid:
            raise DogrulamaHatasi("Vardiya secimi zorunludur.")
        if len(tarih_str) != 10:
            raise DogrulamaHatasi("Tarih YYYY-AA-GG formatinda olmalidir.")
        try:
            date.fromisoformat(tarih_str)
        except ValueError:
            raise DogrulamaHatasi("Gecersiz tarih.")
        vardiya = self._repo.vardiya_getir(vid)
        if vardiya is None:
            raise KayitBulunamadi("Vardiya bulunamadi.")
        saat_suresi = float(vardiya.get("saat_suresi") or 0.0)
        return self._repo.plan_satir_ekle(
            plan_id=pid_plan,
            personel_id=pid_per,
            vardiya_id=vid,
            tarih=tarih_str,
            saat_suresi=saat_suresi,
            kaynak="manuel",
        )

    def plan_personel_aylik_nobet_ozeti(self, plan_id: str) -> list[dict]:
        rows = self.plan_satir_detay_listele(plan_id)
        if not rows:
            return []

        ozet: dict[str, dict] = {}
        tarihler_map: defaultdict[str, list[str]] = defaultdict(list)

        for r in rows:
            personel_id = str(r.get("personel_id") or "").strip()
            if not personel_id:
                continue
            if personel_id not in ozet:
                ozet[personel_id] = {
                    "personel_id": personel_id,
                    "ad_soyad": str(r.get("ad_soyad") or "").strip(),
                    "toplam_saat": 0.0,
                }
            ozet[personel_id]["toplam_saat"] = round(
                float(ozet[personel_id].get("toplam_saat") or 0.0) + float(r.get("saat_suresi") or 0.0),
                2,
            )
            tarih = str(r.get("tarih") or "").strip()
            if tarih:
                tarihler_map[personel_id].append(tarih)

        cikti: list[dict] = []
        for personel_id, p in ozet.items():
            gunler = []
            for t in sorted(set(tarihler_map.get(personel_id) or [])):
                try:
                    gunler.append(f"{date.fromisoformat(t).day:02d}")
                except ValueError:
                    gunler.append(t)
            p["nobet_tarihleri"] = ", ".join(gunler)
            p["nobet_gunu_sayisi"] = len(gunler)
            cikti.append(p)

        return sorted(cikti, key=lambda x: str(x.get("ad_soyad") or ""))

    def plan_gunluk_vardiya_durumu(
        self,
        plan_id: str,
        birim_id: str,
        yil: int,
        ay: int,
    ) -> list[dict]:
        pid = str(plan_id or "").strip()
        bid = str(birim_id or "").strip()
        y = int(yil)
        m = int(ay)
        if not pid or not bid:
            return []

        gun_adlari = ["Pzt", "Sal", "Car", "Per", "Cum", "Cmt", "Paz"]
        atamalar = self.plan_satir_detay_listele(pid)
        vardiyalar = self.vardiya_listele(bid, aktif_only=True)
        if not vardiyalar:
            return []

        atama_map: defaultdict[tuple[str, str], list[str]] = defaultdict(list)
        for a in atamalar:
            tarih = str(a.get("tarih") or "").strip()
            vardiya_id = str(a.get("vardiya_id") or "").strip()
            ad_soyad = str(a.get("ad_soyad") or "").strip()
            if tarih and vardiya_id and ad_soyad:
                atama_map[(tarih, vardiya_id)].append(ad_soyad)

        for anahtar in list(atama_map.keys()):
            atama_map[anahtar] = sorted(atama_map[anahtar])

        sonuc: list[dict] = []
        gun_sayisi = monthrange(y, m)[1]
        for g in range(1, gun_sayisi + 1):
            tarih_obj = date(y, m, g)
            tarih = tarih_obj.isoformat()
            gun_kisa = gun_adlari[tarih_obj.weekday()]
            for v in vardiyalar:
                vardiya_id = str(v.get("id") or "").strip()
                vardiya_ad = str(v.get("ad") or "").strip() or "-"
                kapasite = int(v.get("max_personel") or 1)
                if kapasite < 1:
                    kapasite = 1
                kisiler = atama_map.get((tarih, vardiya_id), [])
                for i in range(kapasite):
                    dolu = i < len(kisiler)
                    sonuc.append(
                        {
                            "tarih": tarih,
                            "gun": gun_kisa,
                            "vardiya": vardiya_ad,
                            "slot": i + 1,
                            "personel": kisiler[i] if dolu else "-",
                            "durum": "Dolu" if dolu else "Bos",
                        }
                    )

        return sonuc

    def taslak_plan_olustur(
        self,
        birim_id: str,
        yil: int,
        ay: int,
        notlar: str = "",
    ) -> str:
        bid = str(birim_id or "").strip()
        if not bid:
            raise DogrulamaHatasi("Nobet birimi secimi zorunludur.")

        if self._repo.birim_getir(bid) is None:
            raise KayitBulunamadi("Secilen nobet birimi bulunamadi.")

        y = int(yil)
        m = int(ay)
        if y < 2000 or y > 2100:
            raise DogrulamaHatasi("Yil gecersiz.")
        if m < 1 or m > 12:
            raise DogrulamaHatasi("Ay 1-12 araliginda olmalidir.")

        if self._repo.plan_getir(bid, y, m):
            raise KayitZatenVar("Bu birim ve ay icin plan zaten mevcut.")

        try:
            return self._repo.plan_ekle(
                birim_id=bid,
                yil=y,
                ay=m,
                durum="taslak",
                notlar=notlar,
            )
        except sqlite3.IntegrityError as exc:
            if "UNIQUE" in str(exc).upper():
                raise KayitZatenVar("Bu birim ve ay icin plan zaten mevcut.") from exc
            raise

    def taslak_plan_olustur_ve_doldur(
        self,
        birim_id: str,
        yil: int,
        ay: int,
        notlar: str = "",
    ) -> dict:
        """Taslak plan olusturur ve basit skorlamayla otomatik satirlari yerlestirir."""
        plan_id = self.taslak_plan_olustur(birim_id=birim_id, yil=yil, ay=ay, notlar=notlar)

        bid = str(birim_id or "").strip()
        y = int(yil)
        m = int(ay)
        vardiyalar = self.vardiya_listele(bid, aktif_only=True)
        if not vardiyalar:
            raise DogrulamaHatasi("Secili birim icin aktif vardiya tanimi bulunamadi.")

        kural = self.birim_kural_getir(bid)
        min_dinlenme_saat = float(kural.get("min_dinlenme_saat") or 12.0)
        max_ardisik_nobet = int(kural.get("max_ardisik_nobet") or 2)
        arefe_baslangic_saat = str(kural.get("arefe_baslangic_saat") or "13:00")
        resmi_tatil_calisma = bool(kural.get("resmi_tatil_calisma"))
        dini_tatil_calisma = bool(kural.get("dini_tatil_calisma"))

        personeller = self.birim_personel_kosullari_listele(bid)
        if not personeller:
            raise DogrulamaHatasi("Secili birim icin aktif personel bulunamadi.")

        saatler: dict[str, float] = {}
        atama_sayisi: dict[str, int] = {}
        hedefler: dict[str, float] = {}
        son_bitisler: dict[str, datetime | None] = {}
        son_atama_tarihleri: dict[str, date | None] = {}
        ardisik_sayilari: dict[str, int] = {}
        for p in personeller:
            pid = str(p.get("personel_id") or "").strip()
            saatler[pid] = 0.0
            atama_sayisi[pid] = 0
            son_bitisler[pid] = None
            son_atama_tarihleri[pid] = None
            ardisik_sayilari[pid] = 0
            hesap = self.personel_aylik_hedef_ve_devir_hesapla(bid, pid, y, m, gerceklesen_saat=0)
            hedefler[pid] = float(hesap.get("devirli_hedef_saat") or 0.0)

        gun_sayisi = monthrange(y, m)[1]
        eksik: list[dict] = []
        satir_adet = 0
        tatil_map = {
            str(t.get("tarih") or "").strip(): t
            for t in self._repo.tatil_aralik_listele(date(y, m, 1).isoformat(), date(y, m, gun_sayisi).isoformat())
        }

        for g in range(1, gun_sayisi + 1):
            tarih = date(y, m, g).isoformat()
            gun_ici_atanan: set[str] = set()
            tatil = tatil_map.get(tarih) or {}
            tatil_turu = str(tatil.get("tur") or "").strip()
            yarim_gun = int(tatil.get("yarim_gun") or 0) == 1

            if tatil_turu == "resmi" and not resmi_tatil_calisma:
                continue
            if tatil_turu == "dini" and not dini_tatil_calisma:
                continue

            for v in vardiyalar:
                vid = str(v.get("id") or "").strip()
                etkin = self._vardiya_etkin_sure_ve_aralik(
                    tarih,
                    v,
                    arefe_baslangic_saat,
                    yarim_gun=yarim_gun,
                )
                if etkin is None:
                    eksik.append(
                        {
                            "tarih": tarih,
                            "vardiya_id": vid,
                            "neden": "vardiya_suresi_sifir",
                        }
                    )
                    continue

                saat, vardiya_bas, vardiya_bit = etkin
                kapasite = int(v.get("max_personel") or 1)
                if kapasite < 1:
                    kapasite = 1

                for _ in range(kapasite):
                    secili_pid = None
                    secili_skor = None
                    red_nedeni = "uygun_aday_yok"
                    for p in personeller:
                        pid = str(p.get("personel_id") or "").strip()
                        if not pid or pid in gun_ici_atanan:
                            continue

                        secili_gun = date.fromisoformat(tarih)
                        onceki_gun = son_atama_tarihleri.get(pid)
                        ardisik = int(ardisik_sayilari.get(pid) or 0)
                        if onceki_gun and (secili_gun - onceki_gun).days == 1 and ardisik >= max_ardisik_nobet:
                            red_nedeni = "ardisik_limit"
                            continue

                        if not self._dinlenme_yeterli_mi(son_bitisler.get(pid), vardiya_bas, min_dinlenme_saat):
                            red_nedeni = "min_dinlenme"
                            continue

                        skor = abs(hedefler.get(pid, 0.0) - (saatler.get(pid, 0.0) + saat))
                        if bool(p.get("mesai_istemiyor")):
                            skor += 8.0
                        if saat >= 24 and not bool(p.get("ister_24_saat")):
                            skor += 6.0
                        skor += float(atama_sayisi.get(pid, 0)) * 0.2

                        if secili_skor is None or skor < secili_skor:
                            secili_skor = skor
                            secili_pid = pid

                    if not secili_pid:
                        eksik.append(
                            {
                                "tarih": tarih,
                                "vardiya_id": vid,
                                "neden": red_nedeni,
                            }
                        )
                        continue

                    self._repo.plan_satir_ekle(
                        plan_id=plan_id,
                        personel_id=secili_pid,
                        vardiya_id=vid,
                        tarih=tarih,
                        saat_suresi=saat,
                        kaynak="algoritma",
                    )
                    satir_adet += 1
                    gun_ici_atanan.add(secili_pid)
                    saatler[secili_pid] = round(saatler.get(secili_pid, 0.0) + saat, 2)
                    atama_sayisi[secili_pid] = int(atama_sayisi.get(secili_pid, 0)) + 1
                    son_bitisler[secili_pid] = vardiya_bit
                    atama_gunu = date.fromisoformat(tarih)
                    onceki_gun = son_atama_tarihleri.get(secili_pid)
                    if onceki_gun and (atama_gunu - onceki_gun).days == 1:
                        ardisik_sayilari[secili_pid] = int(ardisik_sayilari.get(secili_pid) or 0) + 1
                    else:
                        ardisik_sayilari[secili_pid] = 1
                    son_atama_tarihleri[secili_pid] = atama_gunu

        devir_ozet: list[dict] = []
        for p in personeller:
            pid = str(p.get("personel_id") or "").strip()
            if not pid:
                continue
            hesap = self.personel_aylik_hedef_ve_devir_hesapla(
                bid,
                pid,
                y,
                m,
                gerceklesen_saat=float(saatler.get(pid, 0.0) or 0.0),
            )
            self.personel_aylik_devir_kaydet(bid, pid, y, m, float(hesap.get("yeni_devir_saat") or 0.0))
            devir_ozet.append(
                {
                    "personel_id": pid,
                    "devirli_hedef_saat": float(hesap.get("devirli_hedef_saat") or 0.0),
                    "gerceklesen_saat": float(hesap.get("gerceklesen_saat") or 0.0),
                    "yeni_devir_saat": float(hesap.get("yeni_devir_saat") or 0.0),
                }
            )

        return {
            "plan_id": plan_id,
            "satir_sayisi": satir_adet,
            "eksik_atama": eksik,
            "devir_ozet": devir_ozet,
        }

    @staticmethod
    def varsayilan_donem() -> tuple[int, int]:
        bugun = date.today()
        return bugun.year, bugun.month

    def tatil_aralik_listele(self, bas: str, bit: str) -> list[dict]:
        """Repo tatil listesini UI'a açar (bas/bit ISO tarih stringleri)."""
        return self._repo.tatil_aralik_listele(bas, bit)

