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

LIGHT = Theme(
    window="#F4F5F7",
    panel="#FFFFFF",
    panel_border="#DADDE2",
    field="#F7F8FA",
    raised="#ECEEF1",
    border="#DADDE2",
    text="#17191C",
    muted="#5B616B",
    accent="#2563D9",
    accent_hover="#1F56C2",
    accent_pressed="#1A4AA8",
    accent_text="#1F56C2",
    on_accent="#FFFFFF",
    success="#1F8A56",
    success_bg="#EAF6EF",
    success_border="#B9DFC8",
    warning="#9A6408",
    warning_bg="#FBF1DD",
    danger="#C2412D",
    danger_bg="#FBEAE6",
    danger_border="#E3A497",
    lsb_bg="#E3ECFB",
    lsb_text="#1F56C2",
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
_BASE_FONT_SIZE = 10

_theme: Theme = DARK


def theme() -> Theme:
    return _theme


def _detect_theme() -> Theme:
    """Dark is the reference look; light only when the OS asks for it."""
    scheme = QGuiApplication.styleHints().colorScheme()  # pyright: ignore[reportOptionalMemberAccess]
    return LIGHT if scheme == Qt.ColorScheme.Light else DARK


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
        font-size: 16pt;
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
        font-size: 9pt;
    }}

    QLabel[role="error"] {{
        color: {t.danger};
        font-size: 9pt;
    }}

    QLabel[role="success"] {{
        color: {t.success};
        font-size: 9pt;
    }}

    QLabel[badge="pending"] {{
        background-color: {t.raised};
        color: {t.muted};
        border-radius: 10px;
        font-size: 8pt;
        font-weight: 600;
    }}

    QLabel[badge="done"] {{
        background-color: {t.success_bg};
        border-radius: 10px;
    }}

    QLabel[badge="error"] {{
        background-color: {t.danger_bg};
        border-radius: 10px;
    }}

    QLabel[chip="lsb"], QLabel[chip="exif"] {{
        border-radius: 4px;
        padding: 1px 6px;
        font-size: 8pt;
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
        border-radius: 6px;
    }}

    QFrame[card="true"] {{
        background-color: {t.panel};
        border: 1px solid {t.panel_border};
        border-radius: 10px;
    }}

    QFrame[card="true"] QLabel {{
        border: none;
    }}

    QFrame[dropzone="true"] {{
        background-color: {t.panel};
        border: 2px dashed {t.border};
        border-radius: 12px;
    }}

    QFrame[dropzone="true"][dragging="true"] {{
        border-color: {t.accent};
    }}

    QFrame[callout="warning"] {{
        background-color: {t.warning_bg};
        border-radius: 8px;
    }}

    QFrame[callout="warning"] QLabel {{
        color: {t.warning};
    }}

    QFrame[callout="error"] {{
        background-color: {t.danger_bg};
        border-radius: 8px;
    }}

    QFrame[callout="error"] QLabel {{
        color: {t.danger};
    }}

    QFrame[result="success"] {{
        background-color: {t.success_bg};
        border: 1px solid {t.success_border};
        border-radius: 12px;
    }}

    QFrame[result="success"] QLabel[role="status"] {{
        color: {t.success};
        font-weight: 600;
    }}

    QFrame#segmented {{
        background-color: {t.panel};
        border: 1px solid {t.panel_border};
        border-radius: 10px;
    }}

    QPushButton {{
        background-color: {t.raised};
        color: {t.text};
        border: 1px solid {t.border};
        border-radius: 8px;
        padding: 0 14px;
        min-height: 34px;
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
        border-radius: 7px;
        min-height: 36px;
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
        border-radius: 10px;
        min-height: 48px;
        font-size: 11pt;
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
        min-height: 32px;
        min-width: 32px;
        padding: 0;
    }}

    QPushButton[variant="ghost"]:hover {{
        background-color: {t.raised};
    }}

    QPushButton[variant="success"] {{
        background-color: {t.success_bg};
        border: 1px solid {t.success_border};
        color: {t.text};
        min-height: 30px;
        padding: 0 10px;
        font-size: 9pt;
    }}

    QLineEdit, QPlainTextEdit {{
        background-color: {t.field};
        color: {t.text};
        border: 1px solid {t.border};
        border-radius: 8px;
        padding: 0 10px;
        min-height: 38px;
        selection-background-color: {t.accent};
        selection-color: {t.on_accent};
    }}

    QPlainTextEdit {{
        padding: 8px 10px;
        border-radius: 10px;
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
        border-radius: 3px;
        max-height: 6px;
        min-height: 6px;
    }}

    QProgressBar::chunk {{
        background-color: {t.accent_text};
        border-radius: 3px;
    }}

    QProgressBar[over="true"]::chunk {{
        background-color: {t.danger};
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background-color: {t.raised};
        border-radius: 4px;
        min-height: 32px;
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
    global _theme  # noqa: PLW0603
    _theme = _detect_theme()

    app.setStyle("Fusion")
    _load_bundled_fonts()
    app.setFont(app_font())
    app.setStyleSheet(global_stylesheet(_theme))


# ---------------------------------------------------------------------------
# Legacy helpers used by the previous main window; removed with it.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AccentPalette:
    base: str
    hover: str
    pressed: str


HIDE_ACCENT = AccentPalette(base="#4296FA", hover="#5AA8FB", pressed="#0F87FA")
REVEAL_ACCENT = AccentPalette(base="#4CC84B", hover="#5BD85A", pressed="#3DB83C")


def mode_button_active(palette: AccentPalette) -> str:
    return (
        f"QPushButton {{ background-color: {palette.base}; color: #FFFFFF;"
        " border: none; border-radius: 4px; padding: 6px 14px; }"
    )


def mode_button_inactive() -> str:
    return "QPushButton { border: none; border-radius: 4px; padding: 6px 14px; }"


def secondary_button() -> str:
    return mode_button_inactive()


def accent_bar(palette: AccentPalette) -> str:
    return f"border: none; border-bottom: 2px solid {palette.base};"


def separator() -> str:
    return f"background-color: {_theme.border}; border: none;"


def action_button(palette: AccentPalette) -> str:
    return (
        f"QPushButton {{ background-color: {palette.base}; color: #FFFFFF;"
        " border: none; border-radius: 4px; min-height: 34px; }"
    )
