# -*- coding: utf-8 -*-
"""app/db/repos/personel_repo.py — Personel tablosu SQL katmanı"""
from __future__ import annotations
from app.db.repos.base import BaseRepo
from app.validators import bugun


class PersonelRepo(BaseRepo):
    """
    personel tablosu CRUD.
    Sadece SQL — iş mantığı servis katmanında.
    """

    # ── Sorgular ──────────────────────────────────────────────────

    def listele(self, aktif_only: bool = True) -> list[dict]:
        """Tüm personeli soyad+ad sırasıyla döner."""
        if aktif_only:
            return self._db.fetchall(
                "SELECT p.*, gy.ad AS gorev_yeri_ad, gy.sua_hakki "
                "FROM personel p "
                "LEFT JOIN gorev_yeri gy ON p.gorev_yeri_id = gy.id "
                "WHERE p.durum != 'ayrildi' "
                "ORDER BY p.soyad, p.ad"
            )
        return self._db.fetchall(
            "SELECT p.*, gy.ad AS gorev_yeri_ad, gy.sua_hakki "
            "FROM personel p "
            "LEFT JOIN gorev_yeri gy ON p.gorev_yeri_id = gy.id "
            "ORDER BY p.soyad, p.ad"
        )

    def getir(self, personel_id: str) -> dict | None:
        return self._db.fetchone(
            "SELECT p.*, gy.ad AS gorev_yeri_ad, gy.sua_hakki "
            "FROM personel p "
            "LEFT JOIN gorev_yeri gy ON p.gorev_yeri_id = gy.id "
            "WHERE p.id = ?",
            (personel_id,),
        )

    def tc_ile_getir(self, tc: str) -> dict | None:
        return self._db.fetchone(
            "SELECT p.*, gy.ad AS gorev_yeri_ad, gy.sua_hakki "
            "FROM personel p "
            "LEFT JOIN gorev_yeri gy ON p.gorev_yeri_id = gy.id "
            "WHERE p.tc_kimlik = ?",
            (tc,),
        )

    def tc_var_mi(self, tc: str) -> bool:
        return bool(self._db.fetchval(
            "SELECT 1 FROM personel WHERE tc_kimlik = ?", (tc,)
        ))

    def say(self, durum: str | None = None) -> int:
        if durum:
            return self._db.fetchval(
                "SELECT COUNT(*) FROM personel WHERE durum = ?", (durum,)
            ) or 0
        return self._db.fetchval("SELECT COUNT(*) FROM personel") or 0

    def gorev_gecmisi_listele(self, personel_id: str) -> list[dict]:
        """Personelin gorev yeri gecmisini yeninden eskiye listeler."""
        return self._db.fetchall(
            "SELECT pg.*, gy.ad AS gorev_yeri_ad "
            "FROM personel_gorev_gecmis pg "
            "LEFT JOIN gorev_yeri gy ON gy.id = pg.gorev_yeri_id "
            "WHERE pg.personel_id = ? "
            "ORDER BY pg.baslama_tarihi DESC, pg.olusturuldu DESC",
            (personel_id,),
        )

    def aktif_gorev_gecmisi_getir(self, personel_id: str) -> dict | None:
        """Personelin bitis_tarihi bos olan aktif gorev kaydini getirir."""
        return self._db.fetchone(
            "SELECT * FROM personel_gorev_gecmis "
            "WHERE personel_id = ? AND bitis_tarihi IS NULL "
            "ORDER BY baslama_tarihi DESC, olusturuldu DESC "
            "LIMIT 1",
            (personel_id,),
        )

    def gorev_yeri_tarihte_getir(self, personel_id: str, tarih: str) -> dict | None:
        """Verilen tarihte personelin gecmis kaydindan gorev yerini getirir."""
        return self._db.fetchone(
            "SELECT pg.*, gy.ad AS gorev_yeri_ad, gy.sua_hakki "
            "FROM personel_gorev_gecmis pg "
            "LEFT JOIN gorev_yeri gy ON gy.id = pg.gorev_yeri_id "
            "WHERE pg.personel_id = ? "
            "  AND pg.baslama_tarihi <= ? "
            "  AND (pg.bitis_tarihi IS NULL OR pg.bitis_tarihi >= ?) "
            "ORDER BY pg.baslama_tarihi DESC, pg.olusturuldu DESC "
            "LIMIT 1",
            (personel_id, tarih, tarih),
        )

    def gorev_gecmisi_ekle(
        self,
        personel_id: str,
        gorev_yeri_id: str,
        baslama_tarihi: str,
        bitis_tarihi: str | None = None,
        aciklama: str = "",
    ) -> str:
        """Personel icin yeni gorev yeri gecmis kaydi olusturur."""
        kayit_id = self._new_id()
        self._db.execute(
            "INSERT INTO personel_gorev_gecmis "
            "(id, personel_id, gorev_yeri_id, baslama_tarihi, bitis_tarihi, aciklama) "
            "VALUES (?,?,?,?,?,?)",
            (
                kayit_id,
                personel_id,
                gorev_yeri_id,
                baslama_tarihi,
                bitis_tarihi,
                aciklama or "",
            ),
        )
        return kayit_id

    def gorev_gecmisi_getir(self, kayit_id: str) -> dict | None:
        """Tek bir gorev gecmisi kaydini getirir."""
        return self._db.fetchone(
            "SELECT * FROM personel_gorev_gecmis WHERE id = ?",
            (kayit_id,),
        )

    def gorev_gecmisi_guncelle(self, kayit_id: str, veri: dict) -> None:
        """Gorev gecmisi kaydinda izinli alanlari gunceller."""
        korunan = {"id", "personel_id", "olusturuldu"}
        guncellenecek = {k: v for k, v in veri.items() if k not in korunan}
        if not guncellenecek:
            return
        guncellenecek["guncellendi"] = bugun()
        alanlar = ", ".join(f"{k} = ?" for k in guncellenecek)
        degerler = list(guncellenecek.values()) + [kayit_id]
        self._db.execute(
            f"UPDATE personel_gorev_gecmis SET {alanlar} WHERE id = ?",
            tuple(degerler),
        )

    def aktif_gorev_gecmisini_kapat(self, personel_id: str, bitis_tarihi: str) -> None:
        """Aktif gorev gecmisi kaydini verilen tarihle kapatir."""
        aktif = self.aktif_gorev_gecmisi_getir(personel_id)
        if not aktif:
            return
        kapanis_tarihi = bitis_tarihi
        baslama_tarihi = str(aktif.get("baslama_tarihi") or "")
        if kapanis_tarihi and baslama_tarihi and kapanis_tarihi < baslama_tarihi:
            kapanis_tarihi = baslama_tarihi
        self._db.execute(
            "UPDATE personel_gorev_gecmis "
            "SET bitis_tarihi = ?, guncellendi = ? "
            "WHERE id = ? AND bitis_tarihi IS NULL",
            (kapanis_tarihi, bugun(), aktif["id"]),
        )

    # ── Yazma ─────────────────────────────────────────────────────

    def ekle(self, veri: dict) -> str:
        """Yeni personel ekler, üretilen ID'yi döner."""
        pid = self._new_id()
        self._db.execute(
            """INSERT INTO personel (
                id, tc_kimlik, ad, soyad,
                dogum_tarihi, dogum_yeri,
                hizmet_sinifi, kadro_unvani,
                gorev_yeri_id, sicil_no,
                memuriyet_baslama,
                telefon, e_posta,
                okul_1, fakulte_1, mezuniyet_1, diploma_no_1,
                okul_2, fakulte_2, mezuniyet_2, diploma_no_2,
                durum
            ) VALUES (
                ?,?,?,?,
                ?,?,
                ?,?,
                ?,?,
                ?,
                ?,?,
                ?,?,?,?,
                ?,?,?,?,
                'aktif'
            )""",
            (
                pid,
                veri.get("tc_kimlik", ""),
                veri.get("ad", ""),
                veri.get("soyad", ""),
                veri.get("dogum_tarihi"),
                veri.get("dogum_yeri"),
                veri.get("hizmet_sinifi"),
                veri.get("kadro_unvani"),
                veri.get("gorev_yeri_id"),
                veri.get("sicil_no"),
                veri.get("memuriyet_baslama"),
                veri.get("telefon"),
                veri.get("e_posta"),
                veri.get("okul_1"),
                veri.get("fakulte_1"),
                veri.get("mezuniyet_1"),
                veri.get("diploma_no_1"),
                veri.get("okul_2"),
                veri.get("fakulte_2"),
                veri.get("mezuniyet_2"),
                veri.get("diploma_no_2"),
            ),
        )
        return pid

    def guncelle(self, personel_id: str, veri: dict) -> None:
        """Verilen alanları günceller. id ve tc_kimlik değiştirilemez."""
        korunan = {"id", "tc_kimlik", "olusturuldu"}
        guncellenecek = {k: v for k, v in veri.items() if k not in korunan}
        if not guncellenecek:
            return
        guncellenecek["guncellendi"] = bugun()
        alanlar    = ", ".join(f"{k} = ?" for k in guncellenecek)
        degerler   = list(guncellenecek.values()) + [personel_id]
        self._db.execute(
            f"UPDATE personel SET {alanlar} WHERE id = ?",
            tuple(degerler),
        )

    def gorev_yeri_guncelle(self, personel_id: str,
                            gorev_yeri_id: str | None) -> None:
        self._db.execute(
            "UPDATE personel SET gorev_yeri_id = ?, guncellendi = ? "
            "WHERE id = ?",
            (gorev_yeri_id, bugun(), personel_id),
        )
