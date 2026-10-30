from PyQt6.QtCore import QRect
from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QDragEnterEvent
from PyQt6.QtGui import QDragLeaveEvent
from PyQt6.QtGui import QDropEvent
from PyQt6.QtGui import QImageReader
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtWidgets import QStackedWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from app.gui.controllers.actions import Hiding
from app.gui.controllers.actions import ImageInfo
from app.gui.ui import icons
from app.gui.ui import styles
from app.gui.ui.formatting import human_size

THUMBNAIL_SIZE = 40
_EMPTY_PAGE = 0
_LOADED_PAGE = 1


def _thumbnail(path: str, size: int) -> QPixmap | None:
    """Decode only a scaled-down copy of the image, cropped to a square."""
    reader = QImageReader(path)
    original = reader.size()
    if not original.isValid():
        return None
    target = original.scaled(
        QSize(size * 2, size * 2), Qt.AspectRatioMode.KeepAspectRatioByExpanding
    )
    reader.setScaledSize(target)
    image = reader.read()
    if image.isNull():
        return None
    side = min(image.width(), image.height())
    square = image.copy(
        QRect((image.width() - side) // 2, (image.height() - side) // 2, side, side)
    )
    return QPixmap.fromImage(square).scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


class ImageCard(QStackedWidget):
    """Drop zone that becomes a file card once an image is chosen."""

    browse_requested = pyqtSignal()
    file_dropped = pyqtSignal(str)
    cleared = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._info: ImageInfo | None = None

        self.addWidget(self._build_empty_page())
        self.addWidget(self._build_loaded_page())
        self.currentChanged.connect(self._fit_current_page)  # pyright: ignore[reportUnknownMemberType]
        self.setCurrentIndex(_EMPTY_PAGE)
        self._fit_current_page(_EMPTY_PAGE)

    @property
    def info(self) -> ImageInfo | None:
        return self._info

    def sizeHint(self) -> QSize:
        page = self.currentWidget()
        return page.sizeHint() if page is not None else super().sizeHint()

    def minimumSizeHint(self) -> QSize:
        page = self.currentWidget()
        return page.minimumSizeHint() if page is not None else super().minimumSizeHint()

    def _fit_current_page(self, index: int) -> None:
        # A stacked widget is as tall as its tallest page; ignore hidden ones.
        for i in range(self.count()):
            page = self.widget(i)
            if page is None:
                continue
            policy = (
                QSizePolicy.Policy.Preferred
                if i == index
                else QSizePolicy.Policy.Ignored
            )
            page.setSizePolicy(policy, policy)
        self.updateGeometry()

    def _build_empty_page(self) -> QWidget:
        t = styles.theme()
        self.drop_zone = QFrame()
        self.drop_zone.setProperty("dropzone", True)
        self.drop_zone.setMinimumHeight(104)

        layout = QVBoxLayout(self.drop_zone)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel()
        icon.setFixedSize(28, 28)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setPixmap(icons.pixmap("upload", t.lsb_text, 14))
        icon.setStyleSheet(f"background-color: {t.lsb_bg}; border-radius: 14px;")

        title = QLabel("Drop an image here")
        title.setProperty("role", "section")

        self.browse_button = QPushButton("Browse…")
        self.browse_button.setObjectName("browse_button")
        self.browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_button.clicked.connect(self.browse_requested)  # pyright: ignore[reportUnknownMemberType]

        hint = QLabel("PNG, BMP (pixels) · JPEG, TIFF (metadata)")
        hint.setProperty("role", "hint")

        for widget in (icon, title, self.browse_button, hint):
            layout.addWidget(widget, 0, Qt.AlignmentFlag.AlignHCenter)
        return self.drop_zone

    def _build_loaded_page(self) -> QWidget:
        t = styles.theme()
        card = QFrame()
        card.setProperty("card", True)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.thumbnail = QLabel()
        self.thumbnail.setObjectName("thumbnail")
        self.thumbnail.setFixedSize(THUMBNAIL_SIZE, THUMBNAIL_SIZE)
        self.thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text = QVBoxLayout()
        text.setSpacing(2)
        text.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.name_label = QLabel()
        self.name_label.setObjectName("image_name")
        self.name_label.setProperty("role", "strong")
        self.name_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        meta = QHBoxLayout()
        meta.setSpacing(4)
        self.chip = QLabel()
        self.chip.setObjectName("technique_chip")
        self.chip.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.meta_label = QLabel()
        self.meta_label.setProperty("role", "hint")
        meta.addWidget(self.chip)
        meta.addWidget(self.meta_label)
        meta.addStretch()

        text.addWidget(self.name_label)
        text.addLayout(meta)

        self.remove_button = QPushButton()
        self.remove_button.setObjectName("remove_image_button")
        self.remove_button.setProperty("variant", "ghost")
        self.remove_button.setIcon(icons.icon("close", t.muted))
        self.remove_button.setAccessibleName("Remove image")
        self.remove_button.setToolTip("Remove image")
        self.remove_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_button.clicked.connect(self.clear)  # pyright: ignore[reportUnknownMemberType]

        layout.addWidget(self.thumbnail)
        layout.addLayout(text, 1)
        layout.addWidget(self.remove_button, 0, Qt.AlignmentFlag.AlignTop)
        return card

    def set_image(self, info: ImageInfo) -> None:
        self._info = info
        t = styles.theme()

        self.name_label.setText(info.name)
        self.name_label.setToolTip(info.path)
        self.meta_label.setText(
            f"{info.format} · {info.width} × {info.height} · "  # noqa: RUF001
            f"{human_size(info.file_size)}"
        )

        if info.technique is None:
            self.chip.hide()
        else:
            self.chip.show()
            self.chip.setText(info.technique.upper())
            styles.set_property(
                self.chip, "chip", "lsb" if info.technique == Hiding.LSB else "exif"
            )

        thumb = _thumbnail(info.path, THUMBNAIL_SIZE)
        if thumb is None:
            self.thumbnail.setPixmap(icons.pixmap("image", t.muted, 16, 1.75))
        else:
            self.thumbnail.setPixmap(thumb)

        self.setCurrentIndex(_LOADED_PAGE)

    def clear(self) -> None:
        had_image = self._info is not None
        self._info = None
        self.thumbnail.clear()
        self.setCurrentIndex(_EMPTY_PAGE)
        if had_image:
            self.cleared.emit()

    # -- drag and drop ---------------------------------------------------------

    @staticmethod
    def _local_file(event: QDragEnterEvent | QDropEvent) -> str | None:
        mime = event.mimeData()
        if mime is None or not mime.hasUrls():
            return None
        urls = mime.urls()
        if len(urls) != 1 or not urls[0].isLocalFile():
            return None
        return urls[0].toLocalFile()

    def dragEnterEvent(self, a0: QDragEnterEvent | None) -> None:
        if a0 is not None and self._local_file(a0):
            a0.acceptProposedAction()
            styles.set_property(self.drop_zone, "dragging", True)

    def dragLeaveEvent(self, a0: QDragLeaveEvent | None) -> None:
        styles.set_property(self.drop_zone, "dragging", False)

    def dropEvent(self, a0: QDropEvent | None) -> None:
        styles.set_property(self.drop_zone, "dragging", False)
        if a0 is None:
            return
        path = self._local_file(a0)
        if path:
            a0.acceptProposedAction()
            self.file_dropped.emit(path)
