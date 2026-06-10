from dataclasses import dataclass

from PyQt6.QtGui import QFont
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import QApplication


@dataclass(frozen=True)
class AccentPalette:
    base: str
    hover: str
    pressed: str


# Dear ImGui StyleColorsDark palette
WINDOW_BG = "#1A1A1A"
TEXT = "#F0F0F0"
TEXT_SECONDARY = "#A0A0A0"
TEXT_DISABLED = "#808080"
INPUT_BG = "#2D363F"
BORDER = "#454545"
SEPARATOR = "#454545"
INPUT_FONT_SIZE = 11

HIDE_ACCENT = AccentPalette(base="#4296FA", hover="#5AA8FB", pressed="#0F87FA")
REVEAL_ACCENT = AccentPalette(base="#4CC84B", hover="#5BD85A", pressed="#3DB83C")

_INACTIVE_BTN_BG = "#2D363F"
_INACTIVE_BTN_HOVER = "#3A4550"

_PREFERRED_FONTS = ("Segoe UI", "SF Pro Text", "Helvetica Neue", "Arial")


def _system_sans_font() -> str:
    available = set(QFontDatabase.families())
    for family in _PREFERRED_FONTS:
        if family in available:
            return family
    return QFont().defaultFamily()


def app_font() -> QFont:
    font = QFont(_system_sans_font(), 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    return font


def global_stylesheet() -> str:
    return f"""
    QWidget {{
        background-color: {WINDOW_BG};
        color: {TEXT};
    }}

    QLabel {{
        background-color: transparent;
        color: {TEXT};
        padding: 0;
    }}

    QPlainTextEdit {{
        background-color: {INPUT_BG};
        color: {TEXT};
        font-size: {INPUT_FONT_SIZE}pt;
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 3px 5px;
        selection-background-color: {HIDE_ACCENT.base};
        selection-color: #FFFFFF;
    }}

    QPlainTextEdit:read-only {{
        color: {TEXT_SECONDARY};
    }}

    QLineEdit {{
        background-color: {INPUT_BG};
        color: {TEXT};
        font-size: {INPUT_FONT_SIZE}pt;
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 2px 6px;
        min-height: 22px;
        selection-background-color: {HIDE_ACCENT.base};
        selection-color: #FFFFFF;
    }}

    QLineEdit:read-only {{
        color: {TEXT_SECONDARY};
    }}

    QLineEdit::placeholder,
    QPlainTextEdit::placeholder {{
        color: {TEXT_SECONDARY};
    }}

    QPushButton {{
        background-color: {_INACTIVE_BTN_BG};
        color: {TEXT};
        border: none;
        border-radius: 4px;
        padding: 6px 12px;
        min-height: 24px;
    }}

    QPushButton:hover {{
        background-color: {_INACTIVE_BTN_HOVER};
    }}

    QPushButton:pressed {{
        background-color: {INPUT_BG};
    }}

    QPushButton:disabled {{
        background-color: {INPUT_BG};
        color: {TEXT_DISABLED};
    }}

    QCheckBox {{
        color: {TEXT};
        spacing: 8px;
    }}

    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 2px;
        border: 1px solid {BORDER};
        background-color: {INPUT_BG};
    }}

    QCheckBox::indicator:hover {{
        border-color: {HIDE_ACCENT.base};
    }}

    QCheckBox::indicator:checked {{
        background-color: {HIDE_ACCENT.base};
        border-color: {HIDE_ACCENT.base};
    }}

    QCheckBox::indicator:disabled {{
        background-color: {WINDOW_BG};
        border-color: {BORDER};
    }}

    QStatusBar {{
        background-color: {WINDOW_BG};
        color: {TEXT};
        border-top: 1px solid {SEPARATOR};
    }}

    QStatusBar::item {{
        border: none;
    }}

    QFrame[frameShape="4"] {{
        background-color: {SEPARATOR};
        border: none;
        max-height: 1px;
    }}
    """


def apply_app_theme(app: QApplication) -> None:
    app.setFont(app_font())
    app.setStyleSheet(global_stylesheet())


def mode_button_active(palette: AccentPalette) -> str:
    return (
        "QPushButton {"
        f"  background-color: {palette.base};"
        "  color: #FFFFFF;"
        "  border: none;"
        "  border-radius: 4px;"
        "  padding: 6px 14px;"
        "  font-weight: 500;"
        "}"
        "QPushButton:hover {"
        f"  background-color: {palette.hover};"
        "}"
        "QPushButton:pressed {"
        f"  background-color: {palette.pressed};"
        "}"
    )


def mode_button_inactive() -> str:
    return (
        "QPushButton {"
        f"  background-color: {_INACTIVE_BTN_BG};"
        f"  color: {TEXT};"
        "  border: none;"
        "  border-radius: 4px;"
        "  padding: 6px 14px;"
        "  font-weight: 400;"
        "}"
        "QPushButton:hover {"
        f"  background-color: {_INACTIVE_BTN_HOVER};"
        "}"
        "QPushButton:pressed {"
        f"  background-color: {INPUT_BG};"
        "}"
    )


def secondary_button() -> str:
    return mode_button_inactive()


def accent_bar(palette: AccentPalette) -> str:
    return (
        f"background-color: {SEPARATOR};"
        " border: none;"
        f" border-bottom: 2px solid {palette.base};"
    )


def separator() -> str:
    return f"background-color: {SEPARATOR}; border: none;"


def action_button(palette: AccentPalette) -> str:
    return (
        "QPushButton {"
        f"  background-color: {palette.base};"
        "  color: #FFFFFF;"
        "  border: none;"
        "  border-radius: 4px;"
        "  padding: 8px 16px;"
        "  min-height: 34px;"
        "  font-weight: 500;"
        "}"
        "QPushButton:hover {"
        f"  background-color: {palette.hover};"
        "}"
        "QPushButton:pressed {"
        f"  background-color: {palette.pressed};"
        "}"
    )
