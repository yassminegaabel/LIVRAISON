from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Admin, Customer, User, UserRole


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_by_phone(db: Session, phone: str) -> User | None:
    return db.scalar(select(User).where(User.phone == phone))


def add_user(db: Session, user: User) -> User:
    """Ajoute l'utilisateur et envoie l'INSERT (flush) pour obtenir son id."""
    db.add(user)
    db.flush()
    return user


def add_customer(db: Session, customer: Customer) -> Customer:
    db.add(customer)
    db.flush()
    return customer


def get_profile_names(db: Session, user: User) -> tuple[str | None, str | None]:
    """Retourne (prénom, nom) depuis la table de profil du rôle, ou (None, None) si absente."""
    profile = None
    if user.role == UserRole.CUSTOMER.value:
        profile = db.get(Customer, user.id)
    elif user.role in (UserRole.ADMIN.value, UserRole.SUPPORT.value):
        profile = db.get(Admin, user.id)
    if profile is None:
        return None, None
    return profile.first_name, profile.last_name
