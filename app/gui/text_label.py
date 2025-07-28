from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QWidget


class TextLabel(QLabel):
    def __init__(self, text: str, object_name: str, parent: QWidget | None = None):
        super().__init__(text, parent)

        self.setObjectName(object_name)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        font = self.font()
        font.setPointSize(10)
        self.setFont(font)
