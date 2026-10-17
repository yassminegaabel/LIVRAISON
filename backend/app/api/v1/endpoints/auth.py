from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.user import RegisterRequest, UserPublic
from app.services import auth_service, user_service

router = APIRouter()


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> UserPublic:
    """Inscription d'un client avec un email et/ou un téléphone."""
    try:
        user, customer = user_service.register_customer(db, payload)
    except user_service.DuplicateUserError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return UserPublic(
        id=user.id,
        email=user.email,
        phone=user.phone,
        role=user.role,
        first_name=customer.first_name,
        last_name=customer.last_name,
        created_at=user.created_at,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Connexion par email ou téléphone. Retourne un access token et un refresh token."""
    try:
        return auth_service.login(db, payload.identifier, payload.password)
    except auth_service.InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except auth_service.InactiveAccountError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Compte désactivé") from exc


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Échange un refresh token contre une nouvelle paire de tokens (l'ancien devient invalide)."""
    try:
        return auth_service.refresh(db, payload.refresh_token)
    except auth_service.InvalidRefreshTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)) -> None:
    """Déconnexion : révoque le refresh token."""
    auth_service.logout(db, payload.refresh_token)
