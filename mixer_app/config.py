from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_TRIGGER_PROCESSES = (
    "League of Legends.exe",
    "LeagueClientUxRender.exe",
)


@dataclass
class MixerRule:
    process: str
    volume: float
    mute: bool = False


@dataclass
class AppConfig:
    enabled: bool
    trigger_processes: tuple[str, ...]
    rules: list[MixerRule]
    language: str = "tr"


class ConfigError(ValueError):
    """Raised when the settings file cannot be parsed or validated."""


def default_config() -> AppConfig:
    return AppConfig(
        enabled=True,
        trigger_processes=DEFAULT_TRIGGER_PROCESSES,
        rules=[
            MixerRule(process="Discord.exe", volume=0.65),
            MixerRule(process="Spotify.exe", volume=0.35),
        ],
        language="tr",
    )


def get_config_path() -> Path:
    app_data = os.environ.get("APPDATA")
    if app_data:
        return Path(app_data) / "LoLAutomaticAudioMixer" / "settings.json"
    return Path.home() / ".config" / "LoLAutomaticAudioMixer" / "settings.json"


def _validate_process(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or not value.strip().lower().endswith(".exe"):
        raise ConfigError(f"{field} geçerli bir .exe adı olmalıdır.")
    return Path(value.strip()).name


def config_from_dict(data: Any) -> AppConfig:
    if not isinstance(data, dict):
        raise ConfigError("Ayar dosyasının kökü bir JSON nesnesi olmalıdır.")

    enabled = data.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ConfigError("'enabled' alanı true veya false olmalıdır.")

    language = data.get("language", "tr")
    if not isinstance(language, str) or language.strip().lower() not in ("tr", "en"):
        language = "tr"
    else:
        language = language.strip().lower()

    raw_triggers = data.get("trigger_processes", list(DEFAULT_TRIGGER_PROCESSES))
    if not isinstance(raw_triggers, list) or not raw_triggers:
        raise ConfigError("'trigger_processes' boş olmayan bir liste olmalıdır.")
    triggers = tuple(_validate_process(name, "Tetikleyici") for name in raw_triggers)

    raw_rules = data.get("rules")
    if not isinstance(raw_rules, list):
        raise ConfigError("'rules' bir liste olmalıdır.")

    rules: list[MixerRule] = []
    seen_processes: set[str] = set()
    for index, raw_rule in enumerate(raw_rules):
        if not isinstance(raw_rule, dict):
            raise ConfigError(f"{index + 1}. ses kuralı bir JSON nesnesi olmalıdır.")
        process = _validate_process(raw_rule.get("process"), f"{index + 1}. kural process")
        if process.casefold() in seen_processes:
            raise ConfigError(f"{process} için birden fazla ses kuralı tanımlanamaz.")
        seen_processes.add(process.casefold())

        volume = raw_rule.get("volume")
        if isinstance(volume, bool) or not isinstance(volume, (int, float)) or not 0 <= volume <= 1:
            raise ConfigError(f"{process} ses seviyesi 0.0 ile 1.0 arasında olmalıdır.")
        mute = raw_rule.get("mute", False)
        if not isinstance(mute, bool):
            raise ConfigError(f"{process} için 'mute' alanı true veya false olmalıdır.")
        rules.append(MixerRule(process=process, volume=float(volume), mute=mute))

    return AppConfig(enabled=enabled, trigger_processes=triggers, rules=rules, language=language)


def load_config(path: Path) -> AppConfig:
    if not path.exists():
        return default_config()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"Ayar dosyası okunamadı: {exc}") from exc
    return config_from_dict(data)


def save_config(path: Path, config: AppConfig) -> None:
    data = {
        "enabled": config.enabled,
        "language": getattr(config, "language", "tr"),
        "trigger_processes": list(config.trigger_processes),
        "rules": [
            {"process": rule.process, "volume": rule.volume, "mute": rule.mute}
            for rule in config.rules
        ],
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = path.with_suffix(path.suffix + ".tmp")
        temporary_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        temporary_path.replace(path)
    except OSError as exc:
        raise ConfigError(f"Ayarlar kaydedilemedi: {exc}") from exc

