import ctypes
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow

from app.constants import APP_ICON
from app.constants import APP_NAME


def app_icon() -> QIcon:
    return QIcon(str(APP_ICON))


def prepare_platform() -> None:
    """Run platform-specific setup before QApplication is created."""
    if sys.platform == "win32":
        app_id = f"fr.kisscool.{APP_NAME.lower()}"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)


def apply_app_icon(app: QApplication, window: QMainWindow | None = None) -> None:
    """Set the application icon on the app and optionally on a window."""
    icon = app_icon()
    is_macos_app_bundle = sys.platform == "darwin" and getattr(sys, "frozen", False)
    if not is_macos_app_bundle:
        app.setWindowIcon(icon)
    if window is not None:
        window.setWindowIcon(icon)
