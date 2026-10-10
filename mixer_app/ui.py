from __future__ import annotations

from datetime import datetime
from pathlib import Path
import math

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QCursor,
    QFont,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QStyle,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from .audio import AudioBackendError, AudioMixer
from .config import AppConfig, ConfigError, MixerRule, save_config
from .i18n import rules_count_text, t


# ============================================================================
# 3D CYBERPUNK HUD STYLESHEET
# ============================================================================
CYBER_STYLESHEET = """
QMainWindow {
    background-color: #070914;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
}

QWidget#CentralWidget {
    background: transparent;
}

QScrollArea {
    background: transparent;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background: transparent;
}

/* Custom 3D Cyber ScrollBar */
QScrollBar:vertical {
    border: none;
    background: rgba(13, 17, 36, 0.6);
    width: 6px;
    margin: 8px 0px 8px 0px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00f0ff, stop:1 #bd34fe);
    min-height: 30px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #00f0ff;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

/* 3D Tactile Buttons */
QPushButton.cyber-btn-cyan {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a2c52, stop:1 #0c1630);
    color: #00f0ff;
    border: 1px solid #00f0ff;
    border-top: 1px solid #7df8ff;
    border-bottom: 3px solid #004d61;
    border-radius: 8px;
    padding: 7px 14px;
    font-weight: bold;
    font-size: 12px;
}
QPushButton.cyber-btn-cyan:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #253f77, stop:1 #112248);
    border-color: #55fbfb;
    color: #ffffff;
}
QPushButton.cyber-btn-cyan:pressed {
    background: #091024;
    border-bottom: 1px solid #00f0ff;
    padding-top: 9px;
    padding-bottom: 5px;
}

QPushButton.cyber-btn-mode-on {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff2a85, stop:0.5 #d946ef, stop:1 #8b5cf6);
    color: #ffffff;
    border: 1px solid #ff77b5;
    border-top: 1px solid #ffa3cf;
    border-bottom: 3px solid #6b0c36;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 13px;
    letter-spacing: 0.5px;
}
QPushButton.cyber-btn-mode-on:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff4d9d, stop:0.5 #e261f4, stop:1 #9d74f8);
    border-color: #ffffff;
}
QPushButton.cyber-btn-mode-on:pressed {
    border-bottom: 1px solid #ff77b5;
    padding-top: 10px;
    padding-bottom: 6px;
}

QPushButton.cyber-btn-mode-off {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00b4d8, stop:0.5 #0077b6, stop:1 #023e8a);
    color: #ffffff;
    border: 1px solid #00f0ff;
    border-top: 1px solid #90e0ef;
    border-bottom: 3px solid #03045e;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 13px;
    letter-spacing: 0.5px;
}
QPushButton.cyber-btn-mode-off:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #48cae4, stop:0.5 #0096c7, stop:1 #0077b6);
    border-color: #caf0f8;
}
QPushButton.cyber-btn-mode-off:pressed {
    border-bottom: 1px solid #00f0ff;
    padding-top: 10px;
    padding-bottom: 6px;
}

QPushButton.cyber-btn-danger {
    background: rgba(45, 12, 24, 0.7);
    color: #ff4d6d;
    border: 1px solid rgba(255, 77, 109, 0.4);
    border-bottom: 2px solid #590d22;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
}
QPushButton.cyber-btn-danger:hover {
    background: #590d22;
    color: #ffffff;
    border-color: #ff4d6d;
}
QPushButton.cyber-btn-danger:pressed {
    border-bottom: 1px solid #ff4d6d;
    padding-top: 5px;
    padding-bottom: 3px;
}

/* 3D Neon Slider */
QSlider::groove:horizontal {
    border: 1px solid rgba(0, 240, 255, 0.25);
    height: 8px;
    background: #090e22;
    margin: 2px 0;
    border-radius: 4px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f0ff, stop:0.6 #bd34fe, stop:1 #ff2a85);
    border: 1px solid rgba(0, 240, 255, 0.4);
    height: 8px;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:0.4 #00f0ff, stop:1 #06406e);
    border: 2px solid #ffffff;
    width: 18px;
    margin-top: -6px;
    margin-bottom: -6px;
    border-radius: 9px;
}
QSlider::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:0.3 #ff2a85, stop:1 #700636);
    border: 2px solid #ffffff;
}

/* Terminal / Log Styling */
QPlainTextEdit.cyber-log {
    background: #050711;
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
    padding: 6px;
    selection-background-color: #0369a1;
}
"""


# ============================================================================
# CUSTOM 3D / CYBER WIDGETS
# ============================================================================
class CyberCard(QFrame):
    """A floating 3D card container with neon glowing drop-shadow, inner highlights, and bevel."""

    def __init__(self, glow_color: QColor, border_color: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.glow_color = glow_color
        self.border_color = border_color
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        self.setStyleSheet(f"""
            CyberCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(19, 25, 52, 0.95),
                    stop:0.4 rgba(12, 16, 35, 0.93),
                    stop:1 rgba(21, 28, 58, 0.95));
                border: 1.5px solid {self.border_color};
                border-top: 1.5px solid {self._brighten_color(self.border_color)};
                border-bottom: 3px solid rgba(0, 0, 0, 0.85);
                border-radius: 14px;
            }}
        """)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(24)
        self.shadow.setColor(self.glow_color)
        self.shadow.setOffset(0, 6)
        self.setGraphicsEffect(self.shadow)

    def _brighten_color(self, hex_color: str) -> str:
        color = QColor(hex_color)
        return color.lighter(135).name()

    def enterEvent(self, event: object) -> None:
        super().enterEvent(event)
        self.shadow.setBlurRadius(36)
        self.shadow.setOffset(0, 8)

    def leaveEvent(self, event: object) -> None:
        super().leaveEvent(event)
        self.shadow.setBlurRadius(24)
        self.shadow.setOffset(0, 6)


class CyberDialWidget(QWidget):
    """
    3D Glowing Circular Dial inspired by the neon holographic gauge
    in the user reference image (+71.21%, +34.20%, etc.).
    """

    valueChanged = Signal(int)

    def __init__(
        self,
        volume: float = 0.5,
        muted: bool = False,
        accent_color: QColor | None = None,
        sub_label: str = "SES",
        percent_fmt: str = "%{percent}",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._volume = max(0.0, min(1.0, volume))
        self._muted = muted
        self.accent_color = accent_color or QColor("#00f0ff")
        self.sub_label = sub_label
        self.percent_fmt = percent_fmt
        self.setFixedSize(88, 88)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        self._volume = max(0.0, min(1.0, value))
        self.update()

    @property
    def muted(self) -> bool:
        return self._muted

    @muted.setter
    def muted(self, value: bool) -> None:
        self._muted = value
        self.update()

    def paintEvent(self, event: object) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        center = QPointF(w / 2.0, h / 2.0)
        radius = min(w, h) / 2.0 - 8

        # 1. Subtle Outer Dots / Ticks (precision cyber dial)
        painter.setPen(QPen(QColor(255, 255, 255, 30), 1))
        for angle_deg in range(0, 360, 30):
            rad = math.radians(angle_deg)
            dot_x = center.x() + math.cos(rad) * (radius + 4)
            dot_y = center.y() + math.sin(rad) * (radius + 4)
            painter.drawPoint(QPointF(dot_x, dot_y))

        # 2. Background dark ring
        bg_pen = QPen(QColor(16, 22, 45, 220), 7)
        bg_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2), -45 * 16, 270 * 16)

        # 3. Glowing Arc
        arc_angle = int(270 * self._volume)
        if not self._muted:
            grad = QLinearGradient(0, h, w, 0)
            grad.setColorAt(0.0, QColor("#00f0ff"))
            grad.setColorAt(0.5, QColor("#bd34fe"))
            grad.setColorAt(1.0, QColor("#ff2a85"))

            arc_pen = QPen(QBrush(grad), 7)
            arc_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(arc_pen)
            painter.drawArc(QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2), 225 * 16, -arc_angle * 16)

            # Center 3D indicator disc
            inner_radius = radius - 8
            inner_grad = QLinearGradient(0, center.y() - inner_radius, 0, center.y() + inner_radius)
            inner_grad.setColorAt(0.0, QColor(26, 35, 72, 230))
            inner_grad.setColorAt(1.0, QColor(10, 14, 28, 250))
            painter.setPen(QPen(QColor(0, 240, 255, 70), 1))
            painter.setBrush(QBrush(inner_grad))
            painter.drawEllipse(center, inner_radius, inner_radius)

            # Volume text in center
            painter.setPen(QColor("#ffffff"))
            font = QFont("Segoe UI", 11, QFont.Weight.Bold)
            painter.setFont(font)
            percent_val = round(self._volume * 100)
            try:
                percent_str = self.percent_fmt.format(percent=percent_val)
            except Exception:
                percent_str = f"%{percent_val}"
            painter.drawText(QRectF(0, center.y() - 14, w, 20), Qt.AlignmentFlag.AlignCenter, percent_str)

            # Sub-label
            painter.setPen(QColor(0, 240, 255, 180))
            font_sub = QFont("Segoe UI", 7, QFont.Weight.Bold)
            painter.setFont(font_sub)
            painter.drawText(QRectF(0, center.y() + 6, w, 14), Qt.AlignmentFlag.AlignCenter, self.sub_label)
        else:
            mute_pen = QPen(QColor(255, 42, 133, 160), 7)
            mute_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(mute_pen)
            painter.drawArc(QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2), 225 * 16, -arc_angle * 16)

            inner_radius = radius - 8
            painter.setPen(QPen(QColor(255, 42, 133, 50), 1))
            painter.setBrush(QBrush(QColor(25, 8, 18, 230)))
            painter.drawEllipse(center, inner_radius, inner_radius)

            painter.setPen(QColor("#ff2a85"))
            font = QFont("Segoe UI", 9, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, "MUTE")

    def wheelEvent(self, event: object) -> None:
        delta = event.angleDelta().y()
        step = 0.05 if delta > 0 else -0.05
        new_vol = max(0.0, min(1.0, self._volume + step))
        self.volume = new_vol
        self.valueChanged.emit(round(new_vol * 100))


class CyberRadarWidget(QWidget):
    """
    3D Animated Glowing Cyber Orb / Radar showing live game detection
    (Inspired by the cyan/magenta holographic orb in the image).
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(54, 54)
        self._pulse_phase = 0.0
        self._status_mode = "waiting"

        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(40)
        self._anim_timer.timeout.connect(self._animate)
        self._anim_timer.start()

    def set_status(self, mode: str) -> None:
        if self._status_mode != mode:
            self._status_mode = mode
            self.update()

    def _animate(self) -> None:
        self._pulse_phase = (self._pulse_phase + 0.08) % (2 * math.pi)
        self.update()

    def paintEvent(self, event: object) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        center = QPointF(w / 2.0, h / 2.0)

        pulse = (math.sin(self._pulse_phase) + 1.0) / 2.0  # 0.0 to 1.0

        if self._status_mode == "active":
            primary_color = QColor(0, 245, 160)  # Neon Emerald
            secondary_color = QColor(0, 240, 255)  # Cyan
        elif self._status_mode == "disabled":
            primary_color = QColor(255, 120, 50)  # Amber
            secondary_color = QColor(100, 100, 120)
        else:
            primary_color = QColor(0, 240, 255)  # Neon Cyan
            secondary_color = QColor(189, 52, 254)  # Magenta/Purple

        # 1. Outer pulse aura
        aura_radius = 18 + pulse * 6
        aura_pen = QPen(QColor(primary_color.red(), primary_color.green(), primary_color.blue(), int(35 + pulse * 75)), 1.5)
        painter.setPen(aura_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, aura_radius, aura_radius)

        # 2. Middle radar ring
        ring_pen = QPen(QColor(secondary_color.red(), secondary_color.green(), secondary_color.blue(), 140), 1.5)
        painter.setPen(ring_pen)
        painter.drawEllipse(center, 15, 15)

        # 3. Rotating radar sweep line
        if self._status_mode != "disabled":
            angle = self._pulse_phase * 2
            sweep_x = center.x() + math.cos(angle) * 14
            sweep_y = center.y() + math.sin(angle) * 14
            painter.setPen(QPen(QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 200), 2))
            painter.drawLine(center, QPointF(sweep_x, sweep_y))

        # 4. Glowing Core Orb
        core_grad = QLinearGradient(center.x() - 9, center.y() - 9, center.x() + 9, center.y() + 9)
        core_grad.setColorAt(0.0, QColor(255, 255, 255, 240))
        core_grad.setColorAt(0.5, primary_color)
        core_grad.setColorAt(1.0, secondary_color)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(core_grad))
        painter.drawEllipse(center, 7 + pulse * 1.5, 7 + pulse * 1.5)


# ============================================================================
# 3D APPLICATION AUDIO CARD WIDGET
# ============================================================================
class AppAudioCard(CyberCard):
    """An individual 3D floating cybernetic card for controlling an application's volume."""

    def __init__(self, rule: MixerRule, index: int, window: MixerWindow, parent: QWidget | None = None) -> None:
        accent_color = QColor(255, 42, 133, 95) if index % 2 == 1 else QColor(0, 240, 255, 95)
        border_color = "#ff2a85" if index % 2 == 1 else "#00f0ff"
        super().__init__(accent_color, border_color, parent)

        self.rule = rule
        self.index = index
        self.window = window

        self._build_card()

    def _build_card(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(12)

        # 1. Top row: Process name badge + Remove button
        top_row = QHBoxLayout()

        icon_name = "🎵" if "spotify" in self.rule.process.lower() else ("🎮" if "discord" in self.rule.process.lower() else "🔊")
        title_label = QLabel(f"{icon_name}  {self.rule.process}")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-weight: bold;
                font-size: 14px;
                letter-spacing: 0.5px;
            }
        """)
        top_row.addWidget(title_label, 1)

        # 3D Remove button
        lang = self.window.current_language
        self.remove_btn = QPushButton(t("btn_remove", lang))
        self.remove_btn.setProperty("class", "cyber-btn-danger")
        self.remove_btn.setToolTip(t("tooltip_remove", lang))
        self.remove_btn.clicked.connect(lambda: self.window.remove_card_rule(self.index))
        top_row.addWidget(self.remove_btn)
        layout.addLayout(top_row)

        # 2. Middle Row: 3D Dial + Slider Section
        mid_row = QHBoxLayout()
        mid_row.setSpacing(16)

        # Circular 3D Dial
        self.dial = CyberDialWidget(
            volume=self.rule.volume,
            muted=self.rule.mute,
            accent_color=QColor(self.border_color),
            sub_label=t("dial_volume_sub", lang),
            percent_fmt=t("percent_fmt", lang, percent="{percent}"),
            parent=self,
        )
        self.dial.valueChanged.connect(self._on_dial_changed)
        mid_row.addWidget(self.dial)

        # Controls column (Slider + Percentage + Mute)
        controls_col = QVBoxLayout()
        controls_col.setSpacing(8)

        # Volume header with numerical indicator
        vol_info = QHBoxLayout()
        self.vol_title = QLabel(t("target_game_volume", lang))
        self.vol_title.setStyleSheet("color: #94a3b8; font-size: 11px; font-weight: 600;")
        self.vol_value_label = QLabel(t("percent_fmt", lang, percent=round(self.rule.volume * 100)))
        self.vol_value_label.setStyleSheet(f"color: {self.border_color}; font-weight: bold; font-size: 14px;")
        vol_info.addWidget(self.vol_title)
        vol_info.addStretch()
        vol_info.addWidget(self.vol_value_label)
        controls_col.addLayout(vol_info)

        # 3D Slider
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(0, 100)
        self.slider.setValue(round(self.rule.volume * 100))
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.slider.sliderReleased.connect(self.window.save_settings)
        controls_col.addWidget(self.slider)

        # 3D Mute Toggle Button
        self.mute_btn = QPushButton()
        self.mute_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._update_mute_btn_style()
        self.mute_btn.clicked.connect(self._toggle_mute)
        controls_col.addWidget(self.mute_btn)

        mid_row.addLayout(controls_col, 1)
        layout.addLayout(mid_row)

    def _update_mute_btn_style(self) -> None:
        lang = self.window.current_language
        if self.rule.mute:
            self.mute_btn.setText(t("btn_muted", lang))
            self.mute_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a0d24, stop:1 #240510);
                    color: #ff2a85;
                    border: 1px solid #ff2a85;
                    border-bottom: 2px solid #850e41;
                    border-radius: 6px;
                    padding: 5px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: #5e102f;
                    color: #ffffff;
                }
            """)
        else:
            self.mute_btn.setText(t("btn_sound_active", lang))
            self.mute_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0d2838, stop:1 #061520);
                    color: #00f0ff;
                    border: 1px solid rgba(0, 240, 255, 0.4);
                    border-bottom: 2px solid #005f73;
                    border-radius: 6px;
                    padding: 5px;
                    font-weight: 600;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: #113850;
                    border-color: #00f0ff;
                    color: #ffffff;
                }
            """)

    def _on_slider_changed(self, value: int) -> None:
        self.rule.volume = value / 100.0
        self.vol_value_label.setText(t("percent_fmt", self.window.current_language, percent=value))
        self.dial.volume = self.rule.volume
        self.window.on_rule_volume_updated(self.index, self.rule.volume)

    def _on_dial_changed(self, value: int) -> None:
        self.slider.setValue(value)
        self.window.save_settings()

    def _toggle_mute(self) -> None:
        self.rule.mute = not self.rule.mute
        self.dial.muted = self.rule.mute
        self._update_mute_btn_style()
        self.window.on_rule_mute_updated(self.index, self.rule.mute)
        self.window.save_settings()

    def retranslate(self, lang: str) -> None:
        self.vol_title.setText(t("target_game_volume", lang))
        self.vol_value_label.setText(t("percent_fmt", lang, percent=round(self.rule.volume * 100)))
        self.remove_btn.setText(t("btn_remove", lang))
        self.remove_btn.setToolTip(t("tooltip_remove", lang))
        self._update_mute_btn_style()
        self.dial.sub_label = t("dial_volume_sub", lang)
        self.dial.percent_fmt = t("percent_fmt", lang, percent="{percent}")
        self.dial.update()


# ============================================================================
# MAIN 3D APPLICATION WINDOW
# ============================================================================
class MixerWindow(QMainWindow):
    def __init__(self, config: AppConfig, config_path: Path) -> None:
        super().__init__()
        self.config = config
        self.config_path = config_path
        self._closing = False
        self._mixer: AudioMixer | None = None
        self._status_state = "waiting"

        self._app_icon = self._load_app_icon()
        if not self._app_icon.isNull():
            self.setWindowIcon(self._app_icon)

        self.setWindowTitle(t("app_title", self.current_language))
        self.resize(780, 720)
        self.setMinimumSize(700, 580)
        self.setStyleSheet(CYBER_STYLESHEET)

        self._build_ui()
        self._populate_rules()
        self._build_tray()

        try:
            self._mixer = AudioMixer(self._append_log)
        except AudioBackendError as exc:
            self._append_log(str(exc))
            QMessageBox.warning(self, t("msg_audio_backend_title", self.current_language), str(exc))
            self._set_status_state("audio_init_error")
            self.toggle_button.setEnabled(False)

        self._timer = QTimer(self)
        self._timer.setInterval(500)
        self._timer.timeout.connect(self._poll)
        self._timer.start()
        self._poll()

    @property
    def current_language(self) -> str:
        lang = getattr(self.config, "language", "tr")
        return lang if lang in ("tr", "en") else "tr"

    def paintEvent(self, event: object) -> None:
        """Draw ambient 3D glowing auras and subtle cybernetic grid lines."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # 1. Base dark background
        painter.fillRect(0, 0, w, h, QColor("#070914"))

        # 2. Ambient glowing orbs (Cyan top-left, Magenta top-right)
        rad_cyan = QRadialGradient(QPointF(w * 0.15, h * 0.12), 320)
        rad_cyan.setColorAt(0.0, QColor(0, 240, 255, 30))
        rad_cyan.setColorAt(1.0, QColor(0, 240, 255, 0))
        painter.fillRect(0, 0, w, h, QBrush(rad_cyan))

        rad_magenta = QRadialGradient(QPointF(w * 0.85, h * 0.18), 340)
        rad_magenta.setColorAt(0.0, QColor(255, 42, 133, 26))
        rad_magenta.setColorAt(1.0, QColor(255, 42, 133, 0))
        painter.fillRect(0, 0, w, h, QBrush(rad_magenta))

        # 3. Subtle Cybernetic Grid lines
        grid_pen = QPen(QColor(0, 240, 255, 10), 1)
        painter.setPen(grid_pen)
        step = 40
        for x in range(0, w, step):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h, step):
            painter.drawLine(0, y, w, y)

    def _load_app_icon(self) -> QIcon:
        import sys
        base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
        icon_path = base_dir / "mixer_app" / "resources" / "icon.png"
        if icon_path.exists():
            return QIcon(str(icon_path))
        # Fallback to direct relative path
        direct_path = Path(__file__).resolve().parent / "resources" / "icon.png"
        if direct_path.exists():
            return QIcon(str(direct_path))
        return QIcon()

    def _build_ui(self) -> None:
        lang = self.current_language
        central = QWidget(self)
        central.setObjectName("CentralWidget")
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 16, 20, 18)
        main_layout.setSpacing(14)

        # ---------------------------------------------------------
        # TOP HUD BAR: BRANDING + LANGUAGE SELECTION BUTTON
        # ---------------------------------------------------------
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(2, 0, 2, 0)

        self.hud_brand = QLabel(t("hud_top_badge", lang))
        self.hud_brand.setStyleSheet("""
            QLabel {
                color: #38bdf8;
                font-weight: 800;
                font-size: 11px;
                letter-spacing: 1.5px;
            }
        """)
        top_bar.addWidget(self.hud_brand)
        top_bar.addStretch()

        # Language Selection Capsule
        self.lang_container = QFrame(central)
        self.lang_container.setObjectName("LangContainer")
        self.lang_container.setStyleSheet("""
            QFrame#LangContainer {
                background: rgba(13, 17, 36, 0.75);
                border: 1px solid rgba(0, 240, 255, 0.35);
                border-radius: 12px;
            }
        """)
        lang_layout = QHBoxLayout(self.lang_container)
        lang_layout.setContentsMargins(4, 3, 4, 3)
        lang_layout.setSpacing(4)

        lang_icon = QLabel("🌐")
        lang_icon.setStyleSheet("color: #00f0ff; font-size: 11px; background: transparent;")
        lang_layout.addWidget(lang_icon)

        self.btn_lang_tr = QPushButton("🇹🇷 TR")
        self.btn_lang_tr.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_lang_tr.clicked.connect(lambda: self.set_language("tr"))
        lang_layout.addWidget(self.btn_lang_tr)

        self.btn_lang_en = QPushButton("🇬🇧 EN")
        self.btn_lang_en.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_lang_en.clicked.connect(lambda: self.set_language("en"))
        lang_layout.addWidget(self.btn_lang_en)

        self.lang_container.setToolTip(t("lang_switch_tooltip", lang))
        self._update_lang_buttons()

        top_bar.addWidget(self.lang_container)
        main_layout.addLayout(top_bar)

        # ---------------------------------------------------------
        # TOP HERO SECTION: 2 FLOATING 3D CARDS
        # ---------------------------------------------------------
        hero_layout = QHBoxLayout()
        hero_layout.setSpacing(16)

        # Card 1: 3D LoL Detection Radar & Status Card
        self.radar_card = CyberCard(QColor(0, 240, 255, 95), "#00f0ff", central)
        radar_card_layout = QHBoxLayout(self.radar_card)
        radar_card_layout.setContentsMargins(16, 14, 16, 14)
        radar_card_layout.setSpacing(14)

        self.radar_widget = CyberRadarWidget(self.radar_card)
        radar_card_layout.addWidget(self.radar_widget)

        status_info_layout = QVBoxLayout()
        status_info_layout.setSpacing(4)
        self.status_badge = QLabel(t("system_status_badge", lang))
        self.status_badge.setStyleSheet("color: #38bdf8; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        status_info_layout.addWidget(self.status_badge)

        self.status_label = QLabel(t("status_waiting", lang))
        self.status_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 15px;")
        status_info_layout.addWidget(self.status_label)

        triggers_text = ", ".join(self.config.trigger_processes)
        self.trigger_label = QLabel(f"{t('trigger_prefix', lang)}{triggers_text}")
        self.trigger_label.setStyleSheet("color: #64748b; font-size: 11px;")
        self.trigger_label.setWordWrap(True)
        status_info_layout.addWidget(self.trigger_label)

        radar_card_layout.addLayout(status_info_layout, 1)
        hero_layout.addWidget(self.radar_card, 6)

        # Card 2: 3D Master Mode & Action Controls
        self.control_card = CyberCard(QColor(189, 52, 254, 95), "#bd34fe", central)
        control_card_layout = QVBoxLayout(self.control_card)
        control_card_layout.setContentsMargins(16, 14, 16, 14)
        control_card_layout.setSpacing(10)

        self.ctrl_badge = QLabel(t("control_center_badge", lang))
        self.ctrl_badge.setStyleSheet("color: #e879f9; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        control_card_layout.addWidget(self.ctrl_badge)

        self.toggle_button = QPushButton()
        self.toggle_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggle_button.clicked.connect(self._toggle_enabled)
        control_card_layout.addWidget(self.toggle_button)

        quick_btns = QHBoxLayout()
        quick_btns.setSpacing(8)

        self.add_btn = QPushButton(t("btn_add_app", lang))
        self.add_btn.setProperty("class", "cyber-btn-cyan")
        self.add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_btn.clicked.connect(self._add_rule)
        quick_btns.addWidget(self.add_btn)

        self.browse_btn = QPushButton(t("btn_browse", lang))
        self.browse_btn.setProperty("class", "cyber-btn-cyan")
        self.browse_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.browse_btn.clicked.connect(self._browse_executable)
        quick_btns.addWidget(self.browse_btn)

        control_card_layout.addLayout(quick_btns)
        hero_layout.addWidget(self.control_card, 5)

        main_layout.addLayout(hero_layout)

        # ---------------------------------------------------------
        # SECTION TITLE: 3D SES KONTROL KARTLARI
        # ---------------------------------------------------------
        section_header = QHBoxLayout()
        self.section_title = QLabel(t("section_rules_title", lang))
        self.section_title.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 12px; letter-spacing: 1.5px;")
        section_header.addWidget(self.section_title)

        self.rules_count_badge = QLabel(rules_count_text(len(self.config.rules), lang))
        self.rules_count_badge.setStyleSheet("""
            background: rgba(0, 240, 255, 0.15);
            color: #00f0ff;
            border: 1px solid rgba(0, 240, 255, 0.4);
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 11px;
            font-weight: bold;
        """)
        section_header.addWidget(self.rules_count_badge)
        section_header.addStretch()
        main_layout.addLayout(section_header)

        # ---------------------------------------------------------
        # SCROLL AREA FOR 3D CARDS
        # ---------------------------------------------------------
        self.scroll_area = QScrollArea(central)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(4, 4, 12, 4)
        self.cards_layout.setSpacing(14)
        self.cards_layout.addStretch()

        self.scroll_area.setWidget(self.cards_container)
        main_layout.addWidget(self.scroll_area, 1)

        # ---------------------------------------------------------
        # BOTTOM 3D HOLOGRAPHIC LOG CONSOLE
        # ---------------------------------------------------------
        log_header = QHBoxLayout()
        self.log_title = QLabel(t("log_header", lang))
        self.log_title.setStyleSheet("color: #64748b; font-weight: bold; font-size: 10px; letter-spacing: 1px;")
        log_header.addWidget(self.log_title)
        log_header.addStretch()

        self.clear_log_btn = QPushButton(t("btn_clear", lang))
        self.clear_log_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #64748b;
                border: none;
                font-size: 10px;
            }
            QPushButton:hover {
                color: #00f0ff;
            }
        """)
        self.clear_log_btn.clicked.connect(lambda: self.log_view.clear())
        log_header.addWidget(self.clear_log_btn)
        main_layout.addLayout(log_header)

        self.log_view = QPlainTextEdit(central)
        self.log_view.setProperty("class", "cyber-log")
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(250)
        self.log_view.setMaximumHeight(85)
        main_layout.addWidget(self.log_view)

        self.setCentralWidget(central)
        self._update_toggle_button()

    def _update_lang_buttons(self) -> None:
        lang = self.current_language
        active_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #00f0ff, stop:1 #0077b6);
                color: #070914;
                font-weight: 800;
                font-size: 11px;
                border: 1px solid #7df8ff;
                border-bottom: 2px solid #004d61;
                border-radius: 8px;
                padding: 3px 9px;
            }
        """
        inactive_style = """
            QPushButton {
                background: rgba(15, 23, 42, 0.6);
                color: #94a3b8;
                font-weight: 600;
                font-size: 11px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 3px 9px;
            }
            QPushButton:hover {
                background: rgba(0, 240, 255, 0.15);
                color: #00f0ff;
                border-color: rgba(0, 240, 255, 0.4);
            }
        """
        if lang == "tr":
            self.btn_lang_tr.setStyleSheet(active_style)
            self.btn_lang_en.setStyleSheet(inactive_style)
        else:
            self.btn_lang_tr.setStyleSheet(inactive_style)
            self.btn_lang_en.setStyleSheet(active_style)

    def set_language(self, lang: str) -> None:
        if lang not in ("tr", "en") or self.config.language == lang:
            return
        self.config.language = lang
        self.save_settings()
        self._retranslate_ui()
        lang_name = "Türkçe" if lang == "tr" else "English"
        self._append_log(t("log_lang_changed", lang, lang_name=lang_name))

    def _retranslate_ui(self) -> None:
        lang = self.current_language
        self.setWindowTitle(t("app_title", lang))
        self.hud_brand.setText(t("hud_top_badge", lang))
        self.status_badge.setText(t("system_status_badge", lang))
        self._set_status_state(self._status_state)
        triggers_text = ", ".join(self.config.trigger_processes)
        self.trigger_label.setText(f"{t('trigger_prefix', lang)}{triggers_text}")
        self.ctrl_badge.setText(t("control_center_badge", lang))
        self._update_toggle_button()
        self.add_btn.setText(t("btn_add_app", lang))
        self.browse_btn.setText(t("btn_browse", lang))
        self.section_title.setText(t("section_rules_title", lang))
        self.rules_count_badge.setText(rules_count_text(len(self.config.rules), lang))
        self.log_title.setText(t("log_header", lang))
        self.clear_log_btn.setText(t("btn_clear", lang))
        self.lang_container.setToolTip(t("lang_switch_tooltip", lang))
        self._update_lang_buttons()

        # Update cards
        for i in range(self.cards_layout.count()):
            item = self.cards_layout.itemAt(i)
            widget = item.widget() if item else None
            if isinstance(widget, AppAudioCard):
                widget.retranslate(lang)

        # Update tray if present
        if getattr(self, "_tray", None) is not None:
            self._tray.setToolTip(t("tray_tooltip", lang))
            if hasattr(self, "_show_action"):
                self._show_action.setText(t("tray_show", lang))
            if hasattr(self, "_toggle_action"):
                self._toggle_action.setText(t("tray_toggle", lang))
            if hasattr(self, "_quit_action"):
                self._quit_action.setText(t("tray_quit", lang))

    def _set_status_state(self, state: str) -> None:
        self._status_state = state
        lang = self.current_language
        text_map = {
            "waiting": t("status_waiting_dots", lang),
            "active": t("status_active", lang),
            "disabled": t("status_disabled", lang),
            "audio_error": t("status_audio_error", lang),
            "audio_init_error": t("status_audio_init_error", lang),
        }
        self.status_label.setText(text_map.get(state, t("status_waiting", lang)))
        radar_map = {
            "waiting": "waiting",
            "active": "active",
            "disabled": "disabled",
            "audio_error": "disabled",
            "audio_init_error": "disabled",
        }
        self.radar_widget.set_status(radar_map.get(state, "waiting"))

    def _populate_rules(self) -> None:
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for index, rule in enumerate(self.config.rules):
            card = AppAudioCard(rule=rule, index=index, window=self)
            self.cards_layout.insertWidget(index, card)

        self.rules_count_badge.setText(rules_count_text(len(self.config.rules), self.current_language))

    def _build_tray(self) -> None:
        lang = self.current_language
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self._tray: QSystemTrayIcon | None = None
            self._append_log(t("log_tray_unavailable", lang))
            return

        tray_icon = (
            self._app_icon
            if not self._app_icon.isNull()
            else self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume)
        )
        self._tray = QSystemTrayIcon(tray_icon, self)
        self._tray.setToolTip(t("tray_tooltip", lang))
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: #0d1124;
                color: #e2e8f0;
                border: 1px solid #00f0ff;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background: #1e293b;
                color: #00f0ff;
            }
        """)
        self._show_action = QAction(t("tray_show", lang), self)
        self._show_action.triggered.connect(self.showNormal)
        self._toggle_action = QAction(t("tray_toggle", lang), self)
        self._toggle_action.triggered.connect(self._toggle_enabled)
        self._quit_action = QAction(t("tray_quit", lang), self)
        self._quit_action.triggered.connect(self.close_application)
        menu.addAction(self._show_action)
        menu.addAction(self._toggle_action)
        menu.addSeparator()
        menu.addAction(self._quit_action)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._tray_activated)
        self._tray.show()

    def _append_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_view.appendPlainText(f"[{timestamp}] {message}")

    def save_settings(self) -> None:
        try:
            save_config(self.config_path, self.config)
        except ConfigError as exc:
            QMessageBox.warning(self, t("msg_save_error_title", self.current_language), str(exc))
            self._append_log(str(exc))

    def on_rule_volume_updated(self, index: int, volume: float) -> None:
        if 0 <= index < len(self.config.rules):
            self.config.rules[index].volume = volume

    def on_rule_mute_updated(self, index: int, muted: bool) -> None:
        if 0 <= index < len(self.config.rules):
            self.config.rules[index].mute = muted

    def remove_card_rule(self, index: int) -> None:
        if 0 <= index < len(self.config.rules):
            removed_rule = self.config.rules.pop(index)
            self._append_log(t("log_rule_removed", self.current_language, process=removed_rule.process))
            self._populate_rules()
            self.save_settings()

    def _add_rule(self) -> None:
        lang = self.current_language
        process, accepted = QInputDialog.getText(
            self,
            t("dialog_add_title", lang),
            t("dialog_add_prompt", lang),
        )
        if not accepted:
            return
        self._add_process_rule(process)

    def _browse_executable(self) -> None:
        lang = self.current_language
        executable_path, _ = QFileDialog.getOpenFileName(
            self,
            t("dialog_browse_title", lang),
            "",
            t("dialog_browse_filter", lang),
        )
        if executable_path:
            self._add_process_rule(executable_path)

    def _add_process_rule(self, process: str) -> None:
        lang = self.current_language
        process = process.strip()
        if not process.lower().endswith(".exe"):
            QMessageBox.warning(self, t("msg_invalid_process_title", lang), t("msg_invalid_process_text", lang))
            return
        process = Path(process).name
        if any(rule.process.casefold() == process.casefold() for rule in self.config.rules):
            QMessageBox.information(self, t("msg_already_exists_title", lang), t("msg_already_exists_text", lang, process=process))
            return
        self.config.rules.append(MixerRule(process=process, volume=0.5, mute=False))
        self._append_log(t("log_rule_added", lang, process=process))
        self._populate_rules()
        self.save_settings()

    def _toggle_enabled(self) -> None:
        self.config.enabled = not self.config.enabled
        self._update_toggle_button()
        self.save_settings()
        if not self.config.enabled:
            self._set_status_state("disabled")

    def _update_toggle_button(self) -> None:
        lang = self.current_language
        if self.config.enabled:
            self.toggle_button.setText(t("btn_mode_on", lang))
            self.toggle_button.setProperty("class", "cyber-btn-mode-on")
        else:
            self.toggle_button.setText(t("btn_mode_off", lang))
            self.toggle_button.setProperty("class", "cyber-btn-mode-off")
        self.toggle_button.style().unpolish(self.toggle_button)
        self.toggle_button.style().polish(self.toggle_button)

    def _poll(self) -> None:
        if self._mixer is None:
            return
        try:
            active = self._mixer.tick(self.config)
        except Exception as exc:
            self._append_log(t("log_audio_error", self.current_language, exc=exc))
            self._set_status_state("audio_error")
            return

        if not self.config.enabled:
            self._set_status_state("disabled")
        else:
            if active:
                self._set_status_state("active")
            else:
                self._set_status_state("waiting")

    def _tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.showNormal()
                self.raise_()
                self.activateWindow()

    def closeEvent(self, event: object) -> None:
        if self._tray is not None and self._tray.isVisible():
            self.hide()
            event.ignore()
            return
        self._shutdown()
        event.accept()
        application = QApplication.instance()
        if application is not None:
            application.quit()

    def close_application(self) -> None:
        self._shutdown()
        self.hide()
        application = QApplication.instance()
        if application is not None:
            application.quit()

    def _shutdown(self) -> None:
        if self._closing:
            return
        self._closing = True
        self.save_settings()
        if self._mixer is not None:
            self._mixer.close()
            self._mixer = None
        if self._tray is not None:
            self._tray.hide()
        self._timer.stop()
