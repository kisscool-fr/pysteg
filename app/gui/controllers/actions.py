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
    JPG = Hidding.EXIF
    TIFF = Hidding.EXIF


class ActionController:
    def __init__(self, model: WindowModel):
        self.model = model

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

    def hide(self, source: str, destination: str, text: str) -> tuple[bool, str]:
        im = Image.open(source)

        match im.format:
            case "PNG" | "BMP":
                data = lsb.hide(source, text, generators.eratosthenes())
                data.save(destination)
            case "JPEG" | "TIFF":
                exifHeader.hide(source, destination, secret_message=text)  # type: ignore
            case _:
                return False, "Unsupported image format"

        return True, "Encryption successful"

    def reveal(self, source: str) -> tuple[bool, str]:
        im = Image.open(source)
        match im.format:
            case "PNG" | "BMP":
                text = lsb.reveal(source, generators.eratosthenes())
            case "JPEG" | "TIFF":
                text = exifHeader.reveal(source).decode()  # type: ignore
            case _:
                return False, "Unsupported image format"

        return True, text
