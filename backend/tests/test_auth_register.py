import uuid

from sqlalchemy import select

from app.models import Customer, User

URL = "/api/v1/auth/register"


def unique_email() -> str:
    return f"user-{uuid.uuid4().hex[:12]}@example.com"


def unique_phone() -> str:
    return "+216" + str(uuid.uuid4().int)[:8]


def payload(**overrides) -> dict:
    data = {
        "first_name": "Yassmine",
        "last_name": "Test",
        "email": unique_email(),
        "password": "Secret123",
    }
    data.update(overrides)
    return data


def test_register_with_email_succeeds(client):
    response = client.post(URL, json=payload(email="Yass.Test@Example.com"))
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "yass.test@example.com"  # stocké en minuscules
    assert body["role"] == "customer"
    assert body["first_name"] == "Yassmine"
    assert "password" not in body and "password_hash" not in body


def test_register_with_phone_only_succeeds(client):
    phone = unique_phone()
    data = payload(phone=phone)
    del data["email"]
    response = client.post(URL, json=data)
    assert response.status_code == 201
    assert response.json()["phone"] == phone
    assert response.json()["email"] is None


def test_password_is_stored_hashed_and_profile_created(client, db_session):
    data = payload()
    user_id = client.post(URL, json=data).json()["id"]
    user = db_session.scalar(select(User).where(User.id == user_id))
    assert user.password_hash != data["password"]
    assert user.password_hash.startswith("$argon2")
    assert db_session.get(Customer, user_id).last_name == "Test"


def test_register_without_email_and_phone_is_rejected(client):
    data = payload()
    del data["email"]
    assert client.post(URL, json=data).status_code == 422


def test_duplicate_email_is_rejected_case_insensitively(client):
    email = unique_email()
    assert client.post(URL, json=payload(email=email)).status_code == 201
    response = client.post(URL, json=payload(email=email.upper()))
    assert response.status_code == 409


def test_duplicate_phone_is_rejected(client):
    phone = unique_phone()
    assert client.post(URL, json=payload(phone=phone)).status_code == 201
    assert client.post(URL, json=payload(phone=phone)).status_code == 409


def test_weak_passwords_are_rejected(client):
    assert client.post(URL, json=payload(password="short1")).status_code == 422
    assert client.post(URL, json=payload(password="onlyletters")).status_code == 422
    assert client.post(URL, json=payload(password="12345678")).status_code == 422


def test_invalid_email_and_phone_are_rejected(client):
    assert client.post(URL, json=payload(email="not-an-email")).status_code == 422
    assert client.post(URL, json=payload(phone="12345")).status_code == 422


def test_role_cannot_be_chosen_by_the_client(client):
    response = client.post(URL, json=payload(role="admin"))
    assert response.status_code == 201
    assert response.json()["role"] == "customer"
