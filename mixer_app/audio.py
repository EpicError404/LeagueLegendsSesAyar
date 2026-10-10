from __future__ import annotations

import logging
import sys
import time
from dataclasses import dataclass
from typing import Callable

from .config import AppConfig, MixerRule


LOGGER = logging.getLogger(__name__)


class AudioBackendError(RuntimeError):
    """Raised when the Windows audio backend cannot be initialized."""


@dataclass
class ManagedSession:
    volume_interface: object
    process_name: str
    original_volume: float
    original_mute: bool
    expected_volume: float
    expected_mute: bool
    override_until: float = 0.0


class AudioMixer:
    def __init__(self, log: Callable[[str], None]) -> None:
        if sys.platform != "win32":
            raise AudioBackendError("Otomatik ses kontrolü yalnızca Windows'ta kullanılabilir.")
        try:
            import comtypes
            import psutil
            from pycaw.pycaw import AudioUtilities
        except ImportError as exc:
            raise AudioBackendError(
                "Ses bileşenleri bulunamadı. `pip install -r requirements.txt` komutunu çalıştırın."
            ) from exc

        self._comtypes = comtypes
        self._psutil = psutil
        self._audio_utilities = AudioUtilities
        self._log = log
        self._managed: dict[str, ManagedSession] = {}
        self._was_active = False
        try:
            self._comtypes.CoInitialize()
        except Exception as exc:
            raise AudioBackendError(f"Windows ses arabirimi başlatılamadı: {exc}") from exc

    @staticmethod
    def _key(session: object, process_id: int) -> str:
        try:
            return str(session.GetSessionInstanceIdentifier())
        except Exception:
            try:
                return f"pid:{process_id}:session:{session.GetSessionIdentifier()}"
            except Exception:
                return f"pid:{process_id}"

    def _trigger_running(self, config: AppConfig) -> bool | None:
        trigger_names = {name.casefold() for name in config.trigger_processes}
        try:
            for process in self._psutil.process_iter(["name"]):
                try:
                    name = process.info.get("name")
                    if name and name.casefold() in trigger_names:
                        return True
                except (self._psutil.NoSuchProcess, self._psutil.AccessDenied):
                    continue
        except self._psutil.Error as exc:
            self._log(f"Uygulama süreçleri taranamadı: {exc}")
            return None
        return False

    def _sessions(self) -> list[tuple[str, str, object]] | None:
        found: list[tuple[str, str, object]] = []
        process_names: dict[int, str] = {}
        try:
            sessions = self._audio_utilities.GetAllSessions()
        except Exception as exc:
            self._log(f"Windows ses oturumları okunamadı: {exc}")
            return None

        for session in sessions:
            try:
                process = session.Process
                if process is None:
                    continue
                process_id = int(process.pid)
                name = process_names.get(process_id)
                if name is None:
                    name = process.name()
                    process_names[process_id] = name
                volume_interface = session.SimpleAudioVolume
                found.append((self._key(session, process_id), name, volume_interface))
            except (self._psutil.NoSuchProcess, self._psutil.AccessDenied):
                continue
            except Exception as exc:
                self._log(f"Bir ses oturumu okunamadı: {exc}")
        return found

    @staticmethod
    def _read_state(volume_interface: object) -> tuple[float, bool]:
        volume = float(volume_interface.GetMasterVolume())
        mute = bool(volume_interface.GetMute())
        return volume, mute

    def _refresh_expected(self, managed: ManagedSession) -> None:
        try:
            managed.expected_volume, managed.expected_mute = self._read_state(
                managed.volume_interface
            )
        except Exception as exc:
            self._log(f"{managed.process_name} güncel ses durumu okunamadı: {exc}")

    def _write_state(
        self,
        volume_interface: object,
        volume: float,
        mute: bool,
        process_name: str,
    ) -> bool:
        try:
            volume_interface.SetMasterVolume(float(volume), None)
            volume_interface.SetMute(bool(mute), None)
        except Exception as exc:
            self._log(f"{process_name} ses ayarı uygulanamadı: {exc}")
            return False
        return True

    def _restore(self) -> None:
        for session in self._managed.values():
            try:
                self._write_state(
                    session.volume_interface,
                    session.original_volume,
                    session.original_mute,
                    session.process_name,
                )
            except Exception as exc:
                self._log(f"Önceki ses seviyesi geri yüklenemedi: {exc}")
        self._managed.clear()

    def _apply_rule(self, key: str, process_name: str, volume_interface: object, rule: MixerRule) -> None:
        managed = self._managed.get(key)
        if managed is None:
            try:
                original_volume, original_mute = self._read_state(volume_interface)
            except Exception as exc:
                self._log(f"{process_name} başlangıç ses seviyesi okunamadı: {exc}")
                return
            managed = ManagedSession(
                volume_interface=volume_interface,
                process_name=process_name,
                original_volume=original_volume,
                original_mute=original_mute,
                expected_volume=original_volume,
                expected_mute=original_mute,
            )
            self._managed[key] = managed
            if self._write_state(volume_interface, rule.volume, rule.mute, process_name):
                managed.expected_volume = rule.volume
                managed.expected_mute = rule.mute
                self._log(f"{process_name}: oyun modu ses seviyesi %{round(rule.volume * 100)}")
            else:
                self._refresh_expected(managed)
            return

        try:
            current_volume, current_mute = self._read_state(volume_interface)
        except Exception as exc:
            self._log(f"{process_name} ses seviyesi okunamadı: {exc}")
            return

        changed_by_user = (
            abs(current_volume - managed.expected_volume) > 0.015
            or current_mute != managed.expected_mute
        )
        target_changed = (
            abs(rule.volume - managed.expected_volume) > 0.001
            or rule.mute != managed.expected_mute
        )
        now = time.monotonic()
        if changed_by_user:
            if not managed.override_until:
                managed.override_until = now + 2.0
                self._log(f"{process_name}: elle yapılan ses değişikliği için 2 saniye bekleniyor")
                return
            if now < managed.override_until:
                return
        else:
            managed.override_until = 0.0
        if not changed_by_user and not target_changed:
            return

        if self._write_state(volume_interface, rule.volume, rule.mute, process_name):
            managed.expected_volume = rule.volume
            managed.expected_mute = rule.mute
            managed.override_until = 0.0
        else:
            self._refresh_expected(managed)

    def tick(self, config: AppConfig) -> bool:
        running = self._trigger_running(config) if config.enabled else False
        if running is None:
            return self._was_active
        active = config.enabled and running
        if not active:
            if self._was_active:
                self._restore()
                self._log("Oyun modu kapandı; önceki ses seviyeleri geri yüklendi")
            self._was_active = False
            return False

        if not self._was_active:
            self._log("Oyun modu etkin")
        self._was_active = True
        rules = {rule.process.casefold(): rule for rule in config.rules}
        sessions = self._sessions()
        if sessions is None:
            return True
        current_sessions = {key: interface for key, _, interface in sessions}

        for key, managed in list(self._managed.items()):
            if key not in current_sessions:
                self._managed.pop(key, None)

        for key, process_name, volume_interface in sessions:
            rule = rules.get(process_name.casefold())
            if rule is None:
                if key in self._managed:
                    managed = self._managed.pop(key)
                    self._write_state(
                        volume_interface,
                        managed.original_volume,
                        managed.original_mute,
                        process_name,
                    )
                    self._log(f"{process_name}: kural kaldırıldı; önceki ses geri yüklendi")
                continue
            self._apply_rule(key, process_name, volume_interface, rule)
        return True

    def close(self) -> None:
        self._restore()
        try:
            self._comtypes.CoUninitialize()
        except Exception as exc:
            LOGGER.warning("COM kapatılırken hata oluştu: %s", exc)
