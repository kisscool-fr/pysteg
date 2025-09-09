from app.aes256 import Crypto
from app.gui.models.mode import WindowModel


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
