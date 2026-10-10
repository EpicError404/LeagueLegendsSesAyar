from __future__ import annotations

import ctypes
from pathlib import Path
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from mixer_app.config import ConfigError, get_config_path, load_config
from mixer_app.ui import MixerWindow


def main() -> int:
    # Set Windows AppUserModelID so taskbar groups and shows custom icon properly
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("LoLAutomaticAudioMixer.App")
    except Exception:
        pass

    application = QApplication(sys.argv)
    application.setApplicationName("LoLAutomaticAudioMixer")
    application.setQuitOnLastWindowClosed(False)

    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    icon_path = base_dir / "mixer_app" / "resources" / "icon.png"
    if icon_path.exists():
        application.setWindowIcon(QIcon(str(icon_path)))

    config_path = get_config_path()
    try:
        config = load_config(config_path)
    except ConfigError as exc:
        QMessageBox.critical(None, "Ayarlar yüklenemedi", str(exc))
        return 1

    window = MixerWindow(config, config_path)
    application.aboutToQuit.connect(window.close_application)
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
