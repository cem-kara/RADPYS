# -*- coding: utf-8 -*-
"""app/db/repos/fhsz_repo.py - FHSZ tablosu SQL katmani."""
from __future__ import annotations

from app.db.repos.base import BaseRepo


class FhszRepo(BaseRepo):
    """fhsz tablosu CRUD. Sadece SQL - is mantigi yok."""

    def listele(
        self,
        yil: int | None = None,
        donem: int | None = None,
        personel_id: str | None = None,
    ) -> list[dict]:
        sql = (
            "SELECT f.*, p.ad, p.soyad, p.tc_kimlik, "
            "COALESCE(gyh.ad, gy_cur.ad) AS gorev_yeri_ad, "
            "COALESCE(gyh.sua_hakki, gy_cur.sua_hakki, 0) AS sua_hakki "
            "FROM fhsz f "
            "JOIN personel p ON p.id = f.personel_id "
            "LEFT JOIN gorev_yeri gy_cur ON gy_cur.id = p.gorev_yeri_id "
            "LEFT JOIN personel_gorev_gecmis pg ON pg.id = ("
            "  SELECT pg2.id "
            "  FROM personel_gorev_gecmis pg2 "
            "  WHERE pg2.personel_id = f.personel_id "
            "    AND pg2.baslama_tarihi <= printf('%04d-%02d-15', f.yil, f.donem) "
            "    AND (pg2.bitis_tarihi IS NULL OR pg2.bitis_tarihi >= printf('%04d-%02d-15', f.yil, f.donem)) "
            "  ORDER BY pg2.baslama_tarihi DESC, pg2.olusturuldu DESC "
            "  LIMIT 1"
            ") "
            "LEFT JOIN gorev_yeri gyh ON gyh.id = pg.gorev_yeri_id "
            "WHERE 1=1"
        )
        params: list = []
        if yil is not None:
            sql += " AND f.yil = ?"
            params.append(int(yil))
        if donem is not None:
            sql += " AND f.donem = ?"
            params.append(int(donem))
        if personel_id:
            sql += " AND f.personel_id = ?"
            params.append(personel_id)
        sql += " ORDER BY p.soyad, p.ad"
        return self._db.fetchall(sql, tuple(params))

    def donem_sil(self, yil: int, donem: int) -> None:
        self._db.execute(
            "DELETE FROM fhsz WHERE yil = ? AND donem = ?",
            (int(yil), int(donem)),
        )

    def ekle(self, veri: dict) -> str:
        pk = self._new_id()
        self._db.execute(
            """INSERT INTO fhsz (
                id, personel_id, yil, donem, aylik_gun, izin_gun,
                fiili_saat, calisma_kosulu, notlar
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                pk,
                veri["personel_id"],
                int(veri["yil"]),
                int(veri["donem"]),
                float(veri.get("aylik_gun") or 0.0),
                float(veri.get("izin_gun") or 0.0),
                float(veri.get("fiili_saat") or 0.0),
                str(veri.get("calisma_kosulu") or "B"),
                veri.get("notlar") or None,
            ),
        )
        return pk
