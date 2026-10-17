from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Customer, User


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
