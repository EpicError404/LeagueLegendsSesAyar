from __future__ import annotations

import unittest

from mixer_app.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, rules_count_text, t


class I18nTests(unittest.TestCase):
    def test_supported_languages(self) -> None:
        self.assertIn("tr", SUPPORTED_LANGUAGES)
        self.assertIn("en", SUPPORTED_LANGUAGES)
        self.assertEqual(DEFAULT_LANGUAGE, "tr")

    def test_translations_tr_and_en(self) -> None:
        self.assertEqual(t("status_waiting", "tr"), "LoL bekleniyor")
        self.assertEqual(t("status_waiting", "en"), "Waiting for LoL")

        self.assertEqual(t("target_game_volume", "tr"), "Hedef Oyun Sesi:")
        self.assertEqual(t("target_game_volume", "en"), "Target Game Volume:")

        self.assertEqual(t("btn_add_app", "tr"), "+ Uygulama Ekle")
        self.assertEqual(t("btn_add_app", "en"), "+ Add App")

    def test_rules_count_formatting(self) -> None:
        self.assertEqual(rules_count_text(1, "tr"), "1 Kural")
        self.assertEqual(rules_count_text(2, "tr"), "2 Kural")
        self.assertEqual(rules_count_text(1, "en"), "1 Rule")
        self.assertEqual(rules_count_text(3, "en"), "3 Rules")

    def test_fallback_on_unsupported_language(self) -> None:
        self.assertEqual(t("status_waiting", "es"), "LoL bekleniyor")

    def test_fallback_on_missing_key(self) -> None:
        self.assertEqual(t("non_existent_key", "tr"), "non_existent_key")


if __name__ == "__main__":
    unittest.main()
