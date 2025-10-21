from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from app.constants import APP_NAME
from app.constants import APP_VERSION
from app.constants import ASSETS_DIRECTORY
from app.gui.models.mode import Mode
from app.gui.ui.components.file_selector import ReadOnlyFileSelector
from app.gui.ui.components.push_button import PushButton
from app.gui.ui.components.text_input import TextInput
from app.gui.ui.components.text_label import TextLabel
from app.gui.ui.components.text_line import TextLine


class MainWindowUI:
    def setup_ui(self, window: QMainWindow):
        window.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        window.setWindowIcon(QIcon(f"{ASSETS_DIRECTORY}/icons/icon.png"))
        window.setFixedSize(QSize(300, 500))

        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        self._create_mode_buttons()
        self._create_text_section()
        self._create_secret_section()
        self._create_file_section()
        self._create_action_button()

        self.central_widget.setLayout(self.layout)
        window.setCentralWidget(self.central_widget)

        window.status_bar = window.statusBar()  # pyright: ignore[reportAttributeAccessIssue]

    def center_window(self, window: QMainWindow):
        screen = window.screen().availableGeometry()  # pyright: ignore[reportOptionalMemberAccess]
        window_size = window.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        window.move(x, y)

    def _create_mode_buttons(self):
        rb_layout = QHBoxLayout()

        self.rb_encrypt = PushButton("🔐 Hide", Mode.ENCRYPT)
        self.rb_decrypt = PushButton("🔓 Reveal", Mode.DECRYPT)
        rb_layout.addWidget(self.rb_encrypt)
        rb_layout.addWidget(self.rb_decrypt)
        self.layout.addLayout(rb_layout)

    def _create_text_section(self):
        text_label = TextLabel("Text to hide", "mode_label")
        self.layout.addWidget(text_label)

        text_input = TextInput("Enter text here...", "text_input")
        self.layout.addWidget(text_input)

    def _create_secret_section(self):
        secret_label = TextLabel("Shared secret", "secret_label")
        self.layout.addWidget(secret_label)

        secret_input = TextLine("", "secret_input")
        self.layout.addWidget(secret_input)

    def _create_file_section(self):
        image_label = TextLabel("Image file (.png only)", "image_label")
        self.layout.addWidget(image_label)

        self.button_file = PushButton("Choose file", "select_file_button")
        self.layout.addWidget(self.button_file)

        file_selector = ReadOnlyFileSelector("No file selected", "file_selector")
        self.layout.addWidget(file_selector)

    def _create_action_button(self):
        self.action_button = PushButton("Hide Text", "action_button")
        self.layout.addWidget(self.action_button)
