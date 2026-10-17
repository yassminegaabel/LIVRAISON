from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import TokenError, decode_access_token
from app.db.session import get_db
from app.models import User, UserRole
from app.repositories import user_repository

bearer_scheme = HTTPBearer(
    auto_error=False,
    description="Collez l'access token obtenu avec POST /api/v1/auth/login",
)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Retourne l'utilisateur du token. Le rôle et l'état du compte viennent de la base,
    pas du token : une désactivation ou un changement de rôle est effectif immédiatement."""
    if credentials is None:
        raise _unauthorized("Non authentifié")
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (TokenError, KeyError, ValueError):
        raise _unauthorized("Token invalide ou expiré") from None

    user = user_repository.get_by_id(db, user_id)
    if user is None or not user.is_active:
        raise _unauthorized("Token invalide ou expiré")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole) -> Callable[..., User]:
    """Crée une dépendance qui n'autorise que les rôles indiqués (sinon 403)."""
    allowed = {role.value for role in roles}

    def dependency(user: CurrentUser) -> User:
        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès refusé : rôle insuffisant",
            )
        return user

    return dependency
