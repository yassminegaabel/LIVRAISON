from sqlalchemy import CheckConstraint

from app.db.base import Base
import app.models  # noqa: F401  (enregistre les tables)


def test_expected_tables_are_registered():
    assert {"users", "refresh_tokens", "admins", "customers"} <= set(Base.metadata.tables)


def test_users_has_required_constraints():
    users = Base.metadata.tables["users"]
    check_names = {c.name for c in users.constraints if isinstance(c, CheckConstraint)}
    assert "ck_users_email_or_phone" in check_names
    assert "ck_users_role_valid" in check_names
    assert users.c.email.unique and users.c.phone.unique
    assert users.c.password_hash.nullable is False


def test_profile_tables_cascade_on_user_delete():
    for name in ("admins", "customers", "refresh_tokens"):
        fk = next(iter(Base.metadata.tables[name].foreign_keys))
        assert fk.ondelete == "CASCADE"
