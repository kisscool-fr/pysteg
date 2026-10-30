import gettext
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtGui import QKeySequence
from PyQt6.QtGui import QShortcut
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QMainWindow

from app.capacity import Capacity
from app.capacity import available_bytes
from app.capacity import payload_bytes
from app.constants import APP_NAME
from app.constants import SHARED_SECRET_MIN_LENGTH
from app.gui.controllers.actions import ActionController
from app.gui.controllers.actions import Hiding
from app.gui.controllers.actions import ImageInfo
from app.gui.models.mode import Mode
from app.gui.models.mode import WindowModel
from app.gui.ui import icons
from app.gui.ui import styles
from app.gui.ui.components.image_card import THUMBNAIL_SIZE
from app.gui.ui.formatting import human_size
from app.gui.ui.formatting import plural
from app.gui.ui.main_window_ui import FORM_PAGE
from app.gui.ui.main_window_ui import RESULT_PAGE
from app.gui.ui.main_window_ui import MainWindowUI
from app.gui.validators.input import InputValidator
from app.payload import estimate_payload
from app.payload import extract_payload
from app.payload import prepare_payload

gettext.bindtextdomain(APP_NAME, str(Path(__file__).parent.parent.parent / "locales"))
gettext.textdomain(APP_NAME)
_ = gettext.gettext

IMAGE_FILTERS = [
    "All Images (*.png *.bmp *.jpg *.jpeg *.tif *.tiff)",
    "PNG Files (*.png)",
    "BMP Files (*.bmp)",
    "JPEG Files (*.jpg *.jpeg)",
    "TIFF Files (*.tif *.tiff)",
]

# stegano.exifHeader.reveal leaks raw zlib / piexif errors on images that
# carry no message (see tests/test_untrusted_images.py).
_NO_MESSAGE_ERRORS = (IndexError, KeyError, zlib.error)

_RESULT_FOLDER_WIDTH = 160


def show_folder_label() -> str:
    if sys.platform == "darwin":
        return "Show in Finder"
    if sys.platform == "win32":
        return "Show in Explorer"
    return "Open folder"


def shortcut_hint() -> str:
    return "⌘ + Return" if sys.platform == "darwin" else "Ctrl + Enter"


@dataclass
class _Check:
    """Outcome of validating the form for the current mode."""

    image_ok: bool = False
    message_ok: bool = False
    protection_ok: bool = False
    output_ok: bool = False
    blocker: str = ""

    def block(self, reason: str) -> None:
        if not self.blocker:
            self.blocker = reason


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.model = WindowModel()
        self.controller = ActionController(self.model)
        self.ui = MainWindowUI()

        self._info: ImageInfo | None = None
        self._available = 0
        self._image_error = ""
        self._image_notice = ""
        self._reveal_failed = False
        self._last_output: ImageInfo | None = None
        self._output_destination = ""

        self.ui.setup_ui(self)
        self.ui.center_window(self)
        self.ui.show_folder_button.setText(show_folder_label())

        self._connect_signals()
        self._apply_mode(Mode.HIDE)
        self.ui.image_card.browse_button.setFocus()

    # -- wiring ----------------------------------------------------------------

    def _connect_signals(self):
        ui = self.ui
        ui.mode_switch.mode_changed.connect(self._apply_mode)  # pyright: ignore[reportUnknownMemberType]
        ui.image_card.browse_requested.connect(self._browse_image)  # pyright: ignore[reportUnknownMemberType]
        ui.image_card.file_dropped.connect(self.load_image)  # pyright: ignore[reportUnknownMemberType]
        ui.image_card.cleared.connect(self._on_image_cleared)  # pyright: ignore[reportUnknownMemberType]
        ui.message_input.textChanged.connect(self._refresh)  # pyright: ignore[reportUnknownMemberType]
        ui.encrypt_toggle.toggled.connect(self._on_encrypt_toggled)  # pyright: ignore[reportUnknownMemberType]
        ui.secret_input.textChanged.connect(self._on_secret_edited)  # pyright: ignore[reportUnknownMemberType]
        ui.confirm_input.textChanged.connect(self._refresh)  # pyright: ignore[reportUnknownMemberType]
        if ui.secret_input.visibility_action is not None:
            ui.secret_input.visibility_action.toggled.connect(  # pyright: ignore[reportUnknownMemberType]
                ui.confirm_input.set_revealed
            )
        ui.output_input.textChanged.connect(self._refresh)  # pyright: ignore[reportUnknownMemberType]
        ui.change_output_button.clicked.connect(self._choose_output)  # pyright: ignore[reportUnknownMemberType]
        ui.action_button.clicked.connect(self.run_action)  # pyright: ignore[reportUnknownMemberType]
        ui.copy_text_button.clicked.connect(self._copy_revealed_text)  # pyright: ignore[reportUnknownMemberType]
        ui.save_text_button.clicked.connect(self._save_revealed_text)  # pyright: ignore[reportUnknownMemberType]
        ui.copy_path_button.clicked.connect(self._copy_output_path)  # pyright: ignore[reportUnknownMemberType]
        ui.show_folder_button.clicked.connect(self._show_output_folder)  # pyright: ignore[reportUnknownMemberType]
        ui.test_reveal_button.clicked.connect(self._test_with_reveal)  # pyright: ignore[reportUnknownMemberType]
        ui.hide_another_button.clicked.connect(self._hide_another)  # pyright: ignore[reportUnknownMemberType]

        # Qt maps Ctrl to ⌘ on macOS.
        for keys in ("Ctrl+Return", "Ctrl+Enter"):
            shortcut = QShortcut(QKeySequence(keys), self)
            shortcut.activated.connect(self.run_action)  # pyright: ignore[reportUnknownMemberType]

    # -- mode ------------------------------------------------------------------

    def _apply_mode(self, mode: Mode):
        """Switch mode, keeping the image and clearing mode-specific fields."""
        ui = self.ui
        self.model.mode = mode
        hide = mode == Mode.HIDE

        if ui.mode_switch.mode() != mode:
            ui.mode_switch.set_mode(mode)
        ui.pages.setCurrentIndex(FORM_PAGE)

        ui.message_input.blockSignals(True)
        ui.message_input.clear()
        ui.message_input.blockSignals(False)
        for field in (ui.secret_input, ui.confirm_input):
            field.blockSignals(True)
            field.clear()
            field.blockSignals(False)
        ui.encrypt_toggle.blockSignals(True)
        ui.encrypt_toggle.setChecked(True)
        ui.encrypt_toggle.blockSignals(False)
        ui.revealed_text.clear()
        self._reveal_failed = False
        self._image_notice = ""

        ui.image_header.set_title(
            "Cover image" if hide else "Image with a hidden message"
        )
        ui.protection_header.set_number(3 if hide else 2)
        ui.encrypt_title.setText(
            "Encrypt with a shared secret" if hide else "Message is encrypted"
        )
        ui.encrypt_toggle.setAccessibleName(ui.encrypt_title.text())
        ui.message_section.setVisible(hide)
        ui.output_section.setVisible(hide)
        ui.encrypt_subtitle.setVisible(hide)

        self._fill_default_output()
        self._refresh()

    # -- image -----------------------------------------------------------------

    def _browse_image(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilters(IMAGE_FILTERS)  # type: ignore
        dialog.setWindowTitle("Select an image file")
        if dialog.exec():
            files = dialog.selectedFiles()
            if files:
                self.load_image(files[0])

    def load_image(self, path: str):
        try:
            info = self.controller.inspect(path)
        except (OSError, ValueError, Image.DecompressionBombError):
            self._set_image(None, "This file isn't an image PySteg can read.")
            return

        if not info.supported:
            self._set_image(info, "Unsupported format. Use PNG, BMP, JPEG or TIFF.")
        elif not info.within_size_limit:
            self._set_image(info, "This image is too large to process.")
        else:
            self._set_image(info, "")

    def _set_image(self, info: ImageInfo | None, error: str):
        ui = self.ui
        self._info = info
        self._image_error = error
        self._image_notice = ""
        self._reveal_failed = False
        ui.revealed_text.clear()

        if info is None:
            ui.image_card.blockSignals(True)
            ui.image_card.clear()
            ui.image_card.blockSignals(False)
            self._available = 0
        else:
            ui.image_card.set_image(info)
            self._available = available_bytes(info) if not error else 0

        self._fill_default_output()
        self._refresh()

    def _on_image_cleared(self):
        self._set_image(None, "")

    def _fill_default_output(self):
        info = self._info
        if info is None or self.model.mode != Mode.HIDE:
            self.ui.output_input.clear()
            return
        path = Path(info.path)
        self.ui.output_input.setText(str(path.with_stem(path.stem + "_hidden")))

    def _choose_output(self):
        current = self.ui.output_input.text().strip()
        path, _selected = QFileDialog.getSaveFileName(
            self, "Save the image as", current, ";;".join(IMAGE_FILTERS)
        )
        if path:
            self.ui.output_input.setText(path)

    # -- protection ------------------------------------------------------------

    def _on_encrypt_toggled(self, _checked: bool):
        self._reveal_failed = False
        for field in (self.ui.secret_input, self.ui.confirm_input):
            field.clear()
        self._refresh()

    def _on_secret_edited(self):
        self._reveal_failed = False
        self._refresh()

    # -- validation ------------------------------------------------------------

    def _refresh(self):
        """Recompute every step's state, inline messages and the action button."""
        hide = self.model.mode == Mode.HIDE
        check = _Check()

        self._refresh_image(check)
        if hide:
            self._refresh_message(check)
        else:
            self.ui.capacity_meter.hide()
        self._refresh_protection(check, hide=hide)
        if hide:
            self._refresh_output(check)
        self._refresh_action(check, hide=hide)
        self._refresh_reveal_panels(hide=hide)

    def _set_message(self, label: QLabel, text: str, role: str = "error"):
        label.setText(text)
        label.setVisible(bool(text))
        styles.set_property(label, "role", role)

    def _refresh_image(self, check: _Check):
        ui = self.ui
        info = self._info
        check.image_ok = info is not None and not self._image_error

        if self._image_error:
            ui.image_header.set_state("error")
            check.block("Choose a supported image to continue")
        elif info is None:
            ui.image_header.set_state("pending")
            check.block("Add a cover image to continue")
        else:
            ui.image_header.set_state("done")

        self._set_message(ui.image_error, self._image_error or self._image_notice)
        ui.image_note.setVisible(
            check.image_ok and info is not None and info.technique == Hiding.EXIF
        )

    def _capacity(self, text: str) -> Capacity | None:
        info = self._info
        if info is None or self._image_error:
            return None
        payload = estimate_payload(
            text, plain_text=not self.ui.encrypt_toggle.isChecked()
        )
        return Capacity(
            used=payload_bytes(info.technique, payload), available=self._available
        )

    def _refresh_message(self, check: _Check):
        ui = self.ui
        text = ui.message_input.toPlainText()
        ui.message_counter.setText(plural(len(text), "character"))

        capacity = self._capacity(text)
        ui.capacity_meter.setVisible(capacity is not None)
        if capacity is not None:
            ui.capacity_meter.set_capacity(capacity)

        error = ""
        if capacity is not None and not capacity.fits:
            tip = (
                "use a PNG cover image"
                if self._info is not None and self._info.technique == Hiding.EXIF
                else "use a larger image"
            )
            error = f"Shorten the message, or {tip}."
            check.block("Shorten the message to continue")
        elif not text:
            check.block("Write a message to continue")

        check.message_ok = bool(text) and not error
        styles.set_property(ui.message_input, "invalid", bool(error))
        self._set_message(ui.message_error, error)
        ui.message_header.set_state(
            "error" if error else ("done" if check.message_ok else "pending")
        )

    def _refresh_protection(self, check: _Check, *, hide: bool):
        ui = self.ui
        encrypt = ui.encrypt_toggle.isChecked()
        secret = ui.secret_input.text()
        confirm = ui.confirm_input.text()

        ui.plain_warning.setVisible(hide and not encrypt)
        for widget in (ui.secret_label, ui.secret_input):
            widget.setVisible(encrypt)
        for widget in (ui.confirm_label, ui.confirm_input):
            widget.setVisible(encrypt and hide)

        status, role, error = "", "hint", False
        if not encrypt:
            check.protection_ok = True
        else:
            secret_ok, _reason = InputValidator.validate_secret(secret)
            confirm_ok, _reason = InputValidator.validate_confirmation(secret, confirm)
            if self._reveal_failed:
                status, role, error = (
                    "This secret doesn't unlock the message. "
                    "Check spelling and capitals, then try again.",
                    "error",
                    True,
                )
            elif not secret_ok:
                status = (
                    f"At least {SHARED_SECRET_MIN_LENGTH} characters"
                    if not secret
                    else f"{plural(len(secret), 'character')} · "
                    f"at least {SHARED_SECRET_MIN_LENGTH}"
                )
                check.block("Enter a shared secret to continue")
            elif hide and not confirm:
                status = "Type the secret again to confirm it"
                check.block("Confirm the shared secret to continue")
            elif hide and not confirm_ok:
                status, role, error = "Secrets don't match", "error", True
                check.block("Confirm the shared secret to continue")
            elif hide:
                status, role = (
                    f"{plural(len(secret), 'character')} · secrets match",
                    "success",
                )
            check.protection_ok = secret_ok and (confirm_ok or not hide)

        self._set_message(ui.secret_status, status, role)
        styles.set_property(ui.secret_input, "invalid", self._reveal_failed)
        styles.set_property(ui.confirm_input, "invalid", error and hide)
        ui.protection_header.set_state(
            "error" if error else ("done" if check.protection_ok else "pending")
        )

    def _refresh_output(self, check: _Check):
        ui = self.ui
        destination = ui.output_input.text().strip()
        error = ""
        if self._info is not None and destination:
            ok, error = InputValidator.validate_output_file(
                self._info.path, destination
            )
            check.output_ok = ok
        if not check.output_ok:
            check.block("Choose where to save the image")

        styles.set_property(ui.output_input, "invalid", bool(error))
        self._set_message(ui.output_error, error)
        ui.output_header.set_state(
            "error" if error else ("done" if check.output_ok else "pending")
        )

    def _refresh_action(self, check: _Check, *, hide: bool):
        ui = self.ui
        t = styles.theme()
        encrypt = ui.encrypt_toggle.isChecked()

        if hide:
            ready = (
                check.image_ok
                and check.message_ok
                and check.protection_ok
                and check.output_ok
            )
            label, icon_name = (
                ("Hide message", "lock") if encrypt else ("Hide as plain text", "eye")
            )
        else:
            ready = check.image_ok and check.protection_ok
            label = "Try again" if self._reveal_failed else "Reveal message"
            icon_name = "unlock"

        ui.action_button.setEnabled(ready)
        ui.action_button.setText(label)
        ui.action_button.setIcon(
            icons.icon(icon_name, t.on_accent if ready else t.muted, 14)
        )
        ui.action_hint.setText(shortcut_hint() if ready else check.blocker)

    def _refresh_reveal_panels(self, *, hide: bool):
        ui = self.ui
        ui.reveal_result.setVisible(not hide and bool(ui.revealed_text.toPlainText()))
        ui.reveal_help.setVisible(not hide and self._reveal_failed)

    # -- actions ---------------------------------------------------------------

    def run_action(self):
        if (
            not self.ui.action_button.isEnabled()
            or self.ui.pages.currentIndex() != FORM_PAGE
        ):
            return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            if self.model.mode == Mode.HIDE:
                self._hide()
            else:
                self._reveal()
        finally:
            QApplication.restoreOverrideCursor()

    def _hide(self):
        ui = self.ui
        info = self._info
        if info is None:
            return
        encrypt = ui.encrypt_toggle.isChecked()
        destination = ui.output_input.text().strip()
        payload = prepare_payload(
            ui.message_input.toPlainText(),
            ui.secret_input.text(),
            plain_text=not encrypt,
        )

        try:
            ok, status = self.controller.hide(
                source=info.path,
                destination=destination,
                text=payload,
                plain_text=not encrypt,
            )
        except (IndexError, OverflowError, ValueError):
            self._set_message(
                ui.message_error, "The message doesn't fit in this image."
            )
            return
        except OSError:
            self._set_message(ui.output_error, "Couldn't write the output file.")
            return

        if not ok:
            self._image_notice = status
            self._refresh()
            return

        try:
            output = self.controller.inspect(destination)
        except (OSError, ValueError):
            output = None
        self._show_hide_result(destination, output, encrypted=encrypt)

    def _reveal(self):
        ui = self.ui
        info = self._info
        if info is None:
            return
        encrypt = ui.encrypt_toggle.isChecked()

        try:
            ok, hidden = self.controller.reveal(source=info.path)
        except _NO_MESSAGE_ERRORS:
            ok, hidden = False, "No hidden message found in this image."
        except OSError:
            ok, hidden = False, "Couldn't read this image."
        if not ok:
            self._image_notice = hidden
            self._refresh()
            return

        try:
            text = extract_payload(
                hidden, ui.secret_input.text(), plain_text=not encrypt
            )
        except ValueError:
            ui.revealed_text.clear()
            self._reveal_failed = encrypt
            if not encrypt:
                self._image_notice = "The hidden data is unreadable."
            self._refresh()
            return

        self._reveal_failed = False
        self._image_notice = ""
        ui.revealed_text.setPlainText(text)
        ui.reveal_status.setText(
            ("Decrypted" if encrypt else "Revealed")
            + f" · {plural(len(text), 'character')}"
        )
        self._refresh()
        ui.scroll.ensureWidgetVisible(ui.reveal_result)

    def _show_hide_result(
        self, destination: str, output: ImageInfo | None, *, encrypted: bool
    ):
        ui = self.ui
        t = styles.theme()
        self._last_output = output
        path = Path(destination)

        ui.result_description.setText(
            "Encrypted with your shared secret and written into a new image. "
            "Send the secret through a different channel."
            if encrypted
            else "Written into a new image as plain text. Anyone who extracts it "
            "can read it."
        )
        ui.result_name.setText(path.name)
        ui.result_name.setToolTip(str(path))
        size = f" · {human_size(output.file_size)}" if output is not None else ""
        folder = ui.result_meta.fontMetrics().elidedText(
            str(path.parent), Qt.TextElideMode.ElideMiddle, _RESULT_FOLDER_WIDTH
        )
        ui.result_meta.setText(f"{folder}{size}")
        ui.result_meta.setToolTip(str(path.parent))
        ui.result_thumbnail.setPixmap(
            icons.pixmap("image", t.muted, THUMBNAIL_SIZE // 2 - 6, 1.75)
        )
        self._output_destination = str(path)
        ui.test_reveal_button.setEnabled(output is not None)
        ui.pages.setCurrentIndex(RESULT_PAGE)

    def _copy_output_path(self):
        clipboard = QGuiApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(self._output_destination)

    def _show_output_folder(self):
        folder = Path(self._output_destination).parent
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def _test_with_reveal(self):
        output = self._last_output
        self._apply_mode(Mode.REVEAL)
        if output is not None:
            self.load_image(output.path)

    def _hide_another(self):
        self._set_image(None, "")
        self._apply_mode(Mode.HIDE)

    def _copy_revealed_text(self):
        clipboard = QGuiApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(self.ui.revealed_text.toPlainText())

    def _save_revealed_text(self):
        default = ""
        if self._info is not None:
            default = str(Path(self._info.path).with_suffix(".txt"))
        path, _selected = QFileDialog.getSaveFileName(
            self, "Save the message as", default, "Text Files (*.txt)"
        )
        if not path:
            return
        try:
            Path(path).write_text(self.ui.revealed_text.toPlainText(), encoding="utf-8")
        except OSError:
            self._set_message(self.ui.image_error, "Couldn't save the text file.")
