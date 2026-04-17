# -*- coding: utf-8 -*-
"""app/db/repos/nobet_repo.py - nobet tablolari SQL katmani."""
from __future__ import annotations

from app.db.repos.base import BaseRepo


class NobetRepo(BaseRepo):
    """Nobet planlama tablolari icin temel SQL sorgulari."""

    def birimler_listele(self, aktif_only: bool = True) -> list[dict]:
        sql = "SELECT id, ad, kisaltma, aktif FROM nb_birim"
        if aktif_only:
            sql += " WHERE aktif = 1"
        sql += " ORDER BY ad"
        return self._db.fetchall(sql)

    def birim_getir(self, birim_id: str) -> dict | None:
        return self._db.fetchone(
            "SELECT id, ad, kisaltma, aktif FROM nb_birim WHERE id = ?",
            (str(birim_id or "").strip(),),
        )

    def birim_kural_getir(self, birim_id: str) -> dict | None:
        return self._db.fetchone(
            "SELECT * FROM nb_birim_kural WHERE birim_id = ?",
            (str(birim_id or "").strip(),),
        )

    def birim_kural_upsert(self, birim_id: str, veri: dict) -> None:
        mevcut = self.birim_kural_getir(birim_id)
        raw_max_ardisik = veri.get("max_ardisik_nobet")
        payload = {
            "min_dinlenme_saat": float(veri.get("min_dinlenme_saat") or 12),
            "resmi_tatil_calisma": int(veri.get("resmi_tatil_calisma") or 0),
            "dini_tatil_calisma": int(veri.get("dini_tatil_calisma") or 0),
            "arefe_baslangic_saat": str(veri.get("arefe_baslangic_saat") or "13:00").strip() or "13:00",
            "max_fazla_mesai_saat": float(veri.get("max_fazla_mesai_saat") or 0),
            "tolerans_saat": float(veri.get("tolerans_saat") or 7),
            "max_devreden_saat": float(veri.get("max_devreden_saat") or 12),
            "max_ardisik_nobet": 2 if raw_max_ardisik is None or str(raw_max_ardisik).strip() == "" else int(raw_max_ardisik),
            "manuel_limit_asimina_izin": int(veri.get("manuel_limit_asimina_izin") or 0),
        }
        if mevcut:
            self._db.execute(
                "UPDATE nb_birim_kural SET "
                "min_dinlenme_saat=?, resmi_tatil_calisma=?, dini_tatil_calisma=?, "
                "arefe_baslangic_saat=?, max_fazla_mesai_saat=?, tolerans_saat=?, "
                "max_devreden_saat=?, max_ardisik_nobet=?, manuel_limit_asimina_izin=?, guncellendi=date('now') "
                "WHERE birim_id=?",
                (
                    payload["min_dinlenme_saat"],
                    payload["resmi_tatil_calisma"],
                    payload["dini_tatil_calisma"],
                    payload["arefe_baslangic_saat"],
                    payload["max_fazla_mesai_saat"],
                    payload["tolerans_saat"],
                    payload["max_devreden_saat"],
                    payload["max_ardisik_nobet"],
                    payload["manuel_limit_asimina_izin"],
                    str(birim_id or "").strip(),
                ),
            )
            return

        self._db.execute(
            "INSERT INTO nb_birim_kural ("
            "id, birim_id, min_dinlenme_saat, resmi_tatil_calisma, dini_tatil_calisma, "
            "arefe_baslangic_saat, max_fazla_mesai_saat, tolerans_saat, max_devreden_saat, max_ardisik_nobet, manuel_limit_asimina_izin"
            ") VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (
                self._new_id(),
                str(birim_id or "").strip(),
                payload["min_dinlenme_saat"],
                payload["resmi_tatil_calisma"],
                payload["dini_tatil_calisma"],
                payload["arefe_baslangic_saat"],
                payload["max_fazla_mesai_saat"],
                payload["tolerans_saat"],
                payload["max_devreden_saat"],
                payload["max_ardisik_nobet"],
                payload["manuel_limit_asimina_izin"],
            ),
        )

    # ── Şablon (global) metodları ─────────────────────────────────

    def sablon_listele(self, aktif_only: bool = True) -> list[dict]:
        sql = "SELECT id, ad, baslangic_saat, bitis_saat, saat_suresi, aciklama, aktif FROM nb_vardiya_sablon"
        if aktif_only:
            sql += " WHERE aktif = 1"
        sql += " ORDER BY ad"
        return self._db.fetchall(sql)

    def sablon_getir(self, sablon_id: str) -> dict | None:
        return self._db.fetchone(
            "SELECT id, ad, baslangic_saat, bitis_saat, saat_suresi, aciklama, aktif "
            "FROM nb_vardiya_sablon WHERE id = ?",
            (str(sablon_id or "").strip(),),
        )

    def sablon_ekle(self, ad: str, baslangic_saat: str, bitis_saat: str, saat_suresi: float, aciklama: str = "") -> str:
        sid = self._new_id()
        self._db.execute(
            "INSERT INTO nb_vardiya_sablon (id, ad, baslangic_saat, bitis_saat, saat_suresi, aciklama) "
            "VALUES (?,?,?,?,?,?)",
            (sid, str(ad).strip(), str(baslangic_saat).strip(), str(bitis_saat).strip(), float(saat_suresi), str(aciklama or "").strip()),
        )
        return sid

    def sablon_pasife_al(self, sablon_id: str) -> None:
        self._db.execute(
            "UPDATE nb_vardiya_sablon SET aktif = 0 WHERE id = ?",
            (str(sablon_id or "").strip(),),
        )

    # ── Birim vardiya (şablon ataması) metodları ──────────────────

    def vardiya_listele(self, birim_id: str, aktif_only: bool = True) -> list[dict]:
        sql = (
            "SELECT v.id, v.birim_id, v.ad, v.saat_suresi, v.baslangic_saat, v.bitis_saat, "
            "v.max_personel, v.sablon_id, v.ana, v.aktif, "
            "s.ad AS sablon_ad "
            "FROM nb_vardiya v "
            "LEFT JOIN nb_vardiya_sablon s ON s.id = v.sablon_id "
            "WHERE v.birim_id = ?"
        )
        params: list = [str(birim_id or "").strip()]
        if aktif_only:
            sql += " AND v.aktif = 1"
        sql += " ORDER BY v.ad"
        return self._db.fetchall(sql, tuple(params))

    def vardiya_ekle(
        self,
        birim_id: str,
        ad: str,
        saat_suresi: float,
        baslangic_saat: str,
        bitis_saat: str,
        max_personel: int = 1,
        sablon_id: str | None = None,
        ana: int = 1,
        aktif: int = 1,
    ) -> str:
        vid = self._new_id()
        self._db.execute(
            "INSERT INTO nb_vardiya (id, birim_id, ad, saat_suresi, baslangic_saat, bitis_saat, max_personel, sablon_id, ana, aktif) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                vid,
                str(birim_id or "").strip(),
                str(ad or "").strip(),
                float(saat_suresi),
                str(baslangic_saat or "").strip(),
                str(bitis_saat or "").strip(),
                int(max_personel),
                str(sablon_id or "").strip() or None,
                int(ana),
                int(aktif),
            ),
        )
        return vid

    def vardiya_max_personel_guncelle(self, vardiya_id: str, max_personel: int) -> None:
        self._db.execute(
            "UPDATE nb_vardiya SET max_personel = ? WHERE id = ?",
            (int(max_personel), str(vardiya_id or "").strip()),
        )

    def vardiya_pasife_al(self, vardiya_id: str) -> None:
        self._db.execute(
            "UPDATE nb_vardiya SET aktif = 0 WHERE id = ?",
            (str(vardiya_id or "").strip(),),
        )

    def vardiya_getir(self, vardiya_id: str) -> dict | None:
        return self._db.fetchone(
            "SELECT id, birim_id, ad, saat_suresi, baslangic_saat, bitis_saat, max_personel, aktif "
            "FROM nb_vardiya WHERE id = ?",
            (str(vardiya_id or "").strip(),),
        )

    def sablon_birime_ata(
        self,
        birim_id: str,
        sablon_id: str,
        max_personel: int,
    ) -> str:
        """Şablondan birime vardiya kaydı oluşturur; aynı şablon zaten atandıysa id döner."""
        mevcut = self._db.fetchone(
            "SELECT id FROM nb_vardiya WHERE birim_id = ? AND sablon_id = ? AND aktif = 1",
            (str(birim_id or "").strip(), str(sablon_id or "").strip()),
        )
        if mevcut:
            vid = str(mevcut.get("id") or "")
            self.vardiya_max_personel_guncelle(vid, max_personel)
            return vid
        sablon = self.sablon_getir(sablon_id)
        if sablon is None:
            raise ValueError("Sablon bulunamadi.")
        return self.vardiya_ekle(
            birim_id=str(birim_id or "").strip(),
            ad=str(sablon.get("ad") or ""),
            saat_suresi=float(sablon.get("saat_suresi") or 0),
            baslangic_saat=str(sablon.get("baslangic_saat") or ""),
            bitis_saat=str(sablon.get("bitis_saat") or ""),
            max_personel=int(max_personel),
            sablon_id=str(sablon_id or "").strip(),
        )

    def birim_personellerini_esitle(self, birim_id: str) -> int:
        rows = self._db.fetchall(
            "SELECT p.id AS personel_id "
            "FROM nb_birim nb "
            "JOIN gorev_yeri gy ON gy.ad = nb.ad "
            "JOIN personel p ON p.gorev_yeri_id = gy.id "
            "WHERE nb.id = ? AND p.durum = 'aktif'",
            (str(birim_id or "").strip(),),
        )
        eklenen = 0
        for row in rows:
            pid = str(row.get("personel_id") or "").strip()
            if not pid:
                continue
            if self._db.fetchval(
                "SELECT 1 FROM nb_personel WHERE birim_id = ? AND personel_id = ? AND aktif = 1",
                (str(birim_id or "").strip(), pid),
            ):
                continue
            self._db.execute(
                "INSERT INTO nb_personel (id, birim_id, personel_id, baslama, aktif) VALUES (?,?,?,?,1)",
                (self._new_id(), str(birim_id or "").strip(), pid, "2000-01-01"),
            )
            eklenen += 1
        return eklenen

    def birim_personel_listele(self, birim_id: str) -> list[dict]:
        return self._db.fetchall(
            "SELECT p.id AS personel_id, p.ad, p.soyad, p.tc_kimlik, "
            "COALESCE(k.ister_24_saat, 0) AS ister_24_saat, "
            "COALESCE(k.mesai_istemiyor, 0) AS mesai_istemiyor, "
            "COALESCE(k.max_fazla_mesai_saat, 0) AS max_fazla_mesai_saat, "
            "COALESCE(k.tolerans_saat, 7) AS tolerans_saat, "
            "COALESCE(k.max_devreden_saat, 12) AS max_devreden_saat "
            "FROM nb_personel np "
            "JOIN personel p ON p.id = np.personel_id "
            "LEFT JOIN nb_personel_kural k ON k.birim_id = np.birim_id AND k.personel_id = np.personel_id "
            "WHERE np.birim_id = ? AND np.aktif = 1 "
            "ORDER BY p.soyad, p.ad",
            (str(birim_id or "").strip(),),
        )

    def birim_personel_var_mi(self, birim_id: str, personel_id: str) -> bool:
        return bool(
            self._db.fetchval(
                "SELECT 1 FROM nb_personel WHERE birim_id = ? AND personel_id = ? AND aktif = 1",
                (str(birim_id or "").strip(), str(personel_id or "").strip()),
            )
        )

    def personel_kanuni_mesai_listele(self, birim_id: str, aktif_only: bool = True) -> list[dict]:
        sql = (
            "SELECT km.id, km.birim_id, km.personel_id, km.baslangic_tarih, km.bitis_tarih, "
            "km.duzenleme_tipi, km.deger, km.aciklama, km.aktif, "
            "p.ad, p.soyad "
            "FROM nb_personel_kanuni_mesai km "
            "JOIN personel p ON p.id = km.personel_id "
            "WHERE km.birim_id = ?"
        )
        params: list = [str(birim_id or "").strip()]
        if aktif_only:
            sql += " AND km.aktif = 1"
        sql += " ORDER BY km.baslangic_tarih DESC, p.soyad, p.ad"
        return self._db.fetchall(sql, tuple(params))

    def personel_kanuni_mesai_donem_listele(
        self,
        birim_id: str,
        personel_id: str,
        ay_bas: str,
        ay_bit: str,
    ) -> list[dict]:
        return self._db.fetchall(
            "SELECT id, birim_id, personel_id, baslangic_tarih, bitis_tarih, duzenleme_tipi, deger, aciklama "
            "FROM nb_personel_kanuni_mesai "
            "WHERE birim_id = ? AND personel_id = ? AND aktif = 1 "
            "AND baslangic_tarih <= ? "
            "AND COALESCE(bitis_tarih, '9999-12-31') >= ? "
            "ORDER BY baslangic_tarih DESC",
            (
                str(birim_id or "").strip(),
                str(personel_id or "").strip(),
                str(ay_bit or "").strip(),
                str(ay_bas or "").strip(),
            ),
        )

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
        kid = self._new_id()
        self._db.execute(
            "INSERT INTO nb_personel_kanuni_mesai ("
            "id, birim_id, personel_id, baslangic_tarih, bitis_tarih, duzenleme_tipi, deger, aciklama, aktif"
            ") VALUES (?,?,?,?,?,?,?,?,1)",
            (
                kid,
                str(birim_id or "").strip(),
                str(personel_id or "").strip(),
                str(baslangic_tarih or "").strip(),
                str(bitis_tarih or "").strip() or None,
                str(duzenleme_tipi or "").strip(),
                float(deger),
                str(aciklama or "").strip() or None,
            ),
        )
        return kid

    def personel_kanuni_mesai_pasife_al(self, kayit_id: str) -> None:
        self._db.execute(
            "UPDATE nb_personel_kanuni_mesai SET aktif = 0, guncellendi = date('now') WHERE id = ?",
            (str(kayit_id or "").strip(),),
        )

    def tatil_aralik_listele(self, bas: str, bit: str) -> list[dict]:
        return self._db.fetchall(
            "SELECT tarih, yarim_gun FROM tatil WHERE tarih >= ? AND tarih <= ? ORDER BY tarih",
            (str(bas or "").strip(), str(bit or "").strip()),
        )

    def personel_devir_onceki_getir(self, birim_id: str, personel_id: str, yil: int, ay: int) -> float:
        row = self._db.fetchone(
            "SELECT devir_saat FROM nb_personel_devir "
            "WHERE birim_id = ? AND personel_id = ? "
            "AND (yil < ? OR (yil = ? AND ay < ?)) "
            "ORDER BY yil DESC, ay DESC LIMIT 1",
            (
                str(birim_id or "").strip(),
                str(personel_id or "").strip(),
                int(yil),
                int(yil),
                int(ay),
            ),
        )
        return float((row or {}).get("devir_saat") or 0.0)

    def personel_devir_upsert(self, birim_id: str, personel_id: str, yil: int, ay: int, devir_saat: float) -> None:
        mevcut = self._db.fetchval(
            "SELECT 1 FROM nb_personel_devir WHERE birim_id = ? AND personel_id = ? AND yil = ? AND ay = ?",
            (str(birim_id or "").strip(), str(personel_id or "").strip(), int(yil), int(ay)),
        )
        if mevcut:
            self._db.execute(
                "UPDATE nb_personel_devir SET devir_saat = ?, guncellendi = date('now') "
                "WHERE birim_id = ? AND personel_id = ? AND yil = ? AND ay = ?",
                (
                    float(devir_saat),
                    str(birim_id or "").strip(),
                    str(personel_id or "").strip(),
                    int(yil),
                    int(ay),
                ),
            )
            return
        self._db.execute(
            "INSERT INTO nb_personel_devir (id, birim_id, personel_id, yil, ay, devir_saat) VALUES (?,?,?,?,?,?)",
            (
                self._new_id(),
                str(birim_id or "").strip(),
                str(personel_id or "").strip(),
                int(yil),
                int(ay),
                float(devir_saat),
            ),
        )

    def personel_kural_upsert(self, birim_id: str, personel_id: str, veri: dict) -> None:
        mevcut = self._db.fetchval(
            "SELECT 1 FROM nb_personel_kural WHERE birim_id = ? AND personel_id = ?",
            (str(birim_id or "").strip(), str(personel_id or "").strip()),
        )
        payload = {
            "ister_24_saat": int(veri.get("ister_24_saat") or 0),
            "mesai_istemiyor": int(veri.get("mesai_istemiyor") or 0),
            "max_fazla_mesai_saat": float(veri.get("max_fazla_mesai_saat") or 0),
            "tolerans_saat": float(veri.get("tolerans_saat") or 7),
            "max_devreden_saat": float(veri.get("max_devreden_saat") or 12),
        }
        if mevcut:
            self._db.execute(
                "UPDATE nb_personel_kural SET "
                "ister_24_saat=?, mesai_istemiyor=?, max_fazla_mesai_saat=?, tolerans_saat=?, max_devreden_saat=?, guncellendi=date('now') "
                "WHERE birim_id=? AND personel_id=?",
                (
                    payload["ister_24_saat"],
                    payload["mesai_istemiyor"],
                    payload["max_fazla_mesai_saat"],
                    payload["tolerans_saat"],
                    payload["max_devreden_saat"],
                    str(birim_id or "").strip(),
                    str(personel_id or "").strip(),
                ),
            )
            return

        self._db.execute(
            "INSERT INTO nb_personel_kural ("
            "id, birim_id, personel_id, ister_24_saat, mesai_istemiyor, max_fazla_mesai_saat, tolerans_saat, max_devreden_saat"
            ") VALUES (?,?,?,?,?,?,?,?)",
            (
                self._new_id(),
                str(birim_id or "").strip(),
                str(personel_id or "").strip(),
                payload["ister_24_saat"],
                payload["mesai_istemiyor"],
                payload["max_fazla_mesai_saat"],
                payload["tolerans_saat"],
                payload["max_devreden_saat"],
            ),
        )

    def birimleri_gorev_yerinden_esitle(self) -> int:
        rows = self._db.fetchall(
            "SELECT ad, kisaltma FROM gorev_yeri WHERE COALESCE(aktif, 1) = 1 ORDER BY ad"
        )
        eklenen = 0
        for row in rows:
            ad = str(row.get("ad") or "").strip()
            if not ad:
                continue
            mevcut = self._db.fetchval("SELECT 1 FROM nb_birim WHERE ad = ?", (ad,))
            if mevcut:
                continue
            self._db.execute(
                "INSERT INTO nb_birim (id, ad, kisaltma, aktif) VALUES (?,?,?,1)",
                (self._new_id(), ad, str(row.get("kisaltma") or "").strip() or None),
            )
            eklenen += 1
        return eklenen

    def plan_listele(self, yil: int | None = None, ay: int | None = None) -> list[dict]:
        sql = (
            "SELECT np.id, np.birim_id, nb.ad AS birim_ad, nb.kisaltma AS birim_kisaltma, "
            "np.yil, np.ay, np.durum, np.notlar, np.onaylayan, np.olusturuldu, "
            "(SELECT COUNT(*) FROM nb_satir ns WHERE ns.plan_id = np.id) AS satir_sayisi "
            "FROM nb_plan np "
            "JOIN nb_birim nb ON nb.id = np.birim_id "
            "WHERE 1=1"
        )
        params: list = []
        if yil is not None:
            sql += " AND np.yil = ?"
            params.append(int(yil))
        if ay is not None:
            sql += " AND np.ay = ?"
            params.append(int(ay))
        sql += " ORDER BY np.yil DESC, np.ay DESC, nb.ad"
        return self._db.fetchall(sql, tuple(params))

    def plan_getir(self, birim_id: str, yil: int, ay: int) -> dict | None:
        return self._db.fetchone(
            "SELECT * FROM nb_plan WHERE birim_id = ? AND yil = ? AND ay = ?",
            (str(birim_id or "").strip(), int(yil), int(ay)),
        )

    def plan_ekle(
        self,
        birim_id: str,
        yil: int,
        ay: int,
        durum: str = "taslak",
        notlar: str = "",
        onaylayan: str | None = None,
    ) -> str:
        pid = self._new_id()
        self._db.execute(
            "INSERT INTO nb_plan (id, birim_id, yil, ay, durum, notlar, onaylayan) "
            "VALUES (?,?,?,?,?,?,?)",
            (
                pid,
                str(birim_id or "").strip(),
                int(yil),
                int(ay),
                str(durum or "taslak").strip() or "taslak",
                str(notlar or "").strip(),
                str(onaylayan or "").strip() or None,
            ),
        )
        return pid

    def plan_satir_listele(self, plan_id: str) -> list[dict]:
        return self._db.fetchall(
            "SELECT id, plan_id, personel_id, vardiya_id, tarih, saat_suresi, kaynak, olusturuldu "
            "FROM nb_satir WHERE plan_id = ? ORDER BY tarih, vardiya_id, personel_id",
            (str(plan_id or "").strip(),),
        )

    def plan_satir_detay_listele(self, plan_id: str) -> list[dict]:
        return self._db.fetchall(
            "SELECT s.id, s.plan_id, s.personel_id, s.vardiya_id, s.tarih, s.saat_suresi, s.kaynak, "
            "p.ad, p.soyad, v.ad AS vardiya_ad "
            "FROM nb_satir s "
            "JOIN personel p ON p.id = s.personel_id "
            "JOIN nb_vardiya v ON v.id = s.vardiya_id "
            "WHERE s.plan_id = ? "
            "ORDER BY s.tarih, p.soyad, p.ad",
            (str(plan_id or "").strip(),),
        )

    def plan_satirlari_sil(self, plan_id: str) -> None:
        self._db.execute(
            "DELETE FROM nb_satir WHERE plan_id = ?",
            (str(plan_id or "").strip(),),
        )

    def plan_satir_ekle(
        self,
        plan_id: str,
        personel_id: str,
        vardiya_id: str,
        tarih: str,
        saat_suresi: float,
        kaynak: str = "algoritma",
    ) -> str:
        sid = self._new_id()
        self._db.execute(
            "INSERT INTO nb_satir (id, plan_id, personel_id, vardiya_id, tarih, saat_suresi, kaynak) "
            "VALUES (?,?,?,?,?,?,?)",
            (
                sid,
                str(plan_id or "").strip(),
                str(personel_id or "").strip(),
                str(vardiya_id or "").strip(),
                str(tarih or "").strip(),
                float(saat_suresi),
                str(kaynak or "algoritma").strip() or "algoritma",
            ),
        )
        return sid
