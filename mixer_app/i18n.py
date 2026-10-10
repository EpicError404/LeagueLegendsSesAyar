from __future__ import annotations

from typing import Any

SUPPORTED_LANGUAGES = ("tr", "en")
DEFAULT_LANGUAGE = "tr"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "tr": {
        "app_title": "LoL Otomatik Ses Mikseri — 3D Cyber HUD",
        "hud_top_badge": "⚡ LOL SES MİKSERİ // 3D HUD",
        "system_status_badge": "SİSTEM DURUMU",
        "status_waiting": "LoL bekleniyor",
        "status_waiting_dots": "LoL Bekleniyor...",
        "status_active": "Oyun Modu Aktif (Sesler Ayarlandı)",
        "status_disabled": "Oyun Modu Kapalı",
        "status_audio_init_error": "Ses denetimi başlatılamadı",
        "status_audio_error": "Ses Denetimi Hatası",
        "trigger_prefix": "Tetikleyici: ",
        "control_center_badge": "KONTROL MERKEZİ",
        "btn_mode_on": "● Oyun Modunu Kapat",
        "btn_mode_off": "○ Oyun Modunu Aç",
        "btn_add_app": "+ Uygulama Ekle",
        "btn_browse": "📁 Gözat (.exe)",
        "section_rules_title": "UYGULAMA SES KONTROL KARTLARI",
        "rules_count_singular": "{count} Kural",
        "rules_count_plural": "{count} Kural",
        "target_game_volume": "Hedef Oyun Sesi:",
        "dial_volume_sub": "SES",
        "percent_fmt": "%{percent}",
        "btn_remove": "✕ Kaldır",
        "tooltip_remove": "Bu ses kuralını sil",
        "btn_muted": "🔇 SESSİZ (MUTE)",
        "btn_sound_active": "🔊 SES AKTİF",
        "log_header": "İŞLEM GÜNLÜĞÜ / SİSTEM TELEMETRİSİ",
        "btn_clear": "Temizle",
        "tray_show": "Pencereyi göster",
        "tray_toggle": "Oyun modunu aç/kapat",
        "tray_quit": "Çıkış",
        "tray_tooltip": "LoL Otomatik Ses Mikseri",
        "dialog_add_title": "Uygulama Ekle",
        "dialog_add_prompt": "Uygulamanın süreç adı (.exe):",
        "dialog_browse_title": "Uygulama EXE Dosyası Seç",
        "dialog_browse_filter": "Uygulama dosyaları (*.exe)",
        "msg_invalid_process_title": "Geçersiz Süreç Adı",
        "msg_invalid_process_text": "Lütfen geçerli bir .exe adı girin.",
        "msg_already_exists_title": "Zaten Mevcut",
        "msg_already_exists_text": "{process} için zaten bir kural tanımlı.",
        "msg_save_error_title": "Ayarlar kaydedilemedi",
        "msg_audio_backend_title": "Ses denetimi kullanılamıyor",
        "msg_load_error_title": "Ayarlar yüklenemedi",
        "log_rule_removed": "Kural silindi: {process}",
        "log_rule_added": "Yeni kural eklendi: {process}",
        "log_tray_unavailable": "Sistem tepsisi kullanılamıyor; pencere kapatıldığında uygulama kapanacak.",
        "log_audio_error": "Ses denetimi hatası: {exc}",
        "log_lang_changed": "Dil değiştirildi: {lang_name}",
        "lang_switch_tooltip": "Dil Seçimi / Language Selection",
    },
    "en": {
        "app_title": "LoL Automatic Audio Mixer — 3D Cyber HUD",
        "hud_top_badge": "⚡ LOL AUDIO MIXER // 3D HUD",
        "system_status_badge": "SYSTEM STATUS",
        "status_waiting": "Waiting for LoL",
        "status_waiting_dots": "Waiting for LoL...",
        "status_active": "Game Mode Active (Audio Adjusted)",
        "status_disabled": "Game Mode Disabled",
        "status_audio_init_error": "Audio control could not be initialized",
        "status_audio_error": "Audio Control Error",
        "trigger_prefix": "Trigger: ",
        "control_center_badge": "CONTROL CENTER",
        "btn_mode_on": "● Disable Game Mode",
        "btn_mode_off": "○ Enable Game Mode",
        "btn_add_app": "+ Add App",
        "btn_browse": "📁 Browse (.exe)",
        "section_rules_title": "APPLICATION AUDIO CONTROL CARDS",
        "rules_count_singular": "{count} Rule",
        "rules_count_plural": "{count} Rules",
        "target_game_volume": "Target Game Volume:",
        "dial_volume_sub": "VOL",
        "percent_fmt": "{percent}%",
        "btn_remove": "✕ Remove",
        "tooltip_remove": "Delete this audio rule",
        "btn_muted": "🔇 MUTED",
        "btn_sound_active": "🔊 SOUND ACTIVE",
        "log_header": "ACTIVITY LOG / SYSTEM TELEMETRY",
        "btn_clear": "Clear",
        "tray_show": "Show window",
        "tray_toggle": "Toggle game mode",
        "tray_quit": "Quit",
        "tray_tooltip": "LoL Automatic Audio Mixer",
        "dialog_add_title": "Add Application",
        "dialog_add_prompt": "Application process name (.exe):",
        "dialog_browse_title": "Select Application EXE File",
        "dialog_browse_filter": "Application files (*.exe)",
        "msg_invalid_process_title": "Invalid Process Name",
        "msg_invalid_process_text": "Please enter a valid .exe name.",
        "msg_already_exists_title": "Already Exists",
        "msg_already_exists_text": "A rule is already defined for {process}.",
        "msg_save_error_title": "Could not save settings",
        "msg_audio_backend_title": "Audio control unavailable",
        "msg_load_error_title": "Failed to load settings",
        "log_rule_removed": "Rule removed: {process}",
        "log_rule_added": "New rule added: {process}",
        "log_tray_unavailable": "System tray unavailable; window close will terminate the app.",
        "log_audio_error": "Audio control error: {exc}",
        "log_lang_changed": "Language changed: {lang_name}",
        "lang_switch_tooltip": "Language Selection / Dil Seçimi",
    },
}


def t(key: str, lang: str = "tr", **kwargs: Any) -> str:
    """Return the translated string for the given key and language."""
    normalized_lang = lang.lower() if isinstance(lang, str) else DEFAULT_LANGUAGE
    lang_dict = TRANSLATIONS.get(normalized_lang, TRANSLATIONS[DEFAULT_LANGUAGE])
    text = lang_dict.get(key)
    if text is None:
        text = TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


def rules_count_text(count: int, lang: str = "tr") -> str:
    key = "rules_count_singular" if count == 1 else "rules_count_plural"
    return t(key, lang, count=count)
