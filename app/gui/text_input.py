from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtWidgets import QWidget


class TextInput(QPlainTextEdit):
    def __init__(self, text: str, object_name: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setPlaceholderText(text)
        self.setMinimumHeight(100)
