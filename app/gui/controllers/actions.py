from enum import StrEnum
from enum import auto

from PIL import Image
from stegano import exifHeader  # type: ignore
from stegano import lsb  # type: ignore
from stegano.lsb import generators  # type: ignore

from app.gui.models.mode import WindowModel


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

    def hide(
        self, source: str, destination: str, text: str, plain_text: bool
    ) -> tuple[bool, str]:
        with Image.open(source) as im:
            technique = self.get_hiding_technique(im.format)
        match technique:
            case Hiding.LSB:
                lsb.hide(source, text, generators.eratosthenes()).save(destination)
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
        match technique:
            case Hiding.LSB:
                text = lsb.reveal(source, generators.eratosthenes())
            case Hiding.EXIF:
                text = exifHeader.reveal(source).decode()  # type: ignore
            case _:
                return False, "Unsupported image format"
        return True, text
