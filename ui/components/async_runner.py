# -*- coding: utf-8 -*-
"""
ui/components/async_runner.py
─────────────────────────────
Tek generic QThread implementasyonu.
Projenin her yerinde bu kullanılır — başka QThread subclass'ı yazılmaz.

Eski kodda 20+ farklı _Loader/_Worker/_DbSaver vardı.
Hepsi bu sınıfla değiştirildi.

Kullanım:
    from ui.components.async_runner import AsyncRunner

    self._runner = AsyncRunner(
        fn=lambda: self._svc.personel_listele(),
        on_done=self._on_data,
        on_error=self._on_error,
    )
    self._runner.start()

    def _on_data(self, veri):
        self._tablo.set_veri(veri)

    def _on_error(self, mesaj):
        self._alert.goster(mesaj)

Özellikler:
    - fn() sonucu done sinyaliyle döner
    - Exception mesajı error sinyaliyle döner
    - is_running() ile çalışıp çalışmadığı sorgulanabilir
    - cancel() ile çalışan thread durdurulamaz (async cancel yok)
      ama sonuç sinyali emit edilmez
"""
from __future__ import annotations
from typing import Callable, Any
from PySide6.QtCore import QThread, Signal


class AsyncRunner(QThread):
    """
    Tek kullanımlık arkaplan işçisi.
    Servis metodunu UI thread'ini dondurmadan çalıştırır.
    """

    done  = Signal(object)   # fn() sonucu
    error = Signal(str)      # Exception mesajı

    def __init__(
        self,
        fn: Callable[[], Any],
        on_done: Callable = None,
        on_error: Callable = None,
        parent=None,
    ):
        super().__init__(parent)
        self._fn       = fn
        self._iptal    = False

        if on_done:
            self.done.connect(on_done)
        if on_error:
            self.error.connect(on_error)

    def run(self):
        try:
            sonuc = self._fn()
            if not self._iptal:
                self.done.emit(sonuc)
        except Exception as exc:
            if not self._iptal:
                self.error.emit(str(exc))

    def iptal(self):
        """Sonuç sinyallerini susturur (thread durdurulamaz)."""
        self._iptal = True


class AsyncButton:
    """
    Buton + AsyncRunner kombinasyonu.
    Buton tıklandığında arkaplan işlemi başlatır,
    bitince butonu tekrar aktif eder.

    Kullanım:
        self._btn_yukle = PrimaryButton("Yükle")
        ab = AsyncButton(
            btn=self._btn_yukle,
            fn=lambda: svc.listele(),
            on_done=self._goster,
            on_error=self._alert.goster,
        )
    """

    def __init__(self, btn, fn, on_done=None, on_error=None):
        self._btn    = btn
        self._fn     = fn
        self._on_done  = on_done
        self._on_error = on_error
        self._runner: AsyncRunner | None = None
        btn.clicked.connect(self._calistir)

    def _calistir(self):
        if self._runner and self._runner.isRunning():
            return
        self._btn.setEnabled(False)
        self._btn.setText("Yükleniyor…")
        self._runner = AsyncRunner(
            fn=self._fn,
            on_done=self._bitti,
            on_error=self._hata,
        )
        self._runner.start()

    def _bitti(self, sonuc):
        self._btn.setEnabled(True)
        self._btn.setText(self._btn.toolTip() or "Yükle")
        if self._on_done:
            self._on_done(sonuc)

    def _hata(self, mesaj: str):
        self._btn.setEnabled(True)
        self._btn.setText(self._btn.toolTip() or "Yükle")
        if self._on_error:
            self._on_error(mesaj)
