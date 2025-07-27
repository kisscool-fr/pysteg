from PyQt6.QtWidgets import QLineEdit


class ReadOnlyFileSelector(QLineEdit):
    def __init__(self, placeholder_text: str, object_name: str):
        super().__init__()
        self.setPlaceholderText(placeholder_text)
        self.setReadOnly(True)
        self.setObjectName(object_name)