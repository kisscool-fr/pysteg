from enum import StrEnum

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QRadioButton
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget
from stegano import lsb  # type: ignore
from stegano.lsb import generators  # type: ignore

from app.aes256 import Crypto
from app.constants import APP_NAME
from app.constants import APP_VERSION
from app.gui.file_selector import ReadOnlyFileSelector
from app.gui.push_button import PushButton
from app.gui.text_input import TextInput
from app.gui.text_label import TextLabel
from app.gui.text_line import TextLine


class Mode(StrEnum):
    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(QSize(300, 500))

        screen = self.screen().availableGeometry()  # pyright: ignore[reportOptionalMemberAccess]
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

        self.mode = Mode.ENCRYPT
        self.status_bar = self.statusBar()

        layout = QVBoxLayout()
        rb_layout = QHBoxLayout()

        # Radio buttons for encryption/decryptions
        rb_encrypt = QRadioButton("Encrypt")
        rb_encrypt.setChecked(True)
        rb_encrypt.clicked.connect(self.update_mode)  # type: ignore

        rb_decrypt = QRadioButton("Decrypt")
        rb_decrypt.clicked.connect(self.update_mode)  # type: ignore

        rb_layout.addWidget(rb_encrypt)
        rb_layout.addWidget(rb_decrypt)

        layout.addLayout(rb_layout)

        text_label = TextLabel("Text to hide", "mode_label")
        layout.addWidget(text_label)

        text_input = TextInput("Enter text here...", "text_input")
        layout.addWidget(text_input)

        secret_label = TextLabel("Shared secret", "secret_label")
        layout.addWidget(secret_label)

        secret_input = TextLine("", "secret_input")
        layout.addWidget(secret_input)

        image_label = TextLabel("Image file (.png only)", "image_label")
        layout.addWidget(image_label)

        file_selector = ReadOnlyFileSelector("No file selected", "file_selector")
        layout.addWidget(file_selector)

        button_file = PushButton("Choose file", "select_file_button")
        button_file.clicked.connect(self.button_choose_file)  # type: ignore
        layout.addWidget(button_file)

        button = PushButton("Hide Text", "action_button")
        button.clicked.connect(self.button_clicked)  # type: ignore
        layout.addWidget(button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def update_mode(self):
        sender = self.sender()
        if isinstance(sender, QRadioButton) and sender.isChecked():
            if sender.text() == "Encrypt":
                self.mode = Mode.ENCRYPT

                self.status_bar.showMessage("Encrypt mode selected", 2000)  # type: ignore

                self.findChild(QLabel, "mode_label").setText("Text to hide")
                self.findChild(QPlainTextEdit, "text_input").setReadOnly(False)
                self.findChild(QPushButton, "action_button").setText("Hide text")
                self.findChild(QLineEdit, "file_selector").setText("")
            elif sender.text() == "Decrypt":
                self.mode = Mode.DECRYPT

                self.status_bar.showMessage("Decrypt mode selected", 2000)  # type: ignore

                self.findChild(QLabel, "mode_label").setText("Text revealed")
                self.findChild(QPlainTextEdit, "text_input").setReadOnly(True)
                self.findChild(QPushButton, "action_button").setText("Reveal text")
                self.findChild(QLineEdit, "file_selector").setText("")

    def button_clicked(self):
        secret = self.findChild(QLineEdit, "secret_input").text()

        if len(secret.strip()) == 0:
            self.status_bar.showMessage("Secret is empty", 2000)  # type: ignore
            return

        crypto = Crypto(secret)

        if self.mode == Mode.ENCRYPT:
            text = self.findChild(QPlainTextEdit, "text_input").toPlainText()

            encrypted = crypto.encrypt(text)

            file = self.findChild(QLineEdit, "file_selector").text()
            hide = file.replace(".png", "_hidden.png")

            secret = lsb.hide(file, encrypted, generators.eratosthenes())
            secret.save(hide)

            self.status_bar.showMessage("Encryption successful", 2000)  # type: ignore
        else:
            file = self.findChild(QLineEdit, "file_selector").text()

            hide_text = lsb.reveal(file, generators.eratosthenes())

            try:
                decrypted = crypto.decrypt(hide_text)
                self.findChild(QPlainTextEdit, "text_input").setPlainText(decrypted)

                self.status_bar.showMessage("Decryption successful", 2000)  # type: ignore
            except ValueError:
                self.status_bar.showMessage("Decryption failed: Invalid data", 2000)  # type: ignore

    def button_choose_file(self):
        image_input = QFileDialog()
        image_input.setFileMode(QFileDialog.FileMode.ExistingFile)
        image_input.setNameFilter("Images (*.png)")
        # image_input.setViewMode(QFileDialog.ViewMode.List)
        image_input.setWindowTitle("Select an image file")
        if image_input.exec():
            selected_files = image_input.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                self.findChild(QLineEdit, "file_selector").setText(f"{file_path}")
                return file_path
            else:
                return None
