import ctypes
import sys

from PyQt6.QtCore import QRectF
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPainterPath
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QMainWindow

from app.constants import APP_ICON
from app.constants import APP_NAME

# Apple's macOS icon grid: on a 1024px canvas the icon body is 824px wide,
# centred, with a ~185px corner radius.
MACOS_ICON_CANVAS = 1024
MACOS_ICON_BODY = 824
MACOS_ICON_RADIUS = 185


def app_icon() -> QIcon:
    return QIcon(str(APP_ICON))


def macos_dock_icon() -> QIcon:
    """Mimic the Dock's treatment of bundle icons for non-bundled runs.

    For a ``.app``, macOS shrinks the ``.icns`` onto its icon grid and clips it
    to a rounded shape. An icon set at runtime through Qt (``python -m app``)
    is shown verbatim instead, so apply the same grid and mask here.
    """
    source = QPixmap(str(APP_ICON))
    canvas = QPixmap(MACOS_ICON_CANVAS, MACOS_ICON_CANVAS)
    canvas.fill(Qt.GlobalColor.transparent)

    offset = (MACOS_ICON_CANVAS - MACOS_ICON_BODY) / 2
    body = QRectF(offset, offset, MACOS_ICON_BODY, MACOS_ICON_BODY)
    path = QPainterPath()
    path.addRoundedRect(body, MACOS_ICON_RADIUS, MACOS_ICON_RADIUS)

    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.setClipPath(path)
    painter.drawPixmap(body, source, QRectF(source.rect()))
    painter.end()
    return QIcon(canvas)


def prepare_platform() -> None:
    """Run platform-specific setup before QApplication is created."""
    if sys.platform == "win32":
        app_id = f"fr.kisscool.{APP_NAME.lower()}"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)


def apply_app_icon(app: QApplication, window: QMainWindow | None = None) -> None:
    """Set the application icon on the app and optionally on a window."""
    icon = app_icon()
    if sys.platform != "darwin":
        app.setWindowIcon(icon)
    elif not getattr(sys, "frozen", False):
        # The .app bundle gets its Dock icon from the .icns; only dev runs need this.
        app.setWindowIcon(macos_dock_icon())
    if window is not None:
        window.setWindowIcon(icon)
