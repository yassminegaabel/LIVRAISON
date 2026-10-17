import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update

from app.core.security import decode_access_token, hash_refresh_token
from app.models import RefreshToken, User

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
REFRESH = "/api/v1/auth/refresh"
LOGOUT = "/api/v1/auth/logout"
PASSWORD = "Secret123"


def create_user(client, **overrides) -> dict:
    data = {
        "first_name": "Yassmine",
        "last_name": "Test",
        "email": f"user-{uuid.uuid4().hex[:12]}@example.com",
        "password": PASSWORD,
    }
    data.update(overrides)
    response = client.post(REGISTER, json=data)
    assert response.status_code == 201
    return response.json()


def login(client, identifier, password=PASSWORD):
    return client.post(LOGIN, json={"identifier": identifier, "password": password})


def test_login_with_email_returns_tokens(client):
    user = create_user(client)
    response = login(client, user["email"])
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] > 0
    payload = decode_access_token(body["access_token"])
    assert payload["sub"] == str(user["id"])
    assert payload["role"] == "customer"


def test_login_is_case_insensitive_for_email(client):
    user = create_user(client)
    assert login(client, user["email"].upper()).status_code == 200


def test_login_with_phone(client):
    phone = "+216" + str(uuid.uuid4().int)[:8]
    create_user(client, phone=phone, email=None)
    assert login(client, phone).status_code == 200


def test_wrong_password_and_unknown_user_give_same_error(client):
    user = create_user(client)
    wrong = login(client, user["email"], "WrongPass123")
    unknown = login(client, "nobody-here@example.com")
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_inactive_account_cannot_login(client, db_session):
    user = create_user(client)
    db_session.execute(update(User).where(User.id == user["id"]).values(is_active=False))
    assert login(client, user["email"]).status_code == 403
    assert login(client, user["email"], "WrongPass123").status_code == 401


def test_login_updates_last_login_and_stores_refresh_token_hashed(client, db_session):
    user = create_user(client)
    tokens = login(client, user["email"]).json()
    db_user = db_session.get(User, user["id"])
    assert db_user.last_login_at is not None
    stored = db_session.scalar(select(RefreshToken).where(RefreshToken.user_id == user["id"]))
    assert stored.token_hash != tokens["refresh_token"]
    assert stored.token_hash == hash_refresh_token(tokens["refresh_token"])


def test_refresh_rotates_tokens(client):
    user = create_user(client)
    first = login(client, user["email"]).json()
    response = client.post(REFRESH, json={"refresh_token": first["refresh_token"]})
    assert response.status_code == 200
    second = response.json()
    assert second["refresh_token"] != first["refresh_token"]
    assert decode_access_token(second["access_token"])["sub"] == str(user["id"])


def test_refresh_with_unknown_token_is_rejected(client):
    response = client.post(REFRESH, json={"refresh_token": "this-token-does-not-exist"})
    assert response.status_code == 401


def test_refresh_with_expired_token_is_rejected(client, db_session):
    user = create_user(client)
    tokens = login(client, user["email"]).json()
    db_session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user["id"])
        .values(expires_at=datetime.now(UTC) - timedelta(minutes=1))
    )
    assert client.post(REFRESH, json={"refresh_token": tokens["refresh_token"]}).status_code == 401


def test_reusing_an_old_refresh_token_revokes_the_whole_session(client):
    user = create_user(client)
    first = login(client, user["email"]).json()
    second = client.post(REFRESH, json={"refresh_token": first["refresh_token"]}).json()

    reuse = client.post(REFRESH, json={"refresh_token": first["refresh_token"]})
    assert reuse.status_code == 401
    # Le token le plus récent est aussi révoqué par précaution.
    latest = client.post(REFRESH, json={"refresh_token": second["refresh_token"]})
    assert latest.status_code == 401


def test_logout_revokes_refresh_token(client):
    user = create_user(client)
    tokens = login(client, user["email"]).json()
    assert client.post(LOGOUT, json={"refresh_token": tokens["refresh_token"]}).status_code == 204
    assert client.post(REFRESH, json={"refresh_token": tokens["refresh_token"]}).status_code == 401


def test_logout_with_unknown_token_is_harmless(client):
    assert client.post(LOGOUT, json={"refresh_token": "unknown-token"}).status_code == 204
