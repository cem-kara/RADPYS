# -*- coding: utf-8 -*-
"""app/db/repos/izin_repo.py — İzin tablosu SQL katmanı"""
from __future__ import annotations
from app.db.repos.base import BaseRepo


class IzinRepo(BaseRepo):
    """izin tablosu CRUD. Sadece SQL — iş mantığı yok."""

    # ── Sorgular ──────────────────────────────────────────────────

    def listele(
        self,
        personel_id: str | None = None,
        yil: int | None = None,
        durum: str | None = None,
    ) -> list[dict]:
        sql = (
            "SELECT i.*, p.ad, p.soyad, p.kadro_unvani "
            "FROM izin i "
            "JOIN personel p ON p.id = i.personel_id "
            "WHERE 1=1"
        )
        params: list = []
        if personel_id:
            sql += " AND i.personel_id = ?"
            params.append(personel_id)
        if yil:
            sql += " AND strftime('%Y', i.baslama) = ?"
            params.append(str(yil))
        if durum:
            sql += " AND i.durum = ?"
            params.append(durum)
        sql += " ORDER BY i.baslama DESC"
        return self._db.fetchall(sql, tuple(params))

    def getir(self, pk: str) -> dict | None:
        return self._db.fetchone(
            "SELECT i.*, p.ad, p.soyad, p.kadro_unvani "
            "FROM izin i "
            "JOIN personel p ON p.id = i.personel_id "
            "WHERE i.id = ?",
            (pk,),
        )

    def cakisan_var_mi(
        self,
        personel_id: str,
        baslama: str,
        bitis: str,
        haric_id: str | None = None,
    ) -> bool:
        """Aynı personel için tarih aralığı çakışan aktif izin var mı?"""
        sql = (
            "SELECT 1 FROM izin "
            "WHERE personel_id = ? "
            "  AND durum = 'aktif' "
            "  AND baslama <= ? "
            "  AND bitis   >= ?"
        )
        params: list = [personel_id, bitis, baslama]
        if haric_id:
            sql += " AND id != ?"
            params.append(haric_id)
        return bool(self._db.fetchval(sql, tuple(params)))

    def yillik_kullanim(
        self,
        personel_id: str,
        yil: int,
        tur: str | None = None,
    ) -> int:
        """Belirtilen yılda kullanılan toplam izin günü (aktif kayıtlar)."""
        sql = (
            "SELECT COALESCE(SUM(gun), 0) FROM izin "
            "WHERE personel_id = ? "
            "  AND durum = 'aktif' "
            "  AND strftime('%Y', baslama) = ?"
        )
        params: list = [personel_id, str(yil)]
        if tur:
            sql += " AND tur = ?"
            params.append(tur)
        return self._db.fetchval(sql, tuple(params)) or 0

    # ── Yazma ─────────────────────────────────────────────────────

    def ekle(self, veri: dict) -> str:
        pk = self._new_id()
        self._db.execute(
            """INSERT INTO izin
                (id, personel_id, tur, baslama, gun, bitis, aciklama)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                pk,
                veri["personel_id"],
                veri["tur"],
                veri["baslama"],
                veri["gun"],
                veri["bitis"],
                veri.get("aciklama") or None,
            ),
        )
        return pk

    def bul_personel_tur_baslama(
        self,
        personel_id: str,
        tur: str,
        baslama: str,
    ) -> dict | None:
        """Aynı personel + tür + başlama tarihine sahip aktif/arşiv kayıt."""
        return self._db.fetchone(
            "SELECT * FROM izin WHERE personel_id=? AND tur=? AND baslama=? AND durum != 'iptal'",
            (personel_id, tur, baslama),
        )

    def guncelle(self, pk: str, veri: dict) -> None:
        """Varolan izin kaydını günceller (kaynak: düzeltme upload'u)."""
        self._db.execute(
            """UPDATE izin
               SET gun=?, bitis=?, aciklama=?
               WHERE id=?""",
            (
                veri["gun"],
                veri["bitis"],
                veri.get("aciklama") or None,
                pk,
            ),
        )

    def iptal(self, pk: str) -> None:
        self._db.execute(
            "UPDATE izin SET durum='iptal' WHERE id=?", (pk,)
        )
