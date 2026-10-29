from pathlib import Path

import pytest
from PIL import Image
from PyQt6.QtWidgets import QApplication

from app.gui.main_window import MainWindow
from app.gui.models.mode import Mode
from app.gui.ui import styles
from app.gui.ui.main_window_ui import FORM_PAGE
from app.gui.ui.main_window_ui import RESULT_PAGE

FIXTURES = Path(__file__).parent / "fixtures"
SECRET = "harbour-key-2"
MESSAGE = "Meet at the old harbour on Friday."


@pytest.fixture
def window(qapp: QApplication) -> MainWindow:
    styles.apply_app_theme(qapp)
    return MainWindow()


@pytest.fixture
def cover(tmp_path: Path) -> Path:
    path = tmp_path / "cover.png"
    Image.new("RGB", (128, 128), color=(40, 80, 120)).save(path)
    return path


def _fill_hide_form(window: MainWindow, cover: Path, *, encrypt: bool = True) -> None:
    ui = window.ui
    window.load_image(str(cover))
    ui.message_input.setPlainText(MESSAGE)
    ui.encrypt_toggle.setChecked(encrypt)
    if encrypt:
        ui.secret_input.setText(SECRET)
        ui.confirm_input.setText(SECRET)


class TestInitialState:
    def test_starts_in_hide_mode_with_action_disabled(self, window: MainWindow) -> None:
        ui = window.ui
        assert window.model.mode == Mode.HIDE
        assert not ui.action_button.isEnabled()
        assert ui.action_hint.text() == "Add a cover image to continue"
        assert ui.image_header.state == "pending"


class TestHideValidation:
    def test_complete_form_enables_action(
        self, window: MainWindow, cover: Path
    ) -> None:
        _fill_hide_form(window, cover)
        ui = window.ui
        assert ui.action_button.isEnabled()
        assert ui.output_input.text().endswith("cover_hidden.png")
        assert ui.secret_status.text().endswith("secrets match")
        for header in (
            ui.image_header,
            ui.message_header,
            ui.protection_header,
            ui.output_header,
        ):
            assert header.state == "done"

    def test_mismatching_confirmation_blocks(
        self, window: MainWindow, cover: Path
    ) -> None:
        _fill_hide_form(window, cover)
        window.ui.confirm_input.setText(SECRET + "x")
        assert not window.ui.action_button.isEnabled()
        assert window.ui.protection_header.state == "error"

    def test_short_secret_blocks(self, window: MainWindow, cover: Path) -> None:
        _fill_hide_form(window, cover)
        window.ui.secret_input.setText("short")
        window.ui.confirm_input.setText("short")
        assert not window.ui.action_button.isEnabled()
        assert window.ui.action_hint.text() == "Enter a shared secret to continue"

    def test_plain_text_shows_warning_and_skips_secret(
        self, window: MainWindow, cover: Path
    ) -> None:
        _fill_hide_form(window, cover, encrypt=False)
        ui = window.ui
        assert not ui.plain_warning.isHidden()
        assert ui.secret_input.isHidden()
        assert ui.action_button.isEnabled()
        assert ui.action_button.text() == "Hide as plain text"

    def test_message_over_capacity_blocks(
        self, window: MainWindow, tmp_path: Path
    ) -> None:
        tiny = tmp_path / "tiny.png"
        Image.new("RGB", (8, 8)).save(tiny)
        _fill_hide_form(window, tiny)
        ui = window.ui
        assert ui.capacity_meter.bar.property("over") is True
        assert ui.message_header.state == "error"
        assert not ui.action_button.isEnabled()

    def test_non_image_shows_inline_error(self, window: MainWindow) -> None:
        window.load_image(str(FIXTURES / "notimg.png"))
        ui = window.ui
        assert ui.image_header.state == "error"
        assert ui.image_error.text()
        assert not ui.image_error.isHidden()

    def test_same_output_as_input_is_rejected(
        self, window: MainWindow, cover: Path
    ) -> None:
        _fill_hide_form(window, cover)
        window.ui.output_input.setText(str(cover))
        assert window.ui.output_header.state == "error"
        assert not window.ui.action_button.isEnabled()

    def test_jpeg_shows_metadata_note(self, window: MainWindow) -> None:
        window.load_image(str(FIXTURES / "plain.jpg"))
        assert not window.ui.image_note.isHidden()
        assert window.ui.image_card.chip.text() == "EXIF"


class TestModeSwitch:
    def test_switch_keeps_image_and_clears_fields(
        self, window: MainWindow, cover: Path
    ) -> None:
        _fill_hide_form(window, cover)
        window.ui.mode_switch.button(Mode.REVEAL).click()
        ui = window.ui
        assert window.model.mode == Mode.REVEAL
        assert ui.image_card.info is not None
        assert ui.message_input.toPlainText() == ""
        assert ui.secret_input.text() == ""
        assert ui.message_section.isHidden()
        assert ui.output_section.isHidden()
        assert ui.image_header.title.text() == "Image with a hidden message"


class TestRoundTrip:
    @pytest.mark.parametrize("encrypt", [True, False])
    def test_hide_then_reveal(
        self, window: MainWindow, cover: Path, encrypt: bool
    ) -> None:
        _fill_hide_form(window, cover, encrypt=encrypt)
        ui = window.ui
        window.run_action()

        assert ui.pages.currentIndex() == RESULT_PAGE
        output = Path(ui.output_input.text())
        assert output.exists()
        assert ui.result_name.text() == output.name

        ui.test_reveal_button.click()
        assert window.model.mode == Mode.REVEAL
        assert ui.pages.currentIndex() == FORM_PAGE
        assert ui.image_card.info is not None
        assert ui.image_card.info.path == str(output)

        ui.encrypt_toggle.setChecked(encrypt)
        if encrypt:
            ui.secret_input.setText(SECRET)
        window.run_action()

        assert ui.revealed_text.toPlainText() == MESSAGE
        assert not ui.reveal_result.isHidden()

    def test_wrong_secret_shows_inline_error(
        self, window: MainWindow, cover: Path
    ) -> None:
        _fill_hide_form(window, cover)
        window.run_action()
        window.ui.test_reveal_button.click()

        ui = window.ui
        ui.secret_input.setText("not-the-secret")
        window.run_action()

        assert ui.revealed_text.toPlainText() == ""
        assert ui.protection_header.state == "error"
        assert "doesn't unlock" in ui.secret_status.text()
        assert not ui.reveal_help.isHidden()
        assert ui.action_button.text() == "Try again"

        ui.secret_input.setText(SECRET)
        assert ui.reveal_help.isHidden()

    def test_image_without_message(self, window: MainWindow, cover: Path) -> None:
        window.ui.mode_switch.button(Mode.REVEAL).click()
        window.load_image(str(cover))
        window.ui.encrypt_toggle.setChecked(False)
        window.run_action()
        assert window.ui.image_error.text() == "No hidden message found in this image."

    def test_hide_another_resets(self, window: MainWindow, cover: Path) -> None:
        _fill_hide_form(window, cover)
        window.run_action()
        window.ui.hide_another_button.click()
        ui = window.ui
        assert ui.pages.currentIndex() == FORM_PAGE
        assert ui.image_card.info is None
        assert not ui.action_button.isEnabled()
