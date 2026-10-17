from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import Customer, User, UserRole
from app.repositories import user_repository
from app.schemas.user import RegisterRequest


class DuplicateUserError(Exception):
    """Email ou téléphone déjà utilisé."""


def register_customer(db: Session, data: RegisterRequest) -> tuple[User, Customer]:
    """Crée un compte client (utilisateur + profil) dans une seule transaction."""
    email = data.email.lower() if data.email else None

    if email and user_repository.get_by_email(db, email):
        raise DuplicateUserError("Cet email est déjà utilisé")
    if data.phone and user_repository.get_by_phone(db, data.phone):
        raise DuplicateUserError("Ce numéro de téléphone est déjà utilisé")

    try:
        user = user_repository.add_user(
            db,
            User(
                email=email,
                phone=data.phone,
                password_hash=hash_password(data.password),
                role=UserRole.CUSTOMER.value,
            ),
        )
        customer = user_repository.add_customer(
            db,
            Customer(user_id=user.id, first_name=data.first_name, last_name=data.last_name),
        )
        db.commit()
    except IntegrityError as exc:  # course critique : deux inscriptions simultanées
        db.rollback()
        raise DuplicateUserError("Email ou téléphone déjà utilisé") from exc

    db.refresh(user)
    return user, customer
