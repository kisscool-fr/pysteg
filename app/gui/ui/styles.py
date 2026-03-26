from dataclasses import dataclass


@dataclass(frozen=True)
class AccentPalette:
    base: str
    hover: str
    pressed: str


HIDE_ACCENT = AccentPalette(base="#3B82F6", hover="#2563EB", pressed="#1D4ED8")
REVEAL_ACCENT = AccentPalette(base="#F59E0B", hover="#D97706", pressed="#B45309")

_INACTIVE_BG = "#E5E7EB"
_INACTIVE_HOVER = "#D1D5DB"
_INACTIVE_TEXT = "#374151"


def mode_button_active(palette: AccentPalette) -> str:
    return (
        "QPushButton {"
        f"  background-color: {palette.base};"
        "  color: #FFFFFF;"
        "  border: none;"
        "  border-radius: 6px;"
        "  padding: 6px 14px;"
        "  font-weight: 600;"
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
        f"  background-color: {_INACTIVE_BG};"
        f"  color: {_INACTIVE_TEXT};"
        "  border: none;"
        "  border-radius: 6px;"
        "  padding: 6px 14px;"
        "  font-weight: 400;"
        "}"
        "QPushButton:hover {"
        f"  background-color: {_INACTIVE_HOVER};"
        "}"
    )


def accent_bar(palette: AccentPalette) -> str:
    return f"background-color: {palette.base}; border: none;"


def action_button(palette: AccentPalette) -> str:
    return (
        "QPushButton {"
        f"  background-color: {palette.base};"
        "  color: #FFFFFF;"
        "  border: none;"
        "  border-radius: 6px;"
        "  padding: 8px 16px;"
        "  font-weight: 600;"
        "}"
        "QPushButton:hover {"
        f"  background-color: {palette.hover};"
        "}"
        "QPushButton:pressed {"
        f"  background-color: {palette.pressed};"
        "}"
    )
