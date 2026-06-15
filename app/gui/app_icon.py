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
    """Set the application icon on the app and optionally on a window.

    On macOS the Dock icon comes from QApplication.setWindowIcon(), not from
    QMainWindow.setWindowIcon(). On Windows, SetCurrentProcessExplicitAppUserModelID
    (via prepare_platform) is also required when running from python.exe.
    """
    icon = app_icon()
    app.setWindowIcon(icon)
    if window is not None:
        window.setWindowIcon(icon)
