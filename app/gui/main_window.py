import gettext
from enum import StrEnum
from enum import auto

from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtWidgets import QPushButton
from stegano import lsb  # type: ignore
from stegano.lsb import generators  # type: ignore

from app.aes256 import Crypto
from app.constants import APP_NAME
from app.constants import ICON_LOCK
from app.constants import ICON_UNLOCK
from app.gui.controllers.actions import ActionController
from app.gui.models.mode import WindowModel
from app.gui.ui.components.push_button import PushButton
from app.gui.ui.main_window_ui import MainWindowUI
from app.gui.validators.input import InputValidator

gettext.bindtextdomain(APP_NAME, "locales")
gettext.textdomain(APP_NAME)
_ = gettext.gettext


class Mode(StrEnum):
    ENCRYPT = auto()
    DECRYPT = auto()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.model = WindowModel()
        self.controller = ActionController(self.model)
        self.ui = MainWindowUI()

        self.ui.setup_ui(self)
        self.ui.center_window(self)

        self._connect_signals()

    def _connect_signals(self):
        self.ui.rb_encrypt.clicked.connect(self._handle_mode_change)  # pyright: ignore[reportUnknownMemberType]
        self.ui.rb_decrypt.clicked.connect(self._handle_mode_change)  # pyright: ignore[reportUnknownMemberType]
        self.ui.button_file.clicked.connect(self._handle_file_selection)  # pyright: ignore[reportUnknownMemberType]
        self.ui.action_button.clicked.connect(self._handle_action)  # pyright: ignore[reportUnknownMemberType]

    def _handle_mode_change(self):
        sender = self.sender()

        if isinstance(sender, PushButton):
            if sender.objectName() == Mode.ENCRYPT:
                self.mode = Mode.ENCRYPT

                self.status_bar.showMessage("Hide mode selected", 2000)  # type: ignore

                self.findChild(QLabel, "mode_label").setText("Text to hide")
                self.findChild(QPlainTextEdit, "text_input").setReadOnly(False)
                self.findChild(QPushButton, "action_button").setText(
                    f"{ICON_LOCK} Hide text"
                )
                self.findChild(QLineEdit, "file_selector").setText("")
            elif sender.objectName() == Mode.DECRYPT:
                self.mode = Mode.DECRYPT

                self.status_bar.showMessage("Reveal mode selected", 2000)  # type: ignore

                self.findChild(QLabel, "mode_label").setText("Text revealed")
                self.findChild(QPlainTextEdit, "text_input").setReadOnly(True)
                self.findChild(QPushButton, "action_button").setText(
                    f"{ICON_UNLOCK} Reveal text"
                )
                self.findChild(QLineEdit, "file_selector").setText("")

    def _handle_action(self):
        secret = self.findChild(QLineEdit, "secret_input").text()
        secret_valid, secret_status = InputValidator.validate_secret(secret)

        if not secret_valid:
            self.status_bar.showMessage(secret_status, 2000)  # type: ignore
            return

        crypto = Crypto(secret)

        try:
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
        except AttributeError:
            self.status_bar.showMessage("Please choose a working mode", 2000)  # type: ignore
        except FileNotFoundError:
            self.status_bar.showMessage("Please choose a file", 2000)  # type: ignore

    def _handle_file_selection(self):
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
