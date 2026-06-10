from pathlib import Path

import pytest
from PIL import Image
from stegano import lsb  # type: ignore
from stegano.lsb import generators  # type: ignore

from app.payload import extract_payload
from app.payload import prepare_payload

SECRET = "test_secret_8chars"


@pytest.fixture
def sample_png(tmp_path: Path) -> Path:
    path = tmp_path / "sample.png"
    Image.new("RGB", (256, 256), color=(64, 128, 192)).save(path)
    return path


def test_prepare_payload_plain_text_returns_unchanged():
    text = "hello world"
    assert prepare_payload(text, "", plain_text=True) == text


def test_prepare_payload_encrypted_differs_from_plaintext():
    text = "hello world"
    encrypted = prepare_payload(text, SECRET, plain_text=False)
    assert encrypted != text


def test_extract_payload_plain_text_returns_unchanged():
    text = "hidden message"
    assert extract_payload(text, "", plain_text=True) == text


def test_extract_payload_encrypted_round_trip():
    text = "secret message"
    encrypted = prepare_payload(text, SECRET, plain_text=False)
    assert extract_payload(encrypted, SECRET, plain_text=False) == text


def test_plain_text_mode_does_not_decrypt_encrypted_payload():
    text = "secret message"
    encrypted = prepare_payload(text, SECRET, plain_text=False)
    result = extract_payload(encrypted, "", plain_text=True)
    assert result == encrypted
    assert result != text


def test_encrypted_mode_fails_on_plain_payload():
    text = "plain message"
    with pytest.raises(ValueError):
        extract_payload(text, SECRET, plain_text=False)


def test_plain_text_lsb_round_trip(sample_png: Path):
    text = "plain steganography"
    payload = prepare_payload(text, "", plain_text=True)
    hidden_path = sample_png.with_name("sample_hidden.png")

    hidden_image = lsb.hide(str(sample_png), payload, generators.eratosthenes())
    hidden_image.save(hidden_path)

    revealed = lsb.reveal(str(hidden_path), generators.eratosthenes())
    assert extract_payload(revealed, "", plain_text=True) == text


def test_encrypted_lsb_round_trip(sample_png: Path):
    text = "encrypted steganography"
    payload = prepare_payload(text, SECRET, plain_text=False)
    hidden_path = sample_png.with_name("sample_hidden.png")

    hidden_image = lsb.hide(str(sample_png), payload, generators.eratosthenes())
    hidden_image.save(hidden_path)

    revealed = lsb.reveal(str(hidden_path), generators.eratosthenes())
    assert extract_payload(revealed, SECRET, plain_text=False) == text
