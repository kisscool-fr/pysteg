import base64
from os import urandom

from cryptography.exceptions import InvalidKey
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT_SIZE = 16
NONCE_SIZE = 12


class Crypto:
    def __init__(self, shared_secret: str):
        self.salt: bytes = self.get_salt()
        self._pwd: bytes = shared_secret.encode("utf-8")
        self.derived_key: bytes = self.derive_key(self._pwd)

    def get_salt(self) -> bytes:
        return urandom(SALT_SIZE)

    def derive_key(
        self, password: bytes, iterations: int = 100000, salt: bytes | None = None
    ) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt if salt is not None else self.salt,
            iterations=iterations,
            backend=default_backend(),
        )
        return kdf.derive(password)

    def verify_key(self, password: bytes, key: bytes, iterations: int = 100000) -> bool:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=len(key),
            salt=self.salt,
            iterations=iterations,
            backend=default_backend(),
        )
        try:
            kdf.verify(password, key)
            return True
        except InvalidKey:
            return False

    def encrypt(self, value: str) -> str:
        nonce = urandom(NONCE_SIZE)

        aesgcm = AESGCM(self.derived_key)

        ciphertext = aesgcm.encrypt(nonce, value.encode("utf-8"), None)

        return base64.b64encode(self.salt + nonce + ciphertext).decode("utf-8")

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
