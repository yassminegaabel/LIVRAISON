import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from app.core.config import settings

_password_hasher = PasswordHash.recommended()  # Argon2id

ACCESS_TOKEN_TYPE = "access"


class TokenError(Exception):
    """Token invalide, expiré ou falsifié."""


def hash_password(password: str) -> str:
    """Retourne le hash Argon2 du mot de passe (le mot de passe n'est jamais stocké)."""
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Compare un mot de passe saisi avec le hash stocké."""
    try:
        return _password_hasher.verify(password, password_hash)
    except UnknownHashError:
        return False


def create_access_token(
    subject: int | str, role: str, expires_delta: timedelta | None = None
) -> str:
    """Crée un JWT d'accès de courte durée contenant l'id utilisateur et son rôle."""
    now = datetime.now(UTC)
    lifetime = expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(subject),
        "role": role,
        "type": ACCESS_TOKEN_TYPE,
        "iat": now,
        "exp": now + lifetime,
        "jti": secrets.token_hex(8),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Vérifie la signature et la date d'expiration ; lève TokenError sinon."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "iat", "sub"]},
        )
    except jwt.PyJWTError as exc:
        raise TokenError("Token invalide ou expiré") from exc
    if payload.get("type") != ACCESS_TOKEN_TYPE:
        raise TokenError("Type de token incorrect")
    return payload


def hash_refresh_token(raw_token: str) -> str:
    """Hash SHA-256 d'un refresh token (seul le hash est stocké en base)."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def generate_refresh_token() -> tuple[str, str]:
    """Retourne (token_brut_pour_le_client, hash_pour_la_base)."""
    raw = secrets.token_urlsafe(48)
    return raw, hash_refresh_token(raw)


def refresh_token_expiry() -> datetime:
    return datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
