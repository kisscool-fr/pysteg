from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QWidget


class TextLine(QLineEdit):
    def __init__(self, text: str, object_name: str, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setObjectName(object_name)
