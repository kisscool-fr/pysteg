from pathlib import Path

from app.constants import SHARED_SECRET_MIN_LENGTH


class InputValidator:
    @staticmethod
    def validate_secret(secret: str) -> tuple[bool, str]:
        if not secret.strip():
            return False, "Shared secret cannot be empty."
        if len(secret) < SHARED_SECRET_MIN_LENGTH:
            return False, "Shared secret must be at least 8 characters long."
        return True, ""

    @staticmethod
    def validate_output_file(source: str, destination: str) -> tuple[bool, str]:
        if not destination.strip():
            return False, "Please enter an output file name"
        if Path(destination).resolve() == Path(source).resolve():
            return False, "Output file must differ from input file"
        return True, ""
