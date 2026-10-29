from typing import Literal

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QWidget

from app.gui.ui import icons
from app.gui.ui import styles

CalloutKind = Literal["warning", "error"]


class Callout(QFrame):
    """Inline banner with an icon, used instead of modal dialogs."""

    def __init__(self, kind: CalloutKind, text: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setProperty("callout", kind)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        t = styles.theme()
        color = t.warning if kind == "warning" else t.danger
        icon_name = "warning" if kind == "warning" else "alert_circle"
        icon = QLabel()
        icon.setPixmap(icons.pixmap(icon_name, color))
        icon.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.label = QLabel(text)
        self.label.setWordWrap(True)

        layout.addWidget(icon)
        layout.addWidget(self.label, 1)

    def set_text(self, text: str) -> None:
        self.label.setText(text)
