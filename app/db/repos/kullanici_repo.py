# -*- coding: utf-8 -*-
"""app/db/repos/kullanici_repo.py — Kullanici tablosu SQL katmani"""
from __future__ import annotations
from app.db.repos.base import BaseRepo


class KullaniciRepo(BaseRepo):
    """kullanici tablosu CRUD. Sadece SQL."""

    def listele(self) -> list[dict]:
        return self._db.fetchall(
            "SELECT id, ad, rol, aktif, son_giris, olusturuldu "
            "FROM kullanici ORDER BY ad"
        )

    def id_ile_getir(self, kullanici_id: str) -> dict | None:
        return self._db.fetchone(
            "SELECT * FROM kullanici WHERE id = ?",
            (kullanici_id,),
        )

    def ad_ile_getir(self, kullanici_adi: str) -> dict | None:
        return self._db.fetchone(
            "SELECT * FROM kullanici WHERE ad = ?",
            (kullanici_adi,),
        )

    def ad_var_mi(self, kullanici_adi: str) -> bool:
        return bool(self._db.fetchval(
            "SELECT 1 FROM kullanici WHERE ad = ?",
            (kullanici_adi,),
        ))

    def ekle(self, veri: dict) -> str:
        kid = self._new_id()
        self._db.execute(
            "INSERT INTO kullanici (id, ad, sifre_hash, personel_id, rol, aktif, sifre_degismeli) "
            "VALUES (?,?,?,?,?,?,?)",
            (
                kid,
                veri["ad"],
                veri["sifre_hash"],
                veri.get("personel_id"),
                veri["rol"],
                1 if veri.get("aktif", True) else 0,
                1 if veri.get("sifre_degismeli", True) else 0,
            ),
        )
        return kid

    def guncelle(self, kullanici_id: str, veri: dict) -> None:
        korunan = {"id", "olusturuldu", "ad"}
        alanlar = {k: v for k, v in veri.items() if k not in korunan}
        if not alanlar:
            return

        set_sql = ", ".join(f"{k} = ?" for k in alanlar)
        params = list(alanlar.values()) + [kullanici_id]
        self._db.execute(
            f"UPDATE kullanici SET {set_sql} WHERE id = ?",
            tuple(params),
        )

    def son_giris_guncelle(self, kullanici_id: str, zaman: str) -> None:
        self._db.execute(
            "UPDATE kullanici SET son_giris = ? WHERE id = ?",
            (zaman, kullanici_id),
        )
