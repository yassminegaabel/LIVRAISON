import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

PHONE_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")  # format international E.164


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = None
    password: str = Field(min_length=8, max_length=128)

    @field_validator("first_name", "last_name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Ne peut pas être vide")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = re.sub(r"[ .\-]", "", value)
        if not PHONE_PATTERN.match(cleaned):
            raise ValueError("Téléphone invalide : utilisez le format international, ex. +21612345678")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
            raise ValueError("Le mot de passe doit contenir au moins une lettre et un chiffre")
        return value

    @model_validator(mode="after")
    def require_email_or_phone(self) -> "RegisterRequest":
        if not self.email and not self.phone:
            raise ValueError("Un email ou un téléphone est obligatoire")
        return self


class UserPublic(BaseModel):
    """Informations publiques d'un utilisateur (jamais de mot de passe ni de hash)."""

    id: int
    email: str | None
    phone: str | None
    role: str
    first_name: str
    last_name: str
    created_at: datetime
