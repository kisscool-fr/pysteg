from pathlib import Path

import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QLineEdit

from app.capacity import Capacity
from app.gui.controllers.actions import ActionController
from app.gui.models.mode import Mode
from app.gui.models.mode import WindowModel
from app.gui.ui.components.capacity_meter import CapacityMeter
from app.gui.ui.components.image_card import ImageCard
from app.gui.ui.components.mode_switch import ModeSwitch
from app.gui.ui.components.secret_field import SecretField
from app.gui.ui.components.section_header import SectionHeader
from app.gui.ui.components.toggle_switch import ToggleSwitch
from app.gui.ui.formatting import human_size
from app.gui.ui.formatting import plural

FIXTURES = Path(__file__).parent / "fixtures"

pytestmark = pytest.mark.usefixtures("qapp")


class TestFormatting:
    @pytest.mark.parametrize(
        "size, expected",
        [(512, "512 B"), (24 * 1024, "24 KB"), (int(2.4 * 1024 * 1024), "2.4 MB")],
    )
    def test_human_size(self, size: int, expected: str) -> None:
        assert human_size(size) == expected

    def test_plural(self) -> None:
        assert plural(1, "character") == "1 character"
        assert plural(1200, "character") == "1,200 characters"


class TestModeSwitch:
    def test_emits_selected_mode(self) -> None:
        switch = ModeSwitch()
        seen: list[Mode] = []
        switch.mode_changed.connect(seen.append)  # pyright: ignore[reportUnknownMemberType]

        switch.button(Mode.REVEAL).click()

        assert switch.mode() == Mode.REVEAL
        assert seen == [Mode.REVEAL]
        assert not switch.button(Mode.HIDE).isChecked()


class TestSectionHeader:
    def test_states(self) -> None:
        header = SectionHeader(2, "Message")
        assert header.badge.text() == "2"
        header.set_state("done")
        assert header.state == "done"
        assert header.badge.property("badge") == "done"
        header.set_state("pending")
        assert header.badge.text() == "2"


class TestToggleSwitch:
    def test_click_toggles(self) -> None:
        toggle = ToggleSwitch("Encrypt")
        assert toggle.accessibleName() == "Encrypt"
        toggle.click()
        assert toggle.isChecked()


class TestSecretField:
    def test_reveal_toggle(self) -> None:
        field = SecretField("secret")
        assert field.echoMode() == QLineEdit.EchoMode.Password
        assert field.visibility_action is not None
        field.visibility_action.trigger()
        assert field.is_revealed()

    def test_not_revealable(self) -> None:
        assert SecretField("confirm", revealable=False).visibility_action is None


class TestCapacityMeter:
    def test_over_capacity_turns_red(self) -> None:
        meter = CapacityMeter()
        meter.set_capacity(Capacity(used=2048, available=1024))
        assert meter.bar.property("over") is True
        assert meter.caption.text() == "Too long for this image"

    def test_within_capacity(self) -> None:
        meter = CapacityMeter()
        meter.set_capacity(Capacity(used=10, available=1000))
        assert meter.bar.property("over") is False
        assert meter.usage.text().endswith("used")


class TestImageCard:
    def test_set_and_clear(self, qapp: QApplication) -> None:
        card = ImageCard()
        info = ActionController(WindowModel()).inspect(str(FIXTURES / "plain.png"))
        cleared: list[bool] = []
        card.cleared.connect(lambda: cleared.append(True))  # pyright: ignore[reportUnknownMemberType]

        card.set_image(info)
        assert card.currentIndex() == 1
        assert card.name_label.text() == "plain.png"
        assert card.chip.text() == "LSB"

        card.remove_button.click()
        assert card.info is None
        assert card.currentIndex() == 0
        assert cleared == [True]
