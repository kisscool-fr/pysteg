import base64
from os import urandom

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

# Constants for AES-256 encryption
_SALT_SIZE = 16
_NONCE_SIZE = 12

# Argon2 parameters: memory_cost: 64 MiB, time_cost: 3 passes, lanes: 1 thread.
_ARGON2_MEMORY_COST = 65536
_ARGON2_TIME_COST = 3
_ARGON2_LANES = 1
_ARGON2_KEY_LENGTH = 32


class Crypto:
    def __init__(self, shared_secret: str):
        self._secret: bytes = shared_secret.encode("utf-8")
        self._salt: bytes = self.get_random_salt()

    def get_random_salt(self) -> bytes:
        return urandom(_SALT_SIZE)

    def derive_key(self, secret: bytes, *, salt: bytes | None = None) -> bytes:
        kdf = Argon2id(
            salt=salt if salt is not None else self._salt,
            length=_ARGON2_KEY_LENGTH,
            iterations=_ARGON2_TIME_COST,
            lanes=_ARGON2_LANES,
            memory_cost=_ARGON2_MEMORY_COST,
        )
        return kdf.derive(secret)

    def encrypt(self, value: str) -> str:
        nonce = urandom(_NONCE_SIZE)

        derived_key = self.derive_key(self._secret)
        aesgcm = AESGCM(derived_key)

        ciphertext = aesgcm.encrypt(nonce, value.encode("utf-8"), None)

        return base64.b64encode(self._salt + nonce + ciphertext).decode("utf-8")

    def decrypt(self, value: str) -> str:
        try:
            encrypted_data = base64.b64decode(value.encode("utf-8"))

            salt = encrypted_data[:_SALT_SIZE]
            nonce = encrypted_data[_SALT_SIZE : _SALT_SIZE + _NONCE_SIZE]
            ciphertext = encrypted_data[_SALT_SIZE + _NONCE_SIZE :]

            derived_key = self.derive_key(self._secret, salt=salt)
            aesgcm = AESGCM(derived_key)

            plaintext = aesgcm.decrypt(nonce, ciphertext, None)

            return plaintext.decode("utf-8")
        except (InvalidTag, ValueError) as err:
            raise ValueError("Decryption failed: Data has been tampered with") from err
