from enum import StrEnum
from enum import auto

from PIL import Image
from stegano import exifHeader  # type: ignore
from stegano import lsb  # type: ignore
from stegano.lsb import generators  # type: ignore

from app.aes256 import Crypto
from app.gui.models.mode import WindowModel


class Hidding(StrEnum):
    LSB = auto()
    EXIF = auto()


class Format(StrEnum):
    PNG = Hidding.LSB
    BMP = Hidding.LSB
    JPEG = Hidding.EXIF
    TIFF = Hidding.EXIF


class ActionController:
    def __init__(self, model: WindowModel):
        self.model = model

    def get_hidding_technique(self, pil_format: str | None) -> Hidding | None:
        try:
            return Format[pil_format or ""]  # type: ignore[return-value]
        except KeyError:
            return None

    def encrypt(self) -> tuple[bool, str]:
        try:
            crypto = Crypto(self.model.secret)
            encrypted = crypto.encrypt(self.model.text)
            return True, encrypted
        except Exception as e:  # noqa: BLE001
            return False, str(e)

    def decrypt(self, encrypted_text: str) -> tuple[bool, str]:
        try:
            crypto = Crypto(self.model.secret)
            decrypted = crypto.decrypt(encrypted_text)
            return True, decrypted
        except Exception as e:  # noqa: BLE001
            return False, str(e)

    def hide(
        self, source: str, destination: str, text: str, plain_text: bool
    ) -> tuple[bool, str]:
        with Image.open(source) as im:
            technique = self.get_hidding_technique(im.format)
        match technique:
            case Hidding.LSB:
                lsb.hide(source, text, generators.eratosthenes()).save(destination)
            case Hidding.EXIF:
                exifHeader.hide(source, destination, secret_message=text)  # type: ignore
            case _:
                return False, "Unsupported image format"
        return (
            True,
            "Text hidden successfully" if plain_text else "Encryption successful",
        )

    def reveal(self, source: str) -> tuple[bool, str]:
        with Image.open(source) as im:
            technique = self.get_hidding_technique(im.format)
        match technique:
            case Hidding.LSB:
                text = lsb.reveal(source, generators.eratosthenes())
            case Hidding.EXIF:
                text = exifHeader.reveal(source).decode()  # type: ignore
            case _:
                return False, "Unsupported image format"
        return True, text
