from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.db.session import get_db
from app.repositories import user_repository
from app.schemas.auth import MeResponse

router = APIRouter()


@router.get("/me", response_model=MeResponse)
def read_me(current_user: CurrentUser, db: Annotated[Session, Depends(get_db)]) -> MeResponse:
    """Profil de l'utilisateur connecté."""
    first_name, last_name = user_repository.get_profile_names(db, current_user)
    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        phone=current_user.phone,
        role=current_user.role,
        is_active=current_user.is_active,
        first_name=first_name,
        last_name=last_name,
        created_at=current_user.created_at,
    )
