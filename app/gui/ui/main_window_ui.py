from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtWidgets import QStackedWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from app.constants import APP_NAME
from app.constants import APP_VERSION
from app.gui.ui import icons
from app.gui.ui import styles
from app.gui.ui.components.callout import Callout
from app.gui.ui.components.capacity_meter import CapacityMeter
from app.gui.ui.components.image_card import THUMBNAIL_SIZE
from app.gui.ui.components.image_card import ImageCard
from app.gui.ui.components.mode_switch import ModeSwitch
from app.gui.ui.components.secret_field import SecretField
from app.gui.ui.components.section_header import SectionHeader
from app.gui.ui.components.toggle_switch import ToggleSwitch

MINIMUM_SIZE = QSize(320, 480)
DEFAULT_SIZE = QSize(340, 660)
FORM_PAGE = 0
RESULT_PAGE = 1

_MARGIN = 10
_SECTION_SPACING = 12
_SECTION_INNER_SPACING = 5
_CARD_MARGINS = (8, 8, 8, 8)
_CARD_SPACING = 6


def _label(text: str = "", role: str | None = None, *, wrap: bool = False) -> QLabel:
    label = QLabel(text)
    if role is not None:
        label.setProperty("role", role)
    label.setWordWrap(wrap)
    return label


def _button(text: str, object_name: str, variant: str | None = None) -> QPushButton:
    button = QPushButton(text)
    button.setObjectName(object_name)
    if variant is not None:
        button.setProperty("variant", variant)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    return button


def _section() -> tuple[QWidget, QVBoxLayout]:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(_SECTION_INNER_SPACING)
    return widget, layout


class MainWindowUI:
    """Builds the widgets; MainWindow wires the behaviour."""

    def setup_ui(self, window: QMainWindow):
        window.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        window.setMinimumSize(MINIMUM_SIZE)
        window.resize(DEFAULT_SIZE)

        central = QWidget()
        central.setObjectName("central")
        root = QVBoxLayout(central)
        root.setContentsMargins(_MARGIN, _MARGIN, _MARGIN, _MARGIN)
        root.setSpacing(_SECTION_SPACING)

        self.mode_switch = ModeSwitch()
        root.addWidget(self.mode_switch)

        self.pages = QStackedWidget()
        self.pages.addWidget(self._build_form_page())
        self.pages.addWidget(self._build_result_page())
        root.addWidget(self.pages, 1)

        window.setCentralWidget(central)

    def center_window(self, window: QMainWindow):
        screen = window.screen().availableGeometry()  # pyright: ignore[reportOptionalMemberAccess]
        size = window.frameGeometry()
        height = min(size.height(), screen.height())
        window.resize(size.width(), height)
        window.move(
            screen.x() + (screen.width() - size.width()) // 2,
            screen.y() + (screen.height() - height) // 2,
        )

    # -- form ------------------------------------------------------------------

    def _build_form_page(self) -> QWidget:
        page = QWidget()
        page.setObjectName("form")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        content = QWidget()
        content.setObjectName("form_content")
        sections = QVBoxLayout(content)
        # Keep the cards clear of the overlay scroll bar.
        sections.setContentsMargins(0, 0, 8, 0)
        sections.setSpacing(_SECTION_SPACING)
        sections.addWidget(self._build_image_section())
        sections.addWidget(self._build_message_section())
        sections.addWidget(self._build_protection_section())
        sections.addWidget(self._build_output_section())
        sections.addWidget(self._build_reveal_result())
        sections.addWidget(self._build_reveal_help())
        # A stretch factor, so spare height never goes to the sections themselves.
        sections.addStretch(1)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidget(content)
        layout.addWidget(self.scroll, 1)

        self.action_button = _button("", "action_button", "primary")
        self.action_button.setIconSize(QSize(14, 14))
        self.action_hint = _label(role="hint")
        self.action_hint.setObjectName("action_hint")
        self.action_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.action_button)
        layout.addWidget(self.action_hint)
        return page

    def _build_image_section(self) -> QWidget:
        section, layout = _section()
        self.image_header = SectionHeader(1, "Cover image")
        self.image_card = ImageCard()
        self.image_header.set_buddy(self.image_card)
        self.image_note = _label(
            "Hidden in the file's metadata. Re-saving or uploading the photo often "
            "strips it.",
            "hint",
            wrap=True,
        )
        self.image_error = _label(role="error", wrap=True)
        self.image_error.setObjectName("image_error")
        self.capacity_meter = CapacityMeter()

        for widget in (
            self.image_header,
            self.image_card,
            self.image_note,
            self.image_error,
            self.capacity_meter,
        ):
            layout.addWidget(widget)
        return section

    def _build_message_section(self) -> QWidget:
        self.message_section, layout = _section()
        self.message_header = SectionHeader(2, "Message")

        self.message_input = QPlainTextEdit()
        self.message_input.setObjectName("message_input")
        self.message_input.setPlaceholderText("Type the message to hide…")
        self.message_input.setFixedHeight(68)
        self.message_input.setTabChangesFocus(True)
        self.message_header.set_buddy(self.message_input)

        self.message_counter = _label(role="hint")
        self.message_counter.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.message_error = _label(role="error", wrap=True)
        self.message_error.setObjectName("message_error")

        layout.addWidget(self.message_header)
        layout.addWidget(self.message_input)
        layout.addWidget(self.message_counter)
        layout.addWidget(self.message_error)
        return self.message_section

    def _build_protection_section(self) -> QWidget:
        section, layout = _section()
        self.protection_header = SectionHeader(3, "Protection")

        card = QFrame()
        card.setProperty("card", True)
        inner = QVBoxLayout(card)
        inner.setContentsMargins(*_CARD_MARGINS)
        inner.setSpacing(_CARD_SPACING)

        row = QHBoxLayout()
        row.setSpacing(8)
        labels = QVBoxLayout()
        labels.setSpacing(0)
        self.encrypt_title = _label("Encrypt with a shared secret", "strong")
        self.encrypt_subtitle = _label("AES-256-GCM · Argon2id", "hint")
        labels.addWidget(self.encrypt_title)
        labels.addWidget(self.encrypt_subtitle)
        self.encrypt_toggle = ToggleSwitch("Encrypt with a shared secret")
        self.encrypt_toggle.setObjectName("encrypt_toggle")
        self.encrypt_toggle.setChecked(True)
        row.addLayout(labels, 1)
        row.addWidget(self.encrypt_toggle)
        inner.addLayout(row)

        self.plain_warning = Callout(
            "warning",
            "Anyone who extracts the hidden data can read it. "
            "Turn encryption on unless that's fine.",
        )
        inner.addWidget(self.plain_warning)

        self.secret_label = _label("Shared secret", "hint")
        self.secret_input = SecretField("secret_input", "At least 8 characters")
        self.secret_label.setBuddy(self.secret_input)
        self.secret_input.setAccessibleName("Shared secret")

        self.confirm_label = _label("Confirm secret", "hint")
        self.confirm_input = SecretField("confirm_input", revealable=False)
        self.confirm_label.setBuddy(self.confirm_input)
        self.confirm_input.setAccessibleName("Confirm secret")

        self.secret_status = _label(role="hint", wrap=True)
        self.secret_status.setObjectName("secret_status")

        for widget in (
            self.secret_label,
            self.secret_input,
            self.confirm_label,
            self.confirm_input,
            self.secret_status,
        ):
            inner.addWidget(widget)

        layout.addWidget(self.protection_header)
        layout.addWidget(card)
        return section

    def _build_output_section(self) -> QWidget:
        self.output_section, layout = _section()
        self.output_header = SectionHeader(4, "Save as")

        row = QHBoxLayout()
        row.setSpacing(6)
        self.output_input = QLineEdit()
        self.output_input.setObjectName("output_file_input")
        self.output_input.setPlaceholderText("Output file path")
        self.output_header.set_buddy(self.output_input)
        self.change_output_button = _button("Change…", "change_output_button")
        row.addWidget(self.output_input, 1)
        row.addWidget(self.change_output_button)

        self.output_error = _label(role="error", wrap=True)
        self.output_error.setObjectName("output_error")

        layout.addWidget(self.output_header)
        layout.addLayout(row)
        layout.addWidget(self.output_error)
        return self.output_section

    def _build_reveal_result(self) -> QWidget:
        t = styles.theme()
        self.reveal_result = QFrame()
        self.reveal_result.setObjectName("reveal_result")
        self.reveal_result.setProperty("result", "success")
        layout = QVBoxLayout(self.reveal_result)
        layout.setContentsMargins(*_CARD_MARGINS)
        layout.setSpacing(_CARD_SPACING)

        row = QHBoxLayout()
        row.setSpacing(6)
        status_icon = QLabel()
        status_icon.setPixmap(icons.pixmap("check_circle", t.success))
        self.reveal_status = _label(role="status")
        self.copy_text_button = _button("Copy", "copy_text_button", "success")
        self.copy_text_button.setIcon(icons.icon("copy", t.text, 12))
        self.save_text_button = _button("Save .txt", "save_text_button", "success")
        self.save_text_button.setIcon(icons.icon("download", t.text, 12))
        row.addWidget(status_icon)
        row.addWidget(self.reveal_status, 1)

        # Under the text rather than beside the status: the window is too narrow
        # for both on one line.
        actions = QHBoxLayout()
        actions.setSpacing(6)
        actions.addStretch()
        actions.addWidget(self.copy_text_button)
        actions.addWidget(self.save_text_button)

        self.revealed_text = QPlainTextEdit()
        self.revealed_text.setObjectName("revealed_text")
        self.revealed_text.setProperty("revealed", True)
        self.revealed_text.setReadOnly(True)
        self.revealed_text.setMinimumHeight(80)
        self.revealed_text.setAccessibleName("Revealed message")

        layout.addLayout(row)
        layout.addWidget(self.revealed_text)
        layout.addLayout(actions)
        return self.reveal_result

    def _build_reveal_help(self) -> QWidget:
        self.reveal_help = QFrame()
        self.reveal_help.setObjectName("reveal_help")
        self.reveal_help.setProperty("card", True)
        layout = QVBoxLayout(self.reveal_help)
        layout.setContentsMargins(*_CARD_MARGINS)
        layout.setSpacing(_CARD_SPACING)
        layout.addWidget(_label("Still not working?", "strong"))
        layout.addWidget(
            _label(
                "If the sender didn't encrypt it, turn “Message is encrypted” off.",
                "muted",
                wrap=True,
            )
        )
        layout.addWidget(
            _label(
                "If the image was re-saved, resized or sent through a chat app, the "
                "hidden data may be gone. Ask for the original file.",
                "muted",
                wrap=True,
            )
        )
        return self.reveal_help

    # -- hide result -----------------------------------------------------------

    def _build_result_page(self) -> QWidget:
        t = styles.theme()
        page = QWidget()
        page.setObjectName("result_page")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addStretch()

        badge = QLabel()
        badge.setFixedSize(44, 44)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setPixmap(icons.pixmap("check", t.success, 22, stroke_width=2.5))
        badge.setStyleSheet(f"background-color: {t.success_bg}; border-radius: 22px;")
        layout.addWidget(badge, 0, Qt.AlignmentFlag.AlignHCenter)

        self.result_title = _label("Message hidden", "title")
        self.result_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_description = _label(role="muted", wrap=True)
        self.result_description.setObjectName("result_description")
        self.result_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.result_title)
        layout.addWidget(self.result_description)
        layout.addWidget(self._build_result_file_card())

        actions = QHBoxLayout()
        actions.setSpacing(6)
        self.show_folder_button = _button("", "show_folder_button")
        self.show_folder_button.setIcon(icons.icon("folder", t.text))
        self.test_reveal_button = _button("Test with Reveal", "test_reveal_button")
        self.test_reveal_button.setIcon(icons.icon("unlock", t.text))
        for button in (self.show_folder_button, self.test_reveal_button):
            button.setMinimumHeight(30)
            actions.addWidget(button, 1)
        layout.addLayout(actions)
        layout.addStretch()

        self.hide_another_button = _button(
            "Hide another message", "hide_another_button", "primary"
        )
        layout.addWidget(self.hide_another_button)
        return page

    def _build_result_file_card(self) -> QWidget:
        t = styles.theme()
        file_card = QFrame()
        file_card.setProperty("card", True)
        file_row = QHBoxLayout(file_card)
        file_row.setContentsMargins(*_CARD_MARGINS)
        file_row.setSpacing(8)
        self.result_thumbnail = QLabel()
        self.result_thumbnail.setObjectName("thumbnail")
        self.result_thumbnail.setFixedSize(THUMBNAIL_SIZE, THUMBNAIL_SIZE)
        self.result_thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_text = QVBoxLayout()
        file_text.setSpacing(2)
        self.result_name = _label(role="strong")
        self.result_name.setObjectName("result_name")
        self.result_meta = _label(role="hint")
        file_text.addWidget(self.result_name)
        file_text.addWidget(self.result_meta)
        self.copy_path_button = _button("", "copy_path_button", "ghost")
        self.copy_path_button.setIcon(icons.icon("copy", t.muted))
        self.copy_path_button.setAccessibleName("Copy file path")
        self.copy_path_button.setToolTip("Copy file path")
        file_row.addWidget(self.result_thumbnail)
        file_row.addLayout(file_text, 1)
        file_row.addWidget(self.copy_path_button)
        return file_card
