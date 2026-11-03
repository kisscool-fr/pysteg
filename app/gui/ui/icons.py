"""Stroke icons drawn at runtime so they can be tinted per theme and state.

Outlines follow Lucide (https://lucide.dev), ISC License,
Copyright (c) for portions of Lucide are held by Cole Bemis 2013-2022 as part
of Feather (MIT), all other copyright for Lucide are held by Lucide
Contributors 2022.
"""

from PyQt6.QtCore import QByteArray
from PyQt6.QtCore import QRectF
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPixmap
from PyQt6.QtSvg import QSvgRenderer

_PATHS: dict[str, str] = {
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2"/>'
    '<path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "unlock": '<rect x="3" y="11" width="18" height="11" rx="2"/>'
    '<path d="M7 11V7a5 5 0 0 1 9.9-1"/>',
    "image": '<rect x="3" y="3" width="18" height="18" rx="2"/>'
    '<circle cx="9" cy="9" r="2"/>'
    '<path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
    '<polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/>',
    "download": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
    '<polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/>',
    "eye": '<path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0'
    ' 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/><circle cx="12" cy="12" r="3"/>',
    "eye_off": '<path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0'
    ' .696 10.747 10.747 0 0 1-1.444 2.49"/><path d="M14.084 14.158a3 3 0 0 1-4.242'
    '-4.242"/><path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-'
    '.696 10.75 10.75 0 0 1 4.446-5.143"/><path d="m2 2 20 20"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "check_circle": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "alert": '<path d="M12 7v6"/><path d="M12 17h.01"/>',
    "alert_circle": '<circle cx="12" cy="12" r="10"/>'
    '<line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>',
    "warning": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2'
    ' 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "close": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "copy": '<rect x="8" y="8" width="14" height="14" rx="2"/>'
    '<path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>',
    "folder": '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9'
    'L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>',
}

ICON_NAMES = frozenset(_PATHS)


def _svg(name: str, color: str, stroke_width: float) -> bytes:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round"'
        f' stroke-linejoin="round">{_PATHS[name]}</svg>'
    ).encode()


def pixmap(name: str, color: str, size: int = 16, stroke_width: float = 2) -> QPixmap:
    """Render icon ``name`` in ``color`` at ``size`` logical pixels."""
    app = QGuiApplication.instance()
    ratio = app.devicePixelRatio() if isinstance(app, QGuiApplication) else 1.0
    image = QPixmap(round(size * ratio), round(size * ratio))
    image.fill(Qt.GlobalColor.transparent)

    renderer = QSvgRenderer(QByteArray(_svg(name, color, stroke_width)))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(painter, QRectF(0, 0, image.width(), image.height()))
    painter.end()

    image.setDevicePixelRatio(ratio)
    return image


def icon(name: str, color: str, size: int = 16, stroke_width: float = 2) -> QIcon:
    return QIcon(pixmap(name, color, size, stroke_width))
