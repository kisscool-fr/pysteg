from functools import partial

from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QButtonGroup
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QWidget

from app.gui.models.mode import Mode
from app.gui.ui import icons
from app.gui.ui import styles

_SEGMENTS = ((Mode.HIDE, "Hide", "lock"), (Mode.REVEAL, "Reveal", "unlock"))


class ModeSwitch(QFrame):
    """Segmented Hide / Reveal control."""

    mode_changed = pyqtSignal(Mode)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("segmented")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[Mode, QPushButton] = {}

        for mode, label, _ in _SEGMENTS:
            button = QPushButton(label)
            button.setObjectName(f"mode_{mode}")
            button.setProperty("variant", "segment")
            button.setCheckable(True)
            button.setIconSize(QSize(16, 16))
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.toggled.connect(partial(self._on_toggled, mode))  # pyright: ignore[reportUnknownMemberType]
            self._group.addButton(button)
            self._buttons[mode] = button
            layout.addWidget(button)

        self._buttons[Mode.HIDE].setChecked(True)
        self._refresh_icons()

    def button(self, mode: Mode) -> QPushButton:
        return self._buttons[mode]

    def mode(self) -> Mode:
        return Mode.HIDE if self._buttons[Mode.HIDE].isChecked() else Mode.REVEAL

    def set_mode(self, mode: Mode) -> None:
        self._buttons[mode].setChecked(True)

    def _on_toggled(self, mode: Mode, checked: bool) -> None:
        self._refresh_icons()
        if checked:
            self.mode_changed.emit(mode)

    def _refresh_icons(self) -> None:
        t = styles.theme()
        for mode, _, icon_name in _SEGMENTS:
            button = self._buttons[mode]
            color = t.accent_text if button.isChecked() else t.muted
            button.setIcon(icons.icon(icon_name, color))
