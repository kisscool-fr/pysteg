import base64
from os import urandom

from app.aes256 import ENCRYPTION_OVERHEAD
from app.aes256 import Crypto


def estimate_payload(text: str, *, plain_text: bool) -> str:
    """Stand-in for ``prepare_payload`` with the same length and entropy.

    Lets the UI measure capacity on every keystroke without running Argon2id.
    """
    if plain_text:
        return text
    size = len(text.encode("utf-8")) + ENCRYPTION_OVERHEAD
    return base64.b64encode(urandom(size)).decode("ascii")


def prepare_payload(text: str, secret: str, *, plain_text: bool) -> str:
    if plain_text:
        return text
    return Crypto(secret).encrypt(text)


def extract_payload(hidden_text: str, secret: str, *, plain_text: bool) -> str:
    if plain_text:
        return hidden_text
    return Crypto(secret).decrypt(hidden_text)
