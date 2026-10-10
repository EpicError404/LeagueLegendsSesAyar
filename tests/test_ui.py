from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ["QT_QPA_PLATFORM"] = "offscreen"

try:
    from PySide6.QtWidgets import QApplication
    from mixer_app.ui import AppAudioCard, MixerWindow
    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False

from mixer_app.config import AppConfig, MixerRule


@unittest.skipUnless(HAS_PYSIDE6, "PySide6 is required for UI tests")
class UITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not HAS_PYSIDE6:
            return
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "settings.json"
        self.config = AppConfig(
            enabled=True,
            trigger_processes=("LeagueClientUxRender.exe",),
            rules=[MixerRule(process="Discord.exe", volume=0.5, mute=False)],
            language="tr",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @patch("mixer_app.ui.AudioMixer")
    def test_window_initializes_with_turkish_and_language_buttons(self, mock_audio_mixer) -> None:
        mock_mixer_instance = mock_audio_mixer.return_value
        mock_mixer_instance.tick.return_value = False

        window = MixerWindow(self.config, self.config_path)
        try:
            self.assertEqual(window.current_language, "tr")
            self.assertIn("LoL Otomatik Ses Mikseri", window.windowTitle())
            self.assertEqual(window.status_badge.text(), "SİSTEM DURUMU")
            self.assertEqual(window.ctrl_badge.text(), "KONTROL MERKEZİ")
            self.assertEqual(window.add_btn.text(), "+ Uygulama Ekle")
            self.assertEqual(window.browse_btn.text(), "📁 Gözat (.exe)")
            self.assertEqual(window.section_title.text(), "UYGULAMA SES KONTROL KARTLARI")
            self.assertEqual(window.rules_count_badge.text(), "1 Kural")

            # Check card widgets in Turkish
            card = window.cards_layout.itemAt(0).widget()
            self.assertIsInstance(card, AppAudioCard)
            self.assertEqual(card.vol_title.text(), "Hedef Oyun Sesi:")
            self.assertEqual(card.remove_btn.text(), "✕ Kaldır")
            self.assertEqual(card.dial.sub_label, "SES")

            # Now switch language to English
            window.set_language("en")
            self.assertEqual(window.current_language, "en")
            self.assertEqual(window.config.language, "en")
            self.assertIn("LoL Automatic Audio Mixer", window.windowTitle())
            self.assertEqual(window.status_badge.text(), "SYSTEM STATUS")
            self.assertEqual(window.ctrl_badge.text(), "CONTROL CENTER")
            self.assertEqual(window.add_btn.text(), "+ Add App")
            self.assertEqual(window.browse_btn.text(), "📁 Browse (.exe)")
            self.assertEqual(window.section_title.text(), "APPLICATION AUDIO CONTROL CARDS")
            self.assertEqual(window.rules_count_badge.text(), "1 Rule")

            # Check card widgets updated to English
            self.assertEqual(card.vol_title.text(), "Target Game Volume:")
            self.assertEqual(card.remove_btn.text(), "✕ Remove")
            self.assertEqual(card.dial.sub_label, "VOL")

            # Switch back to Turkish via button click simulation
            window.btn_lang_tr.click()
            self.assertEqual(window.current_language, "tr")
            self.assertEqual(card.vol_title.text(), "Hedef Oyun Sesi:")
            self.assertEqual(card.dial.sub_label, "SES")
        finally:
            window.close_application()


if __name__ == "__main__":
    unittest.main()
