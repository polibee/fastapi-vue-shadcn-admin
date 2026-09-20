from server.app.core.config import get_settings


def validate_password(password: str) -> str:
    minimum = get_settings().password_min_length
    if len(password) < minimum:
        raise ValueError(f"password must be at least {minimum} characters")
    if password.isspace():
        raise ValueError("password must contain a non-whitespace character")
    return password
