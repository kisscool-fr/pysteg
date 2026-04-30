from enum import StrEnum
from enum import auto

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
        data = lsb.hide(source, text, generators.eratosthenes())
        data.save(destination)
        return True, "Encryption successful"

    def reveal(self, source: str) -> tuple[bool, str]:
        text = lsb.reveal(source, generators.eratosthenes())
        return True, text
