import uuid
from datetime import timedelta

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import update

from app.api.deps import CurrentUser, require_roles
from app.core.security import create_access_token, hash_password
from app.db.session import get_db
from app.models import Admin, User, UserRole

PASSWORD = "Secret123"
PASSWORD_HASH = hash_password(PASSWORD)  # calculé une seule fois pour accélérer les tests


@pytest.fixture()
def rbac_client(db_session):
    """Mini-application de test avec des routes protégées par rôle (n'existe que dans les tests)."""
    test_app = FastAPI()

    @test_app.get("/whoami")
    def whoami(user: CurrentUser):
        return {"id": user.id, "role": user.role}

    @test_app.get("/admin-only")
    def admin_only(user: User = Depends(require_roles(UserRole.ADMIN))):
        return {"ok": True}

    @test_app.get("/staff")
    def staff(user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPPORT))):
        return {"ok": True}

    test_app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(test_app) as test_client:
        yield test_client


def make_user(db_session, role="customer", is_active=True) -> User:
    user = User(
        email=f"{role}-{uuid.uuid4().hex[:10]}@example.com",
        password_hash=PASSWORD_HASH,
        role=role,
        is_active=is_active,
    )
    db_session.add(user)
    db_session.flush()
    return user


def bearer(user_id: int, role: str, **kwargs) -> dict:
    return {"Authorization": f"Bearer {create_access_token(user_id, role, **kwargs)}"}


def test_missing_token_is_rejected(rbac_client):
    response = rbac_client.get("/whoami")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_garbage_token_is_rejected(rbac_client):
    response = rbac_client.get("/whoami", headers={"Authorization": "Bearer not-a-jwt"})
    assert response.status_code == 401


def test_expired_token_is_rejected(rbac_client, db_session):
    user = make_user(db_session)
    headers = bearer(user.id, user.role, expires_delta=timedelta(seconds=-5))
    assert rbac_client.get("/whoami", headers=headers).status_code == 401


def test_valid_token_identifies_the_user(rbac_client, db_session):
    user = make_user(db_session)
    response = rbac_client.get("/whoami", headers=bearer(user.id, user.role))
    assert response.status_code == 200
    assert response.json() == {"id": user.id, "role": "customer"}


def test_customer_is_forbidden_on_admin_route_but_admin_is_allowed(rbac_client, db_session):
    customer = make_user(db_session, "customer")
    admin = make_user(db_session, "admin")
    assert rbac_client.get("/admin-only", headers=bearer(customer.id, "customer")).status_code == 403
    assert rbac_client.get("/admin-only", headers=bearer(admin.id, "admin")).status_code == 200


def test_route_with_several_allowed_roles(rbac_client, db_session):
    support = make_user(db_session, "support")
    customer = make_user(db_session, "customer")
    assert rbac_client.get("/staff", headers=bearer(support.id, "support")).status_code == 200
    assert rbac_client.get("/staff", headers=bearer(customer.id, "customer")).status_code == 403


def test_deactivated_user_with_valid_token_is_rejected(rbac_client, db_session):
    user = make_user(db_session)
    headers = bearer(user.id, user.role)
    db_session.execute(update(User).where(User.id == user.id).values(is_active=False))
    assert rbac_client.get("/whoami", headers=headers).status_code == 401


def test_role_comes_from_database_not_from_token_claim(rbac_client, db_session):
    customer = make_user(db_session, "customer")
    # Token correctement signé mais qui prétend que le client est admin.
    response = rbac_client.get("/admin-only", headers=bearer(customer.id, "admin"))
    assert response.status_code == 403


def test_role_change_is_effective_immediately(rbac_client, db_session):
    user = make_user(db_session, "customer")
    headers = bearer(user.id, "customer")
    assert rbac_client.get("/admin-only", headers=headers).status_code == 403
    db_session.execute(update(User).where(User.id == user.id).values(role="admin"))
    assert rbac_client.get("/admin-only", headers=headers).status_code == 200


def test_me_returns_the_logged_in_customer(client):
    email = f"me-{uuid.uuid4().hex[:10]}@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"first_name": "Yassmine", "last_name": "Test", "email": email, "password": PASSWORD},
    )
    tokens = client.post(
        "/api/v1/auth/login", json={"identifier": email, "password": PASSWORD}
    ).json()
    response = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == email
    assert body["role"] == "customer"
    assert body["first_name"] == "Yassmine"
    assert "password_hash" not in body


def test_me_requires_authentication(client):
    assert client.get("/api/v1/users/me").status_code == 401


def test_me_returns_admin_profile(client, db_session):
    admin = make_user(db_session, "admin")
    db_session.add(Admin(user_id=admin.id, first_name="Ali", last_name="Admin"))
    db_session.flush()
    response = client.get("/api/v1/users/me", headers=bearer(admin.id, "admin"))
    assert response.status_code == 200
    assert response.json()["first_name"] == "Ali"
    assert response.json()["role"] == "admin"
