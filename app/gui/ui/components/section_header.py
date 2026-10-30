from typing import Literal

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QWidget

from app.gui.ui import icons
from app.gui.ui import styles

StepState = Literal["pending", "done", "error"]

_BADGE_SIZE = 16
_BADGE_ICON_SIZE = 10


class SectionHeader(QWidget):
    """Step title with a badge showing its number, a check or an alert."""

    def __init__(self, number: int, title: str, parent: QWidget | None = None):
        super().__init__(parent)
        self._number = number
        self._state: StepState | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.badge = QLabel()
        self.badge.setFixedSize(_BADGE_SIZE, _BADGE_SIZE)
        self.badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title = QLabel(title)
        self.title.setProperty("role", "section")

        layout.addWidget(self.badge)
        layout.addWidget(self.title)
        layout.addStretch()

        self.set_state("pending")

    @property
    def state(self) -> StepState | None:
        return self._state

    def set_title(self, title: str) -> None:
        self.title.setText(title)

    def set_number(self, number: int) -> None:
        self._number = number
        if self._state == "pending":
            self.badge.setText(str(number))

    def set_buddy(self, widget: QWidget) -> None:
        """Give the title's text to ``widget`` as its accessible name."""
        widget.setAccessibleName(self.title.text())

    def set_state(self, state: StepState) -> None:
        if state == self._state:
            return
        self._state = state
        t = styles.theme()
        if state == "pending":
            self.badge.clear()
            self.badge.setText(str(self._number))
        elif state == "done":
            self.badge.setPixmap(
                icons.pixmap("check", t.success, _BADGE_ICON_SIZE, stroke_width=3)
            )
        else:
            self.badge.setPixmap(
                icons.pixmap("alert", t.danger, _BADGE_ICON_SIZE, stroke_width=3)
            )
        styles.set_property(self.badge, "badge", state)
