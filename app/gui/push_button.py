
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QWidget


class PushButton(QPushButton):
    def __init__(self, text: str, object_name: str, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setObjectName(object_name)

    def connect(self, slot):  # type: ignore
        super().clicked.connect(slot)  # type: ignore
