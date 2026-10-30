import pytest
from PyQt6.QtWidgets import QApplication

from app.gui.ui import icons

ICON_SIZE = 16


@pytest.mark.parametrize("name", sorted(icons.ICON_NAMES))
def test_every_icon_renders(qapp: QApplication, name: str) -> None:
    image = icons.pixmap(name, "#FF0000", ICON_SIZE).toImage()
    assert image.deviceIndependentSize().width() == ICON_SIZE
    painted = any(
        image.pixelColor(x, y).alpha() > 0
        for x in range(image.width())
        for y in range(image.height())
    )
    assert painted
