import base64
import os
from pathlib import Path

import pytest
from PIL import Image
from stegano import exifHeader  # type: ignore
from stegano import lsb  # type: ignore
from stegano.lsb import generators  # type: ignore

from app.capacity import EXIF_SEGMENT_LIMIT
from app.capacity import Capacity
from app.capacity import count_primes_below
from app.capacity import exif_capacity
from app.capacity import lsb_capacity
from app.capacity import measure
from app.capacity import payload_bytes
from app.gui.controllers.actions import ActionController
from app.gui.controllers.actions import Hiding
from app.gui.models.mode import WindowModel
from app.payload import estimate_payload
from app.payload import prepare_payload

FIXTURES = Path(__file__).parent / "fixtures"

PI_TEN_MILLION = 664_579  # exact number of primes below 10^7
PI_TEN_MILLION_FLOOR = 600_000
COMPRESSED_CEILING = 1_000
E_ACUTE_UTF8_BYTES = 2
HI_BYTES = 2
HALF = 0.5


@pytest.fixture
def controller() -> ActionController:
    return ActionController(WindowModel())


# ---------------------------------------------------------------------------
# Prime counting
# ---------------------------------------------------------------------------


class TestCountPrimes:
    @pytest.mark.parametrize(
        "n, expected", [(0, 0), (2, 0), (3, 1), (10, 4), (100, 25), (1000, 168)]
    )
    def test_exact_values(self, n: int, expected: int) -> None:
        assert count_primes_below(n) == expected

    def test_large_values_are_a_lower_bound(self) -> None:
        estimate = count_primes_below(10_000_000)
        assert PI_TEN_MILLION_FLOOR < estimate <= PI_TEN_MILLION


# ---------------------------------------------------------------------------
# LSB capacity matches what stegano can actually store
# ---------------------------------------------------------------------------


class TestLsbCapacity:
    def test_capacity_fits_and_one_more_byte_does_not(self, tmp_path: Path) -> None:
        source = tmp_path / "cover.png"
        Image.new("RGB", (40, 40), color=(10, 20, 30)).save(source)
        capacity = lsb_capacity(40, 40)
        assert capacity > 0

        image = lsb.hide(str(source), "a" * capacity, generators.eratosthenes())
        image.save(tmp_path / "out.png")
        revealed = lsb.reveal(str(tmp_path / "out.png"), generators.eratosthenes())
        assert revealed == "a" * capacity

        with pytest.raises(IndexError):
            lsb.hide(str(source), "a" * (capacity + 40), generators.eratosthenes())

    def test_tiny_image_has_no_room(self) -> None:
        assert lsb_capacity(1, 1) == 0


# ---------------------------------------------------------------------------
# EXIF capacity
# ---------------------------------------------------------------------------


class TestExifCapacity:
    def test_existing_exif_reduces_room(self) -> None:
        assert exif_capacity(0) == EXIF_SEGMENT_LIMIT
        assert exif_capacity(1000) == EXIF_SEGMENT_LIMIT - 1000

    @pytest.mark.parametrize("name", ["plain.jpg", "exif_nodesc.jpg"])
    def test_estimate_is_writable(
        self, controller: ActionController, tmp_path: Path, name: str
    ) -> None:
        info = controller.inspect(str(FIXTURES / name))
        room = exif_capacity(info.exif_size)
        # Random base64 barely compresses, so grow it until it reaches the room.
        size = room * 3 // 4
        message = base64.b64encode(os.urandom(size)).decode()
        while payload_bytes(Hiding.EXIF, message) > room:
            size -= 64
            message = base64.b64encode(os.urandom(size)).decode()

        exifHeader.hide(  # type: ignore
            str(FIXTURES / name), str(tmp_path / "out.jpg"), secret_message=message
        )

    def test_never_negative(self) -> None:
        assert exif_capacity(100_000) == 0

    def test_exif_payload_is_compressed(self) -> None:
        assert payload_bytes(Hiding.EXIF, "a" * 10_000) < COMPRESSED_CEILING

    def test_lsb_payload_is_utf8_length(self) -> None:
        assert payload_bytes(Hiding.LSB, "é") == E_ACUTE_UTF8_BYTES


# ---------------------------------------------------------------------------
# Payload estimate
# ---------------------------------------------------------------------------


class TestEstimatePayload:
    def test_plain_text_is_unchanged(self) -> None:
        assert estimate_payload("hello", plain_text=True) == "hello"

    @pytest.mark.parametrize("text", ["", "hello", "é" * 50, "x" * 1000])
    def test_encrypted_estimate_has_real_length(self, text: str) -> None:
        real = prepare_payload(text, "secret_8chars", plain_text=False)
        assert len(estimate_payload(text, plain_text=False)) == len(real)


# ---------------------------------------------------------------------------
# inspect + measure
# ---------------------------------------------------------------------------


class TestInspect:
    def test_png(self, controller: ActionController) -> None:
        info = controller.inspect(str(FIXTURES / "plain.png"))
        assert info.format == "PNG"
        assert info.technique == Hiding.LSB
        assert info.supported
        assert info.name == "plain.png"
        assert info.file_size > 0

    def test_jpeg(self, controller: ActionController) -> None:
        info = controller.inspect(str(FIXTURES / "plain.jpg"))
        assert info.technique == Hiding.EXIF

    def test_non_image_raises(self, controller: ActionController) -> None:
        with pytest.raises(OSError):
            controller.inspect(str(FIXTURES / "notimg.png"))

    def test_measure_reports_fit(self, controller: ActionController) -> None:
        info = controller.inspect(str(FIXTURES / "plain.png"))
        result = measure(info, "hi")
        assert result.used == HI_BYTES
        assert result.fits


class TestCapacity:
    def test_ratio_and_fit(self) -> None:
        assert Capacity(used=50, available=100).ratio == HALF
        assert not Capacity(used=101, available=100).fits

    def test_zero_available(self) -> None:
        assert Capacity(used=0, available=0).ratio == 1.0
