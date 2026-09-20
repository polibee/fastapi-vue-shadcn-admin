import pytest

from server.app.core.auth import hash_password, verify_password
from server.app.core.passwords import validate_password


def test_password_policy_rejects_short_passwords(monkeypatch) -> None:
    from server.app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "password_min_length", 8)
    with pytest.raises(ValueError):
        validate_password("short")


def test_password_hash_is_one_way_and_verifiable() -> None:
    encoded = hash_password("long-enough-password")

    assert encoded != "long-enough-password"
    assert verify_password("long-enough-password", encoded)
    assert not verify_password("wrong-password", encoded)
