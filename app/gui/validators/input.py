from app.constants import SHARED_SECRET_MIN_LENGTH


class InputValidator:
    @staticmethod
    def validate_secret(secret: str) -> tuple[bool, str]:
        if not secret.strip():
            return False, "Shared secret cannot be empty."
        if len(secret) < SHARED_SECRET_MIN_LENGTH:
            return False, "Shared secret must be at least 8 characters long."
        return True, ""
