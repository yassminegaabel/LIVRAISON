from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=1, max_length=255, description="Email ou téléphone")
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1, max_length=512)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Durée de vie du access token, en secondes")


class MeResponse(BaseModel):
    """Profil de l'utilisateur connecté (le prénom et le nom dépendent du rôle)."""

    id: int
    email: str | None
    phone: str | None
    role: str
    is_active: bool
    first_name: str | None
    last_name: str | None
    created_at: datetime
