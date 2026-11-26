from dataclasses import dataclass
from enum import StrEnum
from enum import auto
from pathlib import Path

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


@dataclass(frozen=True)
class ImageInfo:
    path: str
    format: str
    technique: Hiding | None
    width: int
    height: int
    file_size: int
    exif_size: int

    @property
    def name(self) -> str:
        return Path(self.path).name

    @property
    def supported(self) -> bool:
        return self.technique is not None

    @property
    def within_size_limit(self) -> bool:
        return self.width * self.height <= MAX_IMAGE_PIXELS


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

    def inspect(self, source: str) -> ImageInfo:
        """Read an image's header without decoding its pixels.

        Raises the same errors as ``Image.open`` for missing or non-image files.
        """
        with Image.open(source) as im:
            exif = im.info.get("exif", b"")
            return ImageInfo(
                path=source,
                format=im.format or "",
                technique=self.get_hiding_technique(im.format),
                width=im.size[0],
                height=im.size[1],
                file_size=Path(source).stat().st_size,
                exif_size=len(exif) if isinstance(exif, bytes) else 0,
            )

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
