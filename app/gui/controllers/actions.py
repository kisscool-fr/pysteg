from enum import StrEnum
from enum import auto

from PIL import Image
from stegano import exifHeader  # type: ignore
from stegano import lsb  # type: ignore
from stegano.lsb import generators  # type: ignore

from app.gui.models.mode import WindowModel

# Upper bound on the number of pixels we will process from an (untrusted) image.
# Bounds memory use and mitigates decompression-bomb style inputs before the
# stegano library loads the full image into memory.
MAX_IMAGE_PIXELS = 64_000_000


class Hiding(StrEnum):
    LSB = auto()
    EXIF = auto()


class Format(StrEnum):
    PNG = Hiding.LSB
    BMP = Hiding.LSB
    JPEG = Hiding.EXIF
    TIFF = Hiding.EXIF


class ActionController:
    def __init__(self, model: WindowModel):
        self.model = model

    def get_hiding_technique(self, pil_format: str | None) -> Hiding | None:
        try:
            return Format[pil_format or ""]  # type: ignore[return-value]
        except KeyError:
            return None

    def is_within_size_limit(self, im: Image.Image) -> bool:
        width, height = im.size
        return width * height <= MAX_IMAGE_PIXELS

    def hide(
        self, source: str, destination: str, text: str, plain_text: bool
    ) -> tuple[bool, str]:
        with Image.open(source) as im:
            technique = self.get_hiding_technique(im.format)
            if not self.is_within_size_limit(im):
                return False, "Image too large to process"
        match technique:
            case Hiding.LSB:
                lsb.hide(
                    source,
                    text,
                    generators.eratosthenes(),
                    auto_convert_rgb=True,
                ).save(destination)
            case Hiding.EXIF:
                exifHeader.hide(source, destination, secret_message=text)  # type: ignore
            case _:
                return False, "Unsupported image format"
        return (
            True,
            "Text hidden successfully" if plain_text else "Encryption successful",
        )

    def reveal(self, source: str) -> tuple[bool, str]:
        with Image.open(source) as im:
            technique = self.get_hiding_technique(im.format)
            if not self.is_within_size_limit(im):
                return False, "Image too large to process"
        match technique:
            case Hiding.LSB:
                text = lsb.reveal(source, generators.eratosthenes())
            case Hiding.EXIF:
                text = exifHeader.reveal(source).decode()  # type: ignore
            case _:
                return False, "Unsupported image format"
        return True, text
