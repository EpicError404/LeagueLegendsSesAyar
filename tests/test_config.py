import json
import tempfile
import unittest
from pathlib import Path

from mixer_app.config import (
    ConfigError,
    config_from_dict,
    default_config,
    load_config,
    save_config,
)


class ConfigTests(unittest.TestCase):
    def test_defaults_include_league_triggers_and_mix_rules(self) -> None:
        config = default_config()
        self.assertIn("League of Legends.exe", config.trigger_processes)
        self.assertIn("LeagueClientUxRender.exe", config.trigger_processes)
        self.assertEqual([rule.process for rule in config.rules], ["Discord.exe", "Spotify.exe"])

    def test_round_trip_json_settings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            config = default_config()
            save_config(path, config)
            loaded = load_config(path)
        self.assertEqual(loaded.enabled, config.enabled)
        self.assertEqual(loaded.trigger_processes, config.trigger_processes)
        self.assertEqual(
            [(rule.process, rule.volume, rule.mute) for rule in loaded.rules],
            [(rule.process, rule.volume, rule.mute) for rule in config.rules],
        )

    def test_rejects_out_of_range_volume(self) -> None:
        data = {
            "enabled": True,
            "trigger_processes": ["LeagueClientUxRender.exe"],
            "rules": [{"process": "Discord.exe", "volume": 1.1, "mute": False}],
        }
        with self.assertRaises(ConfigError):
            config_from_dict(data)

    def test_rejects_duplicate_process_rules(self) -> None:
        data = {
            "enabled": True,
            "trigger_processes": ["LeagueClientUxRender.exe"],
            "rules": [
                {"process": "Discord.exe", "volume": 0.5},
                {"process": "discord.EXE", "volume": 0.7},
            ],
        }
        with self.assertRaises(ConfigError):
            config_from_dict(data)

    def test_reports_invalid_json_instead_of_silently_resetting(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(path)

    def test_language_defaults_to_tr_and_persists_en(self) -> None:
        config = default_config()
        self.assertEqual(config.language, "tr")

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            config.language = "en"
            save_config(path, config)
            loaded = load_config(path)
            self.assertEqual(loaded.language, "en")

    def test_language_fallback_when_invalid_or_missing(self) -> None:
        data_missing = {
            "enabled": True,
            "trigger_processes": ["LeagueClientUxRender.exe"],
            "rules": [],
        }
        cfg1 = config_from_dict(data_missing)
        self.assertEqual(cfg1.language, "tr")

        data_invalid = {
            "enabled": True,
            "trigger_processes": ["LeagueClientUxRender.exe"],
            "rules": [],
            "language": "fr",
        }
        cfg2 = config_from_dict(data_invalid)
        self.assertEqual(cfg2.language, "tr")


if __name__ == "__main__":
    unittest.main()
