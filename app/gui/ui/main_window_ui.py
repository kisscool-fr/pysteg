from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from app.constants import APP_NAME
from app.constants import APP_VERSION
from app.constants import ICON_LOCK
from app.constants import ICON_UNLOCK
from app.gui.models.mode import Mode
from app.gui.ui import styles
from app.gui.ui.components.file_selector import ReadOnlyFileSelector
from app.gui.ui.components.push_button import PushButton
from app.gui.ui.components.text_input import TextInput
from app.gui.ui.components.text_label import TextLabel
from app.gui.ui.components.text_line import TextLine


class MainWindowUI:
    def setup_ui(self, window: QMainWindow):
        window.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        window.setFixedSize(QSize(318, 507))

        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(8)

        self._create_mode_buttons()
        self._create_accent_bar()
        self._create_text_section()
        self._add_separator()
        self._create_secret_section()
        self._add_separator()
        self._create_file_section()
        self._add_separator()
        self._create_action_button()

        self.central_widget.setLayout(self.layout)
        window.setCentralWidget(self.central_widget)

        window.status_bar = window.statusBar()  # pyright: ignore[reportAttributeAccessIssue]

        self.apply_mode_style(Mode.ENCRYPT)

    def center_window(self, window: QMainWindow):
        screen = window.screen().availableGeometry()  # pyright: ignore[reportOptionalMemberAccess]
        window_size = window.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        window.move(x, y)

    def _create_mode_buttons(self):
        rb_layout = QHBoxLayout()

        self.rb_encrypt = PushButton(f"{ICON_LOCK} Hide", Mode.ENCRYPT)
        self.rb_decrypt = PushButton(f"{ICON_UNLOCK} Reveal", Mode.DECRYPT)
        rb_layout.addWidget(self.rb_encrypt)
        rb_layout.addWidget(self.rb_decrypt)
        self.layout.addLayout(rb_layout)

    def _create_accent_bar(self):
        self.accent_bar = QFrame()
        self.accent_bar.setFrameShape(QFrame.Shape.HLine)
        self.accent_bar.setFixedHeight(2)
        self.layout.addWidget(self.accent_bar)

    def _add_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        separator.setStyleSheet(styles.separator())
        self.layout.addWidget(separator)

    def apply_mode_style(self, mode: Mode):
        if mode == Mode.ENCRYPT:
            palette = styles.HIDE_ACCENT
            self.rb_encrypt.setStyleSheet(styles.mode_button_active(palette))
            self.rb_decrypt.setStyleSheet(styles.mode_button_inactive())
        else:
            palette = styles.REVEAL_ACCENT
            self.rb_encrypt.setStyleSheet(styles.mode_button_inactive())
            self.rb_decrypt.setStyleSheet(styles.mode_button_active(palette))

        self.accent_bar.setStyleSheet(styles.accent_bar(palette))
        self.action_button.setStyleSheet(styles.action_button(palette))

    def _create_text_section(self):
        self.mode_label = TextLabel("Text to hide", "mode_label")
        self.layout.addWidget(self.mode_label)

        self.text_input = TextInput("Enter text here...", "text_input")
        self.layout.addWidget(self.text_input)

    def _create_secret_section(self):
        secret_label = TextLabel("Shared secret", "secret_label")
        self.layout.addWidget(secret_label)

        secret_row = QHBoxLayout()
        self.secret_input = TextLine("", "secret_input")
        self.plain_text_checkbox = QCheckBox()
        self.plain_text_checkbox.setObjectName("plain_text_checkbox")
        self.plain_text_checkbox.setToolTip("Hide text in the image without encryption")
        secret_row.addWidget(self.secret_input)
        secret_row.addWidget(self.plain_text_checkbox)
        self.layout.addLayout(secret_row)

    def _create_file_section(self):
        image_label = TextLabel("Cover image", "image_label")
        self.layout.addWidget(image_label)

        self.button_file = PushButton("Choose file", "select_file_button")
        self.button_file.setStyleSheet(styles.secondary_button())
        self.layout.addWidget(self.button_file)

        self.file_selector = ReadOnlyFileSelector("No file selected", "file_selector")
        self.layout.addWidget(self.file_selector)

    def _create_action_button(self):
        self.action_button = PushButton(f"{ICON_LOCK} Hide Text", "action_button")
        self.layout.addWidget(self.action_button)
