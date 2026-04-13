# -*- coding: utf-8 -*-
"""tests/test_saglik_service.py – SaglikService is kuralları birim testleri."""
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import Database
from app.db.migrations import run as migrate
from app.db.seed import seed_all as seed
from app.services.personel_service import PersonelService
from app.services.saglik_service import SaglikService


# ─────────────────────────── Fixtures ────────────────────────────


@pytest.fixture
def db(tmp_path):
    d = Database(tmp_path / "test.db")
    migrate(d)
    seed(d)
    yield d
    d.close()


@pytest.fixture
def svc(db):
    return SaglikService(db)


@pytest.fixture
def pid(db):
    """Testlerde kullanılacak aktif personel ID'si oluşturur."""
    psvc = PersonelService(db)
    return psvc.ekle(
        {
            "tc_kimlik": "10000000146",
            "ad": "Test",
            "soyad": "Personel",
            "memuriyet_baslama": "2020-01-01",
        }
    )


# ─────────────────────────── Yardımcı ────────────────────────────


def _kaydet(svc, pid, uzmanlik, yil=2025, muayene_id=None):
    return svc.muayene_kaydet(
        {
            "personel_id": pid,
            "uzmanlik": uzmanlik,
            "tarih": f"{yil}-06-15",
            "sonuc": "Uygun",
            "notlar": "",
            "belge_id": None,
        },
        muayene_id=muayene_id,
    )


# ─────────────────────────── Testler ────────────────────────────


def test_zorunlu_uzmanliklar_listesi(svc):
    """uzmanlik_secenekleri yalnızca 3 zorunlu uzmanlığı döndürür."""
    opts = svc.uzmanlik_secenekleri()
    assert len(opts) == 3
    norms = [svc._norm_uzmanlik(v) for v in opts]
    assert "dermatoloji" in norms
    assert "dahiliye" in norms
    assert "goz" in norms


def test_ilk_kayit_basarili(svc, pid):
    mid = _kaydet(svc, pid, "Dermatoloji")
    assert mid


def test_ayni_yil_ayni_uzmanlik_hata(svc, pid):
    """Aynı personel + yıl + uzmanlık ikinci kez girilirse ValueError fırlatılmalı."""
    _kaydet(svc, pid, "Dermatoloji")
    with pytest.raises(ValueError, match="zaten var"):
        _kaydet(svc, pid, "Dermatoloji")


def test_ayni_yil_farkli_uzmanlik_basarili(svc, pid):
    """Aynı personel + yıl için farklı uzmanlık kaydedilebilir."""
    _kaydet(svc, pid, "Dermatoloji")
    _kaydet(svc, pid, "Dahiliye")
    _kaydet(svc, pid, "Goz")
    kayitlar = svc.personel_muayene_kayitlari(pid)
    assert len([k for k in kayitlar if k["yil"] == 2025]) == 3


def test_zorunlu_olmayan_uzmanlik_hata(svc, pid):
    """3 ana uzmanlik dışında uzmanlik girişi ValueError fırlatmalı."""
    with pytest.raises(ValueError, match="3 ana uzmanlik"):
        _kaydet(svc, pid, "Kardiyoloji")


def test_bir_yil_sonra_normal(svc):
    """_bir_yil_sonra: normal tarihte yıl +1."""
    d = date(2024, 3, 10)
    result = svc._bir_yil_sonra(d)
    assert result == date(2025, 3, 10)


def test_bir_yil_sonra_29_subat(svc):
    """_bir_yil_sonra: 29 Şubat'tan sonra 28 Şubat döner (leap→non-leap)."""
    d = date(2024, 2, 29)  # 2024 artık yıl
    result = svc._bir_yil_sonra(d)
    assert result == date(2025, 2, 28)


def test_sonraki_tarih_otomatik_bir_yil(svc, pid):
    """muayene_kaydet sonucunda sonraki_kontrol = tarih + 1 yıl olmalı."""
    _kaydet(svc, pid, "Dermatoloji", yil=2025)
    kayitlar = svc.personel_muayene_kayitlari(pid)
    kayit = next(k for k in kayitlar if k["yil"] == 2025)
    assert kayit["sonraki_kontrol"] == "15.06.2026"


def test_personel_yil_uzmanlik_durumu_bos(svc, pid):
    """Hiç kayıt yoksa tüm 3 uzmanlik eksik görünür."""
    durum = svc.personel_yil_uzmanlik_durumu(pid, 2025)
    assert durum["tamamlandi"] is False
    assert len(durum["eksik"]) == 3
    assert len(durum["tamamlanan"]) == 0


def test_personel_yil_uzmanlik_durumu_tamam(svc, pid):
    """3 kayıt tamamlandıktan sonra tamamlandi=True olmalı."""
    for uz in ("Dermatoloji", "Dahiliye", "Goz"):
        _kaydet(svc, pid, uz)
    durum = svc.personel_yil_uzmanlik_durumu(pid, 2025)
    assert durum["tamamlandi"] is True
    assert len(durum["eksik"]) == 0
    assert len(durum["tamamlanan"]) == 3


def test_tek_rapor_kalitimi(svc, pid, db):
    """Aynı personel+yıl için farklı uzmanlik kayıtları aynı belge_id'yi paylaşır."""
    from app.db.repos.belge_repo import BelgeRepo
    from app.validators import bugun

    # Sahte bir belge kaydı oluştur
    repo = BelgeRepo(db)
    belge_id = repo.ekle(
        {
            "entity_turu": "muayene_formu",
            "entity_id": f"{pid}:2025",
            "dosya_adi": "rapor.pdf",
            "lokal_yol": "/tmp/rapor.pdf",
            "tur": "Periyodik Muayene Raporu",
            "aciklama": "test",
            "yuklendi": bugun(),
        }
    )
    # Dermatoloji kaydını bu belge ile gir
    svc.muayene_kaydet(
        {
            "personel_id": pid,
            "uzmanlik": "Dermatoloji",
            "tarih": "2025-06-15",
            "sonuc": "Uygun",
            "notlar": "",
            "belge_id": belge_id,
        }
    )
    # Dahiliye kaydını belge_id vermeden gir → servis otomatik miras almalı
    _kaydet(svc, pid, "Dahiliye")
    kayitlar = svc.tum_muayene_kayitlari(yil=2025)
    pid_kayitlari = [k for k in kayitlar if k["personel_id"] == pid]
    assert len(pid_kayitlari) == 2
    rapor = svc.personel_yil_tek_rapor(pid, 2025)
    assert rapor is not None
    assert rapor["belge_id"] == belge_id


def test_muayene_sil(svc, pid):
    """muayene_sil: kayıt silinmeli."""
    mid = _kaydet(svc, pid, "Dermatoloji")
    svc.muayene_sil(mid)
    kayitlar = svc.personel_muayene_kayitlari(pid)
    assert not any(k.get("yil") == 2025 for k in kayitlar)


def test_muayene_sil_bos_id_hata(svc):
    """muayene_sil: boş ID ValueError fırlatmalı."""
    with pytest.raises(ValueError):
        svc.muayene_sil("")
