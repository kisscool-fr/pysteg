import pytest
from cryptography.hazmat.primitives.ciphers import CipherContext

from app.aes256 import Crypto

AES_IV_SIZE = 16  # AES-128 requires a 16-byte IV
AES_KEY_SIZE = 32  # AES-256 requires a 32-byte key


@pytest.fixture
def crypto() -> Crypto:
    return Crypto("test_key")


def test_get_secret_key(crypto: Crypto):
    secret_key = crypto.get_secret_key()
    assert isinstance(secret_key, bytes)
    assert len(secret_key) == AES_IV_SIZE


def test_get_encryptor(crypto: Crypto):
    # Generate test IV
    test_iv = b"\x00" * AES_IV_SIZE

    # Get encryptor
    encryptor = crypto.get_encryptor(test_iv)

    # Verify encryptor type
    assert isinstance(encryptor, CipherContext)

    # Test encryption functionality
    test_data = b"test message"
    encrypted = encryptor.update(test_data) + encryptor.finalize()

    # Verify encrypted data is different from input
    assert encrypted != test_data

    # Verify encrypted data is not empty
    assert len(encrypted) > 0


def test_get_decryptor(crypto: Crypto):
    # Generate test IV
    test_iv = b"\x00" * AES_IV_SIZE

    # Get decryptor
    decryptor = crypto.get_decryptor(test_iv)

    # Verify decryptor type
    assert isinstance(decryptor, CipherContext)

    # Test decryption functionality
    test_data = b"test message"
    encryptor = crypto.get_encryptor(test_iv)
    encrypted_data = encryptor.update(test_data) + encryptor.finalize()
    decrypted = decryptor.update(encrypted_data) + decryptor.finalize()

    # Verify decrypted data matches original input
    assert decrypted == test_data


def test_derive_key(crypto: Crypto):
    password = b"test_password"
    derived_key = crypto.derive_key(password)

    # Verify derived key is bytes and has correct length
    assert isinstance(derived_key, bytes)
    assert len(derived_key) == AES_KEY_SIZE


def test_verify_key(crypto: Crypto):
    password = b"test_password"
    derived_key = crypto.derive_key(password)

    # Verify the key matches
    assert crypto.verify_key(password, derived_key)

    # Verify a wrong password does not match
    assert not crypto.verify_key(b"wrong_password", derived_key)


def test_encrypt(crypto: Crypto):
    test_value = "test message"
    encrypted_value = crypto.encrypt(test_value)

    # Verify encrypted value is not the same as original
    assert encrypted_value != test_value

    # Verify encrypted value is a string
    assert isinstance(encrypted_value, str)


def test_decrypt(crypto: Crypto):
    test_value = "test message"
    encrypted_value = crypto.encrypt(test_value)

    decrypted_value = crypto.decrypt(encrypted_value)

    # Verify decrypted value matches original
    assert decrypted_value == test_value
