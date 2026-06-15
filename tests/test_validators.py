from pathlib import Path

import pytest

from app.gui.validators.input import InputValidator

# ---------------------------------------------------------------------------
# validate_secret
# ---------------------------------------------------------------------------


class TestValidateSecret:
    def test_valid_secret_returns_true(self) -> None:
        ok, msg = InputValidator.validate_secret("strongpass")
        assert ok is True
        assert msg == ""

    def test_empty_secret_returns_false(self) -> None:
        ok, msg = InputValidator.validate_secret("")
        assert ok is False
        assert msg

    def test_whitespace_only_secret_returns_false(self) -> None:
        ok, msg = InputValidator.validate_secret("   ")
        assert ok is False
        assert msg

    def test_too_short_secret_returns_false(self) -> None:
        ok, msg = InputValidator.validate_secret("short")
        assert ok is False
        assert msg


# ---------------------------------------------------------------------------
# validate_output_file
# ---------------------------------------------------------------------------


class TestValidateOutputFile:
    def test_valid_different_paths_returns_true(self, tmp_path: Path) -> None:
        source = str(tmp_path / "photo.png")
        destination = str(tmp_path / "photo_hidden.png")
        ok, msg = InputValidator.validate_output_file(source, destination)
        assert ok is True
        assert msg == ""

    def test_empty_destination_returns_false(self, tmp_path: Path) -> None:
        source = str(tmp_path / "photo.png")
        ok, msg = InputValidator.validate_output_file(source, "")
        assert ok is False
        assert msg

    def test_whitespace_only_destination_returns_false(self, tmp_path: Path) -> None:
        source = str(tmp_path / "photo.png")
        ok, msg = InputValidator.validate_output_file(source, "   ")
        assert ok is False
        assert msg

    def test_same_path_returns_false(self, tmp_path: Path) -> None:
        path = str(tmp_path / "photo.png")
        ok, msg = InputValidator.validate_output_file(path, path)
        assert ok is False
        assert msg

    def test_same_path_via_different_representations_returns_false(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "photo.png"
        path.touch()
        absolute = str(path)
        relative = (
            str(Path(absolute).relative_to(Path.cwd()))
            if path.is_relative_to(Path.cwd())
            else absolute
        )
        ok, msg = InputValidator.validate_output_file(absolute, relative)
        assert ok is False
        assert msg

    @pytest.mark.parametrize(
        "source, destination",
        [
            ("/images/photo.png", "/images/photo_hidden.png"),
            ("/images/photo.jpg", "/images/output.jpg"),
            ("/a/b/c.png", "/a/b/d.png"),
        ],
    )
    def test_parametrized_different_paths_return_true(
        self, source: str, destination: str
    ) -> None:
        ok, _ = InputValidator.validate_output_file(source, destination)
        assert ok is True
