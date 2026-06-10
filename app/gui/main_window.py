import gettext
from pathlib import Path

from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QMessageBox

from app.constants import APP_NAME
from app.constants import ICON_LOCK
from app.constants import ICON_UNLOCK
from app.gui.controllers.actions import ActionController
from app.gui.models.mode import Mode
from app.gui.models.mode import WindowModel
from app.gui.ui.components.push_button import PushButton
from app.gui.ui.main_window_ui import MainWindowUI
from app.gui.validators.input import InputValidator
from app.payload import extract_payload
from app.payload import prepare_payload

gettext.bindtextdomain(APP_NAME, "locales")
gettext.textdomain(APP_NAME)
_ = gettext.gettext


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.model = WindowModel()
        self.mode = Mode.ENCRYPT
        self.controller = ActionController(self.model)
        self.ui = MainWindowUI()

        self.ui.setup_ui(self)
        self.ui.center_window(self)

        self._connect_signals()
        self._apply_mode(Mode.ENCRYPT, notify=False)

    def _connect_signals(self):
        self.ui.rb_encrypt.clicked.connect(self._handle_mode_change)  # pyright: ignore[reportUnknownMemberType]
        self.ui.rb_decrypt.clicked.connect(self._handle_mode_change)  # pyright: ignore[reportUnknownMemberType]
        self.ui.button_file.clicked.connect(self._handle_file_selection)  # pyright: ignore[reportUnknownMemberType]
        self.ui.action_button.clicked.connect(self._handle_action)  # pyright: ignore[reportUnknownMemberType]
        self.ui.plain_text_checkbox.toggled.connect(self._handle_plain_text_toggle)  # pyright: ignore[reportUnknownMemberType]

    def _handle_plain_text_toggle(self, checked: bool):
        if checked and self.mode == Mode.ENCRYPT:
            message = QMessageBox(self)
            message.setIcon(QMessageBox.Icon.NoIcon)
            message.setWindowTitle("Plain text mode")
            message.setText(
                "Your text will be hidden without encryption. "
                "Anyone who extracts the hidden data can read it in plain text. "
                "Use a shared secret unless you accept this risk."
            )
            message.setStandardButtons(QMessageBox.StandardButton.Ok)
            message.exec()
            self.ui.secret_input.clear()

        self.ui.secret_input.setEnabled(not checked)

    def _handle_mode_change(self):
        sender = self.sender()

        if isinstance(sender, PushButton):
            if sender.objectName() == Mode.ENCRYPT:
                self._apply_mode(Mode.ENCRYPT)
            elif sender.objectName() == Mode.DECRYPT:
                self._apply_mode(Mode.DECRYPT)

    def _apply_mode(self, mode: Mode, *, notify: bool = True):
        self.mode = mode
        self.model.mode = mode

        if mode == Mode.ENCRYPT:
            if notify:
                self.status_bar.showMessage("Hide mode selected", 2000)  # type: ignore

            self.ui.mode_label.setText("Text to hide")
            self.ui.text_input.setReadOnly(False)
            self.ui.action_button.setText(f"{ICON_LOCK} Hide text")
        else:
            if notify:
                self.status_bar.showMessage("Reveal mode selected", 2000)  # type: ignore

            self.ui.mode_label.setText("Text revealed")
            self.ui.text_input.setReadOnly(True)
            self.ui.action_button.setText(f"{ICON_UNLOCK} Reveal text")

        self.ui.text_input.setPlainText("")
        self.ui.file_selector.setText("")
        self.ui.secret_input.clear()
        self.ui.plain_text_checkbox.setChecked(False)
        self.ui.apply_mode_style(mode)

    def _handle_action(self):
        plain_text = self.ui.plain_text_checkbox.isChecked()

        if not plain_text:
            secret_valid, secret_status = InputValidator.validate_secret(
                self.ui.secret_input.text()
            )

            if not secret_valid:
                self.status_bar.showMessage(secret_status, 2000)  # type: ignore
                return

        try:
            if self.mode == Mode.ENCRYPT:
                text = self.ui.text_input.toPlainText()
                payload = prepare_payload(
                    text, self.ui.secret_input.text(), plain_text=plain_text
                )

                filename = self.ui.file_selector.text()
                p = Path(filename)
                hidename = str(p.with_stem(p.stem + "_hidden"))

                try:
                    _, status = self.controller.hide(
                        source=filename,
                        destination=hidename,
                        text=payload,
                        plain_text=plain_text,
                    )
                    self.status_bar.showMessage(status, 2000)  # type: ignore
                except (IndexError, OverflowError, ValueError):
                    self.status_bar.showMessage(  # type: ignore
                        "Hide failed: message too large for this image", 2000
                    )
                except OSError:
                    self.status_bar.showMessage(  # type: ignore
                        "Hide failed: could not write output file", 2000
                    )
            else:
                filename = self.ui.file_selector.text()

                try:
                    hide_text = self.controller.reveal(source=filename)[1]

                    result = extract_payload(
                        hide_text, self.ui.secret_input.text(), plain_text=plain_text
                    )
                    self.ui.text_input.setPlainText(result)

                    status = (
                        "Text revealed successfully"
                        if plain_text
                        else "Decryption successful"
                    )
                    self.status_bar.showMessage(status, 2000)  # type: ignore
                except IndexError:
                    self.status_bar.showMessage(  # type: ignore
                        "Reveal failed: No hidden text found", 2000
                    )
                except ValueError:
                    failure = (
                        "Reveal failed: Invalid data"
                        if plain_text
                        else "Decryption failed: Invalid data"
                    )
                    self.status_bar.showMessage(failure, 2000)  # type: ignore
        except AttributeError:
            self.status_bar.showMessage("Please choose a working mode", 2000)  # type: ignore
        except FileNotFoundError:
            self.status_bar.showMessage("Please choose a file", 2000)  # type: ignore

    def _handle_file_selection(self):
        image_input = QFileDialog()
        image_input.setFileMode(QFileDialog.FileMode.ExistingFile)
        image_input.setNameFilters(  # type: ignore
            [
                "All Images (*.png *.jpg *.jpeg *.bmp)",
                "PNG Files (*.png)",
                "JPEG Files (*.jpg *.jpeg)",
                "BMP Files (*.bmp)",
                "TIFF Files (*.tiff *.tif)",
            ]
        )
        # image_input.setViewMode(QFileDialog.ViewMode.List)
        image_input.setWindowTitle("Select an image file")
        if image_input.exec():
            selected_files = image_input.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                self.ui.file_selector.setText(file_path)
                return file_path
            else:
                return None
