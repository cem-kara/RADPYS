# -*- coding: utf-8 -*-
"""app/db/repos/dozimetre_repo.py - dozimetre tablosu SQL katmani."""
from __future__ import annotations

from app.db.repos.base import BaseRepo


class DozimetreRepo(BaseRepo):
    """dozimetre tablosu sorgulari. Sadece SQL, is mantigi yok."""

    def listele(
        self,
        yil: int | None = None,
        periyot: int | None = None,
        personel_id: str | None = None,
        birim: str | None = None,
    ) -> list[dict]:
        sql = (
            "WITH yil_periyot AS ("
            "  SELECT yil, MAX(periyot) AS max_periyot"
            "  FROM dozimetre"
            "  GROUP BY yil"
            "), cozum AS ("
            "  SELECT d.*, p.ad, p.soyad, p.tc_kimlik,"
            "  COALESCE("
            "    (SELECT gy2.ad FROM personel_gorev_gecmis pgg"
            "     JOIN gorev_yeri gy2 ON gy2.id = pgg.gorev_yeri_id"
            "     WHERE pgg.personel_id = d.personel_id"
            "       AND pgg.baslama_tarihi <= printf('%04d-%02d-15', d.yil,"
            "           MIN(12, MAX(1, CAST(((d.periyot - 1) * 12.0 / CASE WHEN yp.max_periyot > 0 THEN yp.max_periyot ELSE 1 END) AS INTEGER) + 1)))"
            "       AND (pgg.bitis_tarihi IS NULL"
            "            OR pgg.bitis_tarihi >= printf('%04d-%02d-15', d.yil,"
            "               MIN(12, MAX(1, CAST(((d.periyot - 1) * 12.0 / CASE WHEN yp.max_periyot > 0 THEN yp.max_periyot ELSE 1 END) AS INTEGER) + 1))))"
            "     ORDER BY pgg.baslama_tarihi DESC, pgg.olusturuldu DESC"
            "     LIMIT 1),"
            "    gy.ad"
            "  ) AS birim"
            "  FROM dozimetre d"
            "  JOIN personel p ON p.id = d.personel_id"
            "  LEFT JOIN gorev_yeri gy ON gy.id = p.gorev_yeri_id"
            "  LEFT JOIN yil_periyot yp ON yp.yil = d.yil"
            ") SELECT * FROM cozum WHERE 1=1"
        )
        params: list = []

        if yil is not None:
            sql += " AND yil = ?"
            params.append(int(yil))
        if periyot is not None:
            sql += " AND periyot = ?"
            params.append(int(periyot))
        if personel_id:
            sql += " AND personel_id = ?"
            params.append(str(personel_id))
        if birim:
            sql += " AND birim = ?"
            params.append(str(birim))

        sql += " ORDER BY yil DESC, periyot DESC, soyad, ad"
        return self._db.fetchall(sql, tuple(params))

    def rapor_listele(self, rapor_no: str) -> list[dict]:
        return self._db.fetchall(
            "SELECT * FROM dozimetre WHERE rapor_no = ? ORDER BY yil DESC, periyot DESC",
            (str(rapor_no or "").strip(),),
        )

    def ekle(self, veri: dict) -> str:
        did = self._new_id()
        self._db.execute(
            "INSERT INTO dozimetre ("
            "id, personel_id, rapor_no, yil, periyot, periyot_adi, "
            "dozimetre_no, tur, bolge, hp10, hp007, durum, olusturuldu"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'))",
            (
                did,
                veri["personel_id"],
                veri.get("rapor_no") or None,
                int(veri.get("yil") or 0),
                int(veri.get("periyot") or 0),
                veri.get("periyot_adi") or None,
                veri.get("dozimetre_no") or None,
                veri.get("tur") or None,
                veri.get("bolge") or None,
                veri.get("hp10"),
                veri.get("hp007"),
                veri.get("durum") or None,
            ),
        )
        return did
