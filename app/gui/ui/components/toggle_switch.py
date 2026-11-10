from PyQt6.QtCore import QRectF
from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPaintEvent
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QAbstractButton
from PyQt6.QtWidgets import QWidget

from app.gui.ui import styles

_WIDTH = 32
_HEIGHT = 18
_KNOB_MARGIN = 2


class ToggleSwitch(QAbstractButton):
    """On/off switch; a checkable button, so Space and clicks toggle it."""

    def __init__(self, accessible_name: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setAccessibleName(accessible_name)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedSize(self.sizeHint())

    def sizeHint(self) -> QSize:
        return QSize(_WIDTH, _HEIGHT)

    def paintEvent(self, e: QPaintEvent | None) -> None:
        t = styles.theme()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        track = QRectF(0.5, 0.5, _WIDTH - 1, _HEIGHT - 1)
        radius = track.height() / 2
        if self.isChecked():
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(t.accent))
        else:
            painter.setPen(QPen(QColor(t.border), 1))
            painter.setBrush(QColor(t.raised))
        if not self.isEnabled():
            painter.setOpacity(0.5)
        painter.drawRoundedRect(track, radius, radius)

        knob_size = _HEIGHT - 2 * _KNOB_MARGIN
        x = _WIDTH - _KNOB_MARGIN - knob_size if self.isChecked() else _KNOB_MARGIN
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(t.on_accent if self.isChecked() else t.muted))
        painter.drawEllipse(QRectF(x, _KNOB_MARGIN, knob_size, knob_size))

        if self.hasFocus():
            painter.setOpacity(1)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(t.accent_text), 1.5))
            painter.drawRoundedRect(
                track.adjusted(-0.5, -0.5, 0.5, 0.5), radius, radius
            )
        painter.end()
