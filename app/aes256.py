import base64
from os import urandom

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT_SIZE = 16
NONCE_SIZE = 12


class Crypto:
    def __init__(self, shared_secret: str):
        self._pwd: bytes = shared_secret.encode("utf-8")
        self._salt: bytes = self.get_salt()

    def get_salt(self) -> bytes:
        return urandom(SALT_SIZE)

    def derive_key(
        self, password: bytes, iterations: int = 100000, salt: bytes | None = None
    ) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt if salt is not None else self._salt,
            iterations=iterations,
            backend=default_backend(),
        )
        return kdf.derive(password)

    def encrypt(self, value: str) -> str:
        nonce = urandom(NONCE_SIZE)

        derived_key = self.derive_key(self._pwd)
        aesgcm = AESGCM(derived_key)

        ciphertext = aesgcm.encrypt(nonce, value.encode("utf-8"), None)

        return base64.b64encode(self._salt + nonce + ciphertext).decode("utf-8")

    def decrypt(self, value: str) -> str:
        try:
            encrypted_data = base64.b64decode(value.encode("utf-8"))

            salt = encrypted_data[:SALT_SIZE]
            nonce = encrypted_data[SALT_SIZE : SALT_SIZE + NONCE_SIZE]
            ciphertext = encrypted_data[SALT_SIZE + NONCE_SIZE :]

            derived_key = self.derive_key(self._pwd, salt=salt)
            aesgcm = AESGCM(derived_key)

            plaintext = aesgcm.decrypt(nonce, ciphertext, None)

            return plaintext.decode("utf-8")
        except (InvalidTag, ValueError) as err:
            raise ValueError("Decryption failed: Data has been tampered with") from err
