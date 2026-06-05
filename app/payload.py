from app.aes256 import Crypto


def prepare_payload(text: str, secret: str, *, plain_text: bool) -> str:
    if plain_text:
        return text
    return Crypto(secret).encrypt(text)


def extract_payload(hidden_text: str, secret: str, *, plain_text: bool) -> str:
    if plain_text:
        return hidden_text
    return Crypto(secret).decrypt(hidden_text)
