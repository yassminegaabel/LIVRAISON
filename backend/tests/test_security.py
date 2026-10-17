from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    TokenError,
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


def test_password_is_hashed_and_verifiable():
    hashed = hash_password("Secret123!")
    assert hashed != "Secret123!"
    assert verify_password("Secret123!", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_same_password_gives_different_hashes():
    assert hash_password("Secret123!") != hash_password("Secret123!")


def test_verify_password_with_invalid_hash_returns_false():
    assert verify_password("Secret123!", "not-a-valid-hash") is False


def test_access_token_roundtrip():
    token = create_access_token(42, "customer")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "customer"
    assert payload["type"] == "access"


def test_expired_token_is_rejected():
    token = create_access_token(1, "admin", expires_delta=timedelta(seconds=-5))
    with pytest.raises(TokenError):
        decode_access_token(token)


def test_tampered_token_is_rejected():
    token = create_access_token(1, "customer")
    with pytest.raises(TokenError):
        decode_access_token(token[:-3] + "abc")


def test_token_signed_with_other_key_is_rejected():
    now = datetime.now(UTC)
    forged = jwt.encode(
        {"sub": "1", "role": "admin", "type": "access", "iat": now, "exp": now + timedelta(minutes=5)},
        "x" * 40,
        algorithm="HS256",
    )
    with pytest.raises(TokenError):
        decode_access_token(forged)


def test_unsigned_token_is_rejected():
    now = datetime.now(UTC)
    unsigned = jwt.encode(
        {"sub": "1", "role": "admin", "type": "access", "iat": now, "exp": now + timedelta(minutes=5)},
        key=None,
        algorithm="none",
    )
    with pytest.raises(TokenError):
        decode_access_token(unsigned)


def test_token_of_wrong_type_is_rejected():
    now = datetime.now(UTC)
    other = jwt.encode(
        {"sub": "1", "role": "customer", "type": "refresh", "iat": now, "exp": now + timedelta(minutes=5)},
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(TokenError):
        decode_access_token(other)


def test_refresh_token_generation_and_hashing():
    raw, hashed = generate_refresh_token()
    assert raw != hashed
    assert hash_refresh_token(raw) == hashed
    assert len(hashed) == 64
    assert generate_refresh_token()[0] != raw
