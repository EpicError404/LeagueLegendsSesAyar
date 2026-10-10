import sys
import types
import unittest
from unittest.mock import patch

from mixer_app.audio import AudioMixer
from mixer_app.config import AppConfig, MixerRule


class FakeProcess:
    def __init__(self, process_id, name):
        self.pid = process_id
        self.info = {"name": name}
        self._name = name

    def name(self):
        return self._name


class FakeVolume:
    def __init__(self, volume, mute):
        self.volume = volume
        self.mute = mute

    def GetMasterVolume(self):
        return self.volume

    def GetMute(self):
        return self.mute

    def SetMasterVolume(self, volume, _context):
        self.volume = volume

    def SetMute(self, mute, _context):
        self.mute = mute


class FakeSession:
    def __init__(self, process, volume):
        self.Process = process
        self.SimpleAudioVolume = volume

    def GetSessionInstanceIdentifier(self):
        return f"session-{self.Process.pid}"


class AudioMixerTests(unittest.TestCase):
    def setUp(self):
        self.trigger_process = FakeProcess(1, "LeagueClientUxRender.exe")
        self.target_process = FakeProcess(2, "Discord.exe")
        self.volume = FakeVolume(0.9, True)
        self.session = FakeSession(self.target_process, self.volume)
        self.processes = [self.trigger_process]

        comtypes = types.ModuleType("comtypes")
        comtypes.CoInitialize = lambda: None
        comtypes.CoUninitialize = lambda: None

        psutil = types.ModuleType("psutil")
        psutil.NoSuchProcess = type("NoSuchProcess", (Exception,), {})
        psutil.AccessDenied = type("AccessDenied", (Exception,), {})
        psutil.Error = Exception
        psutil.process_iter = lambda _attributes: iter(self.processes)

        pycaw = types.ModuleType("pycaw")
        pycaw.__path__ = []
        pycaw_api = types.ModuleType("pycaw.pycaw")

        class AudioUtilities:
            @staticmethod
            def GetAllSessions():
                return [self.session]

        pycaw_api.AudioUtilities = AudioUtilities
        self.modules = {
            "comtypes": comtypes,
            "psutil": psutil,
            "pycaw": pycaw,
            "pycaw.pycaw": pycaw_api,
        }
        self.module_patch = patch.dict(sys.modules, self.modules)
        self.module_patch.start()
        self.platform_patch = patch("mixer_app.audio.sys.platform", "win32")
        self.platform_patch.start()
        self.addCleanup(self.platform_patch.stop)
        self.addCleanup(self.module_patch.stop)
        self.logs = []
        self.mixer = AudioMixer(self.logs.append)
        self.addCleanup(self.mixer.close)
        self.config = AppConfig(
            enabled=True,
            trigger_processes=("LeagueClientUxRender.exe",),
            rules=[MixerRule("Discord.exe", 0.4, False)],
        )

    def test_restores_volume_and_mute_when_league_closes(self):
        self.mixer.tick(self.config)
        self.assertEqual((self.volume.volume, self.volume.mute), (0.4, False))

        self.processes.clear()
        self.mixer.tick(self.config)
        self.assertEqual((self.volume.volume, self.volume.mute), (0.9, True))
        self.assertTrue(any("geri yüklendi" in message for message in self.logs))

    def test_manual_volume_change_is_not_overridden_until_cooldown_expires(self):
        self.mixer.tick(self.config)
        self.volume.volume = 0.8

        with patch("mixer_app.audio.time.monotonic", side_effect=[10.0, 11.0, 13.0]):
            self.mixer.tick(self.config)
            self.assertEqual(self.volume.volume, 0.8)
            self.mixer.tick(self.config)
            self.assertEqual(self.volume.volume, 0.8)
            self.mixer.tick(self.config)
        self.assertEqual(self.volume.volume, 0.4)


if __name__ == "__main__":
    unittest.main()
