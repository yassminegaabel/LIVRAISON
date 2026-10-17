import re
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    refresh_token_expiry,
    verify_password,
)
from app.models import RefreshToken, User
from app.repositories import refresh_token_repository, user_repository
from app.schemas.auth import TokenResponse

# Hash factice : on vérifie toujours un mot de passe, même si l'utilisateur n'existe pas,
# pour que le temps de réponse ne révèle pas si un compte existe.
_DUMMY_HASH = hash_password("dummy-password-for-timing")


class InvalidCredentialsError(Exception):
    """Identifiant ou mot de passe incorrect."""


class InactiveAccountError(Exception):
    """Le compte est désactivé."""


class InvalidRefreshTokenError(Exception):
    """Refresh token inconnu, expiré ou déjà utilisé."""


def _find_user(db: Session, identifier: str) -> User | None:
    identifier = identifier.strip()
    if "@" in identifier:
        return user_repository.get_by_email(db, identifier.lower())
    return user_repository.get_by_phone(db, re.sub(r"[ .\-]", "", identifier))


def _issue_tokens(db: Session, user: User) -> TokenResponse:
    raw_refresh, refresh_hash = generate_refresh_token()
    refresh_token_repository.add(
        db,
        RefreshToken(user_id=user.id, token_hash=refresh_hash, expires_at=refresh_token_expiry()),
    )
    return TokenResponse(
        access_token=create_access_token(user.id, user.role),
        refresh_token=raw_refresh,
        expires_in=settings.access_token_expire_minutes * 60,
    )


def login(db: Session, identifier: str, password: str) -> TokenResponse:
    user = _find_user(db, identifier)
    password_ok = verify_password(password, user.password_hash if user else _DUMMY_HASH)
    if user is None or not password_ok:
        raise InvalidCredentialsError()
    if not user.is_active:
        raise InactiveAccountError()

    user.last_login_at = datetime.now(UTC)
    tokens = _issue_tokens(db, user)
    db.commit()
    return tokens


def refresh(db: Session, raw_token: str) -> TokenResponse:
    """Renouvelle les tokens (rotation). Un token déjà utilisé révoque toute la session."""
    token = refresh_token_repository.get_by_hash_for_update(db, hash_refresh_token(raw_token))
    if token is None:
        raise InvalidRefreshTokenError()

    now = datetime.now(UTC)
    if token.revoked_at is not None:
        # Réutilisation d'un ancien token : il a peut-être été volé -> on révoque tous les tokens.
        refresh_token_repository.revoke_all_for_user(db, token.user_id, now)
        db.commit()
        raise InvalidRefreshTokenError()
    if token.expires_at <= now:
        raise InvalidRefreshTokenError()

    user = db.get(User, token.user_id)
    if user is None or not user.is_active:
        raise InvalidRefreshTokenError()

    token.revoked_at = now
    tokens = _issue_tokens(db, user)
    db.commit()
    return tokens


def logout(db: Session, raw_token: str) -> None:
    """Révoque le refresh token. Sans erreur si le token est inconnu ou déjà révoqué."""
    token = refresh_token_repository.get_by_hash_for_update(db, hash_refresh_token(raw_token))
    if token is not None and token.revoked_at is None:
        token.revoked_at = datetime.now(UTC)
        db.commit()
