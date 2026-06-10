from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from app.gui.controllers.actions import ActionController
from app.gui.controllers.actions import Format
from app.gui.controllers.actions import Hiding
from app.gui.models.mode import WindowModel

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def model() -> WindowModel:
    return WindowModel(secret="test_secret", text="hello world")


@pytest.fixture
def controller(model: WindowModel) -> ActionController:
    return ActionController(model)


# ---------------------------------------------------------------------------
# Format enum
# ---------------------------------------------------------------------------


class TestFormat:
    def test_png_maps_to_lsb(self) -> None:
        assert Format.PNG == Hiding.LSB

    def test_bmp_maps_to_lsb(self) -> None:
        assert Format.BMP == Hiding.LSB

    def test_jpeg_maps_to_exif(self) -> None:
        assert Format.JPEG == Hiding.EXIF

    def test_tiff_maps_to_exif(self) -> None:
        assert Format.TIFF == Hiding.EXIF


# ---------------------------------------------------------------------------
# hiding_technique
# ---------------------------------------------------------------------------


class TestTechnique:
    @pytest.mark.parametrize("pil_format", ["PNG", "BMP"])
    def test_lsb_formats(self, controller: ActionController, pil_format: str) -> None:
        assert controller.get_hiding_technique(pil_format) == Hiding.LSB

    @pytest.mark.parametrize("pil_format", ["JPEG", "TIFF"])
    def test_exif_formats(self, controller: ActionController, pil_format: str) -> None:
        assert controller.get_hiding_technique(pil_format) == Hiding.EXIF

    @pytest.mark.parametrize("pil_format", ["GIF", "WEBP", "ICO", ""])
    def test_unsupported_returns_none(
        self, controller: ActionController, pil_format: str
    ) -> None:
        assert controller.get_hiding_technique(pil_format) is None

    def test_none_returns_none(self, controller: ActionController) -> None:
        assert controller.get_hiding_technique(None) is None


# ---------------------------------------------------------------------------
# hide
# ---------------------------------------------------------------------------


class TestHide:
    @patch("app.gui.controllers.actions.lsb")
    @patch("app.gui.controllers.actions.Image")
    def test_lsb_path_calls_lsb_hide_and_save(
        self, mock_image: MagicMock, mock_lsb: MagicMock, controller: ActionController
    ) -> None:
        mock_image.open.return_value.__enter__.return_value.format = "PNG"
        saved = MagicMock()
        mock_lsb.hide.return_value = saved

        ok, msg = controller.hide("src.png", "dst.png", "secret text", plain_text=False)

        mock_lsb.hide.assert_called_once()
        saved.save.assert_called_once_with("dst.png")
        assert ok is True
        assert msg == "Encryption successful"

    @patch("app.gui.controllers.actions.exifHeader")
    @patch("app.gui.controllers.actions.Image")
    def test_exif_path_calls_exif_hide(
        self, mock_image: MagicMock, mock_exif: MagicMock, controller: ActionController
    ) -> None:
        mock_image.open.return_value.__enter__.return_value.format = "JPEG"

        ok, msg = controller.hide("src.jpg", "dst.jpg", "secret text", plain_text=False)

        mock_exif.hide.assert_called_once_with(
            "src.jpg", "dst.jpg", secret_message="secret text"
        )
        assert ok is True
        assert msg == "Encryption successful"

    @pytest.mark.parametrize("pil_format", ["PNG", "BMP"])
    @patch("app.gui.controllers.actions.lsb")
    @patch("app.gui.controllers.actions.Image")
    def test_lsb_formats_succeed(
        self,
        mock_image: MagicMock,
        mock_lsb: MagicMock,
        pil_format: str,
        controller: ActionController,
    ) -> None:
        mock_image.open.return_value.__enter__.return_value.format = pil_format
        ok, _ = controller.hide("src", "dst", "text", plain_text=False)
        assert ok is True

    @pytest.mark.parametrize("pil_format", ["JPEG", "TIFF"])
    @patch("app.gui.controllers.actions.exifHeader")
    @patch("app.gui.controllers.actions.Image")
    def test_exif_formats_succeed(
        self,
        mock_image: MagicMock,
        _mock_exif: MagicMock,
        pil_format: str,
        controller: ActionController,
    ) -> None:
        mock_image.open.return_value.__enter__.return_value.format = pil_format
        ok, _ = controller.hide("src", "dst", "text", plain_text=False)
        assert ok is True

    @patch("app.gui.controllers.actions.Image")
    def test_unsupported_format_returns_failure(
        self, mock_image: MagicMock, controller: ActionController
    ) -> None:
        mock_image.open.return_value.__enter__.return_value.format = "GIF"

        ok, msg = controller.hide("src.gif", "dst.gif", "secret text", plain_text=False)

        assert ok is False
        assert msg == "Unsupported image format"


# ---------------------------------------------------------------------------
# reveal
# ---------------------------------------------------------------------------


class TestReveal:
    @patch("app.gui.controllers.actions.lsb")
    @patch("app.gui.controllers.actions.Image")
    def test_lsb_path_calls_lsb_reveal(
        self, mock_image: MagicMock, mock_lsb: MagicMock, controller: ActionController
    ) -> None:
        mock_image.open.return_value.__enter__.return_value.format = "PNG"
        mock_lsb.reveal.return_value = "hidden text"

        ok, text = controller.reveal("src.png")

        mock_lsb.reveal.assert_called_once()
        assert ok is True
        assert text == "hidden text"

    @patch("app.gui.controllers.actions.exifHeader")
    @patch("app.gui.controllers.actions.Image")
    def test_exif_path_calls_exif_reveal(
        self, mock_image: MagicMock, mock_exif: MagicMock, controller: ActionController
    ) -> None:
        mock_image.open.return_value.__enter__.return_value.format = "JPEG"
        mock_exif.reveal.return_value.decode.return_value = "hidden text"

        ok, text = controller.reveal("src.jpg")

        mock_exif.reveal.assert_called_once_with("src.jpg")
        assert ok is True
        assert text == "hidden text"

    @patch("app.gui.controllers.actions.Image")
    def test_unsupported_format_returns_failure(
        self, mock_image: MagicMock, controller: ActionController
    ) -> None:
        mock_image.open.return_value.__enter__.return_value.format = "GIF"

        ok, msg = controller.reveal("src.gif")

        assert ok is False
        assert msg == "Unsupported image format"
