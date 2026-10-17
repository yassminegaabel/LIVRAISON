import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.errors import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    register_exception_handlers,
)

REGISTER = "/api/v1/auth/register"


def assert_error_shape(body: dict, code: str) -> dict:
    assert set(body) == {"error"}
    assert body["error"]["code"] == code
    assert isinstance(body["error"]["message"], str) and body["error"]["message"]
    return body["error"]


@pytest.fixture()
def error_client():
    """Mini-application de test dont les routes lèvent des erreurs."""
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/not-found")
    def not_found():
        raise NotFoundError("Produit introuvable")

    @test_app.get("/conflict")
    def conflict():
        raise ConflictError("Stock insuffisant", details={"available": 2})

    @test_app.get("/forbidden")
    def forbidden():
        raise ForbiddenError()

    @test_app.get("/unauthorized")
    def unauthorized():
        raise UnauthorizedError()

    @test_app.get("/boom")
    def boom():
        raise RuntimeError("secret internal detail: db password is hunter2")

    with TestClient(test_app, raise_server_exceptions=False) as test_client:
        yield test_client


def test_unknown_route_uses_standard_format(client):
    response = client.get("/this-route-does-not-exist")
    assert response.status_code == 404
    error = assert_error_shape(response.json(), "not_found")
    assert error["message"] == "Ressource introuvable"


def test_wrong_method_returns_405(client):
    response = client.get("/api/v1/auth/login")
    assert response.status_code == 405
    assert_error_shape(response.json(), "method_not_allowed")


def test_unauthorized_keeps_standard_format_and_header(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert_error_shape(response.json(), "unauthorized")
    assert response.headers["www-authenticate"] == "Bearer"


def test_validation_error_lists_fields_and_never_echoes_the_password(client):
    password = "weakpassword"
    response = client.post(
        REGISTER,
        json={"first_name": "A", "last_name": "B", "email": "a@example.com", "password": password},
    )
    assert response.status_code == 422
    error = assert_error_shape(response.json(), "validation_error")
    fields = {item["field"] for item in error["details"]}
    assert "password" in fields
    assert password not in response.text


def test_model_level_validation_error_is_reported_on_body(client):
    response = client.post(
        REGISTER, json={"first_name": "A", "last_name": "B", "password": "Secret123"}
    )
    assert response.status_code == 422
    error = assert_error_shape(response.json(), "validation_error")
    assert error["details"][0]["field"] == "body"
    assert "email ou un téléphone" in error["details"][0]["message"]


def test_conflict_uses_standard_format(client):
    email = f"dup-{uuid.uuid4().hex[:10]}@example.com"
    data = {"first_name": "A", "last_name": "B", "email": email, "password": "Secret123"}
    assert client.post(REGISTER, json=data).status_code == 201
    response = client.post(REGISTER, json=data)
    assert response.status_code == 409
    assert_error_shape(response.json(), "conflict")


def test_app_errors_are_mapped_to_http_responses(error_client):
    response = error_client.get("/not-found")
    assert response.status_code == 404
    assert assert_error_shape(response.json(), "not_found")["message"] == "Produit introuvable"

    response = error_client.get("/conflict")
    assert response.status_code == 409
    error = assert_error_shape(response.json(), "conflict")
    assert error["details"] == {"available": 2}

    assert error_client.get("/forbidden").status_code == 403
    assert error_client.get("/unauthorized").status_code == 401


def test_unhandled_exception_returns_generic_500_without_internal_details(error_client):
    response = error_client.get("/boom")
    assert response.status_code == 500
    error = assert_error_shape(response.json(), "internal_error")
    assert error["message"] == "Erreur interne du serveur"
    assert "hunter2" not in response.text
    assert "RuntimeError" not in response.text
