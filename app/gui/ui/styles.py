from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QWidget

from app.constants import FONTS_DIRECTORY


@dataclass(frozen=True)
class Theme:
    """Colour tokens from docs/design/DESIGN.md."""

    window: str
    panel: str
    panel_border: str
    field: str
    raised: str
    border: str
    text: str
    muted: str
    accent: str
    accent_hover: str
    accent_pressed: str
    accent_text: str
    on_accent: str
    success: str
    success_bg: str
    success_border: str
    warning: str
    warning_bg: str
    danger: str
    danger_bg: str
    danger_border: str
    lsb_bg: str
    lsb_text: str


DARK = Theme(
    window="#141518",
    panel="#1D1F23",
    panel_border="#2C2F34",
    field="#25282D",
    raised="#2B2F35",
    border="#3A3E45",
    text="#ECEDEE",
    muted="#A1A5AC",
    accent="#2F6FDB",
    accent_hover="#3D7CE6",
    accent_pressed="#2760C2",
    accent_text="#7AAEFF",
    on_accent="#FFFFFF",
    success="#5FD39A",
    success_bg="#16261E",
    success_border="#24533A",
    warning="#F0BE6A",
    warning_bg="#2A2214",
    danger="#F2907D",
    danger_bg="#2C1916",
    danger_border="#B9533F",
    lsb_bg="#23324A",
    lsb_text="#9CC2FF",
)

_PREFERRED_FONTS = (
    "Inter",
    "SF Pro Text",
    "Segoe UI",
    "Cantarell",
    "Ubuntu",
    "Helvetica Neue",
    "Arial",
)
_FONT_EXTENSIONS = (".ttf", ".otf")
_BASE_FONT_SIZE = 9


def theme() -> Theme:
    return DARK


def _load_bundled_fonts() -> None:
    if not FONTS_DIRECTORY.is_dir():
        return
    for path in sorted(FONTS_DIRECTORY.iterdir()):
        if path.suffix.lower() in _FONT_EXTENSIONS:
            QFontDatabase.addApplicationFont(str(path))


def _ui_font_family() -> str:
    available = set(QFontDatabase.families())
    for family in _PREFERRED_FONTS:
        if family in available:
            return family
    return QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont).family()


def app_font() -> QFont:
    font = QFont(_ui_font_family(), _BASE_FONT_SIZE)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    return font


def global_stylesheet(t: Theme) -> str:
    return f"""
    QWidget {{
        color: {t.text};
    }}

    QMainWindow, QWidget#central, QWidget#form, QWidget#result_page {{
        background-color: {t.window};
    }}

    QScrollArea, QScrollArea > QWidget > QWidget {{
        background: transparent;
        border: none;
    }}

    QLabel {{
        background: transparent;
    }}

    QLabel[role="section"] {{
        font-weight: 600;
    }}

    QLabel[role="title"] {{
        font-size: 13pt;
        font-weight: 600;
    }}

    QLabel[role="strong"] {{
        font-weight: 500;
    }}

    QLabel[role="muted"] {{
        color: {t.muted};
    }}

    QLabel[role="hint"] {{
        color: {t.muted};
        font-size: 8pt;
    }}

    QLabel[role="error"] {{
        color: {t.danger};
        font-size: 8pt;
    }}

    QLabel[role="success"] {{
        color: {t.success};
        font-size: 8pt;
    }}

    QLabel[badge="pending"] {{
        background-color: {t.raised};
        color: {t.muted};
        border-radius: 8px;
        font-size: 7pt;
        font-weight: 600;
    }}

    QLabel[badge="done"] {{
        background-color: {t.success_bg};
        border-radius: 8px;
    }}

    QLabel[badge="error"] {{
        background-color: {t.danger_bg};
        border-radius: 8px;
    }}

    QLabel[chip="lsb"], QLabel[chip="exif"] {{
        border-radius: 3px;
        padding: 0 4px;
        font-size: 7pt;
        font-weight: 600;
    }}

    QLabel[chip="lsb"] {{
        background-color: {t.lsb_bg};
        color: {t.lsb_text};
    }}

    QLabel[chip="exif"] {{
        background-color: {t.warning_bg};
        color: {t.warning};
    }}

    QLabel#thumbnail {{
        background-color: {t.raised};
        border-radius: 4px;
    }}

    QFrame[card="true"] {{
        background-color: {t.panel};
        border: 1px solid {t.panel_border};
        border-radius: 6px;
    }}

    QFrame[card="true"] QLabel {{
        border: none;
    }}

    QFrame[dropzone="true"] {{
        background-color: {t.panel};
        border: 1px dashed {t.border};
        border-radius: 6px;
    }}

    QFrame[dropzone="true"][dragging="true"] {{
        border-color: {t.accent};
    }}

    QFrame[callout="warning"] {{
        background-color: {t.warning_bg};
        border-radius: 5px;
    }}

    QFrame[callout="warning"] QLabel {{
        color: {t.warning};
    }}

    QFrame[callout="error"] {{
        background-color: {t.danger_bg};
        border-radius: 5px;
    }}

    QFrame[callout="error"] QLabel {{
        color: {t.danger};
    }}

    QFrame[result="success"] {{
        background-color: {t.success_bg};
        border: 1px solid {t.success_border};
        border-radius: 6px;
    }}

    QFrame[result="success"] QLabel[role="status"] {{
        color: {t.success};
        font-weight: 600;
    }}

    QFrame#segmented {{
        background-color: {t.panel};
        border: 1px solid {t.panel_border};
        border-radius: 6px;
    }}

    QPushButton {{
        background-color: {t.raised};
        color: {t.text};
        border: 1px solid {t.border};
        border-radius: 5px;
        padding: 0 10px;
        min-height: 24px;
        font-weight: 500;
    }}

    QPushButton:hover {{
        border-color: {t.muted};
    }}

    QPushButton:focus {{
        border-color: {t.accent};
    }}

    QPushButton[variant="segment"] {{
        background: transparent;
        color: {t.muted};
        border: none;
        border-radius: 4px;
        min-height: 24px;
    }}

    QPushButton[variant="segment"]:checked {{
        background-color: {t.raised};
        color: {t.text};
        font-weight: 600;
    }}

    QPushButton[variant="segment"]:focus {{
        border: 1px solid {t.accent};
    }}

    QPushButton[variant="primary"] {{
        background-color: {t.accent};
        color: {t.on_accent};
        border: none;
        border-radius: 6px;
        min-height: 32px;
        font-size: 10pt;
        font-weight: 600;
    }}

    QPushButton[variant="primary"]:hover {{
        background-color: {t.accent_hover};
    }}

    QPushButton[variant="primary"]:pressed {{
        background-color: {t.accent_pressed};
    }}

    QPushButton[variant="primary"]:disabled {{
        background-color: {t.raised};
        color: {t.muted};
    }}

    QPushButton[variant="ghost"] {{
        background: transparent;
        border: none;
        min-height: 22px;
        min-width: 22px;
        padding: 0;
    }}

    QPushButton[variant="ghost"]:hover {{
        background-color: {t.raised};
    }}

    QPushButton[variant="success"] {{
        background-color: {t.success_bg};
        border: 1px solid {t.success_border};
        color: {t.text};
        min-height: 20px;
        padding: 0 8px;
        font-size: 8pt;
    }}

    QLineEdit, QPlainTextEdit {{
        background-color: {t.field};
        color: {t.text};
        border: 1px solid {t.border};
        border-radius: 5px;
        padding: 0 6px;
        min-height: 24px;
        selection-background-color: {t.accent};
        selection-color: {t.on_accent};
    }}

    QPlainTextEdit {{
        padding: 3px 4px;
    }}

    QLineEdit {{
        /* U+2022: Inter's default U+25CF dot is oversized at this text size. */
        lineedit-password-character: 8226;
    }}

    QLineEdit:focus, QPlainTextEdit:focus {{
        border-color: {t.accent};
    }}

    QLineEdit[invalid="true"], QPlainTextEdit[invalid="true"] {{
        border-color: {t.danger_border};
    }}

    QLineEdit:disabled {{
        color: {t.muted};
        background-color: {t.panel};
    }}

    QPlainTextEdit[revealed="true"] {{
        background-color: {t.window};
        border: none;
    }}

    QProgressBar {{
        background-color: {t.raised};
        border: none;
        border-radius: 2px;
        max-height: 4px;
        min-height: 4px;
    }}

    QProgressBar::chunk {{
        background-color: {t.accent_text};
        border-radius: 2px;
    }}

    QProgressBar[over="true"]::chunk {{
        background-color: {t.danger};
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background-color: {t.raised};
        border-radius: 3px;
        min-height: 24px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {t.border};
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        height: 0;
        background: transparent;
    }}

    QToolTip {{
        background-color: {t.panel};
        color: {t.text};
        border: 1px solid {t.border};
    }}
    """


def set_property(widget: QWidget, name: str, value: object) -> None:
    """Set a dynamic property and re-apply the stylesheet rules that use it."""
    if widget.property(name) == value:
        return
    widget.setProperty(name, value)
    style = widget.style()
    if style is not None:
        style.unpolish(widget)
        style.polish(widget)
    widget.update()


def apply_app_theme(app: QApplication) -> None:
    # Pin Qt's own scheme too, so Fusion's palette (menus, tooltips, dialogs) stays dark
    # even when the OS is in light mode.
    QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Dark)  # pyright: ignore[reportOptionalMemberAccess]
    app.setStyle("Fusion")
    _load_bundled_fonts()
    app.setFont(app_font())
    app.setStyleSheet(global_stylesheet(DARK))
