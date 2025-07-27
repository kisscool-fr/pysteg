import base64
from os import urandom

from cryptography.exceptions import InvalidKey
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers import CipherContext
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers import modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Crypto:
    def __init__(self, key: str):
        self.key = key
        self.secret_key = self.get_secret_key()
        self.refresh_key()

    def get_secret_key(self) -> bytes:
        return urandom(16)
    
    def refresh_key(self):
        self.derived_key = self.derive_key(self.key.encode("utf-8"))

    def get_encryptor(self, iv: bytes) -> CipherContext:
        return Cipher(
            algorithms.AES(self.derived_key), modes.CFB(iv), backend=default_backend()
        ).encryptor()

    def get_decryptor(self, iv: bytes) -> CipherContext:
        return Cipher(
            algorithms.AES(self.derived_key), modes.CFB(iv), backend=default_backend()
        ).decryptor()

    def derive_key(self, password: bytes, iterations: int = 100000) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.secret_key,
            iterations=iterations,
            backend=default_backend(),
        )
        return kdf.derive(password)

    def verify_key(self, password: bytes, key: bytes, iterations: int = 100000) -> bool:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=len(key),
            salt=self.secret_key,
            iterations=iterations,
            backend=default_backend(),
        )
        try:
            kdf.verify(password, key)
            return True
        except InvalidKey:
            return False

    def encrypt(self, value: str) -> str:
        iv = urandom(16)
        padder = padding.PKCS7(algorithms.AES(self.derived_key).block_size).padder()
        padded_data = padder.update(value.encode("utf-8")) + padder.finalize()
        encryptor = self.get_encryptor(iv)
        encrypted_text = encryptor.update(padded_data) + encryptor.finalize()
        return base64.b64encode(iv + self.secret_key + encrypted_text).decode("utf-8")

    def decrypt(self, value: str) -> str:
        encrypted_data_bytes = base64.b64decode(value.encode("utf-8"))

        iv = encrypted_data_bytes[:16]
        self.secret_key = encrypted_data_bytes[16:32]
        ciphertext = encrypted_data_bytes[32:]

        self.refresh_key()

        padder = padding.PKCS7(algorithms.AES(self.derived_key).block_size).unpadder()
        decrypted_data = self.get_decryptor(iv).update(ciphertext)
        unpadded = padder.update(decrypted_data) + padder.finalize()
        return unpadded.decode("utf-8")
