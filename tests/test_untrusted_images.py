import zlib
from pathlib import Path

import pytest
from PIL import UnidentifiedImageError

from app.gui.controllers.actions import ActionController
from app.gui.models.mode import WindowModel

FIXTURES = Path(__file__).parent / "fixtures"

# Anything bigger than this coming out of a 64x64 image is a decompression bomb.
MAX_REVEALED_LENGTH = 1_000_000

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def controller() -> ActionController:
    return ActionController(WindowModel(secret="test_secret", text="hello world"))


# ---------------------------------------------------------------------------
# Legitimate images
# ---------------------------------------------------------------------------


class TestRoundTrip:
    @pytest.mark.parametrize("name", ["plain.png", "plain.jpg"])
    def test_hide_then_reveal(
        self, controller: ActionController, tmp_path: Path, name: str
    ) -> None:
        destination = tmp_path / f"hidden{Path(name).suffix}"

        ok, _ = controller.hide(
            str(FIXTURES / name), str(destination), "secret text", plain_text=True
        )
        assert ok

        ok, text = controller.reveal(str(destination))
        assert ok
        assert text == "secret text"


# ---------------------------------------------------------------------------
# Malformed or hostile images
# ---------------------------------------------------------------------------


class TestUntrustedInput:
    def test_non_image_is_rejected(self, controller: ActionController) -> None:
        with pytest.raises(UnidentifiedImageError):
            controller.reveal(str(FIXTURES / "notimg.png"))

    def test_png_without_hidden_text_raises_index_error(
        self, controller: ActionController
    ) -> None:
        with pytest.raises(IndexError):
            controller.reveal(str(FIXTURES / "plain.png"))

    @pytest.mark.parametrize(
        ("name", "current_error"),
        [
            ("plain.jpg", zlib.error),
            ("exif_nodesc.jpg", KeyError),
            ("bomb.tif", zlib.error),
        ],
    )
    def test_exif_without_valid_payload_raises_handled_error(
        self,
        controller: ActionController,
        request: pytest.FixtureRequest,
        name: str,
        current_error: type[Exception],
    ) -> None:
        # The GUI only maps IndexError / ValueError to a "Reveal failed" message.
        request.applymarker(
            pytest.mark.xfail(
                raises=current_error,
                strict=True,
                reason="stegano.exifHeader.reveal leaks raw zlib/piexif errors",
            )
        )
        with pytest.raises((IndexError, ValueError)):
            controller.reveal(str(FIXTURES / name))

    @pytest.mark.xfail(
        raises=AssertionError,
        strict=True,
        reason="EXIF payload is zlib-decompressed without any size limit",
    )
    def test_decompression_bomb_is_rejected(self, controller: ActionController) -> None:
        try:
            ok, text = controller.reveal(str(FIXTURES / "bomb.jpg"))
        except ValueError:
            return
        assert not ok
        assert len(text) <= MAX_REVEALED_LENGTH
