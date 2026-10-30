from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from app.capacity import Capacity
from app.gui.ui import styles
from app.gui.ui.formatting import human_size

_SCALE = 1000


class CapacityMeter(QWidget):
    """How much of the cover image the (encrypted) message uses."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        self.bar = QProgressBar()
        self.bar.setRange(0, _SCALE)
        self.bar.setTextVisible(False)
        self.bar.setAccessibleName("Capacity used")

        labels = QHBoxLayout()
        self.caption = QLabel("Capacity")
        self.usage = QLabel()
        for label in (self.caption, self.usage):
            label.setProperty("role", "hint")
        labels.addWidget(self.caption)
        labels.addStretch()
        labels.addWidget(self.usage)

        layout.addWidget(self.bar)
        layout.addLayout(labels)

    def set_capacity(self, capacity: Capacity) -> None:
        over = not capacity.fits
        self.bar.setValue(min(round(capacity.ratio * _SCALE), _SCALE))
        styles.set_property(self.bar, "over", over)

        role = "error" if over else "hint"
        self.caption.setText("Too long for this image" if over else "Capacity")
        used, available = human_size(capacity.used), human_size(capacity.available)
        self.usage.setText(
            f"{used} of {available}" if over else f"{used} of {available} used"
        )
        for label in (self.caption, self.usage):
            styles.set_property(label, "role", role)
