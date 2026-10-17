from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import RegisterRequest, UserPublic
from app.services import user_service

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
