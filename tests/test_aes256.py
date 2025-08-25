import pytest

from app.aes256 import Crypto

AES_IV_SIZE = 16  # AES-128 requires a 16-byte IV
AES_KEY_SIZE = 32  # AES-256 requires a 32-byte key


@pytest.fixture
def crypto() -> Crypto:
    return Crypto("test_key")


def test_get_salt(crypto: Crypto):
    secret_key = crypto.get_salt()
    assert isinstance(secret_key, bytes)
    assert len(secret_key) == AES_IV_SIZE


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

    decrypted_value = crypto.decrypt(crypto.encrypt(test_value))

    # Verify decrypted value matches original
    assert decrypted_value == test_value
