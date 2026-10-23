from uuid import uuid4

import pytest

from api.auth import verify_password
from db.connection import get_connection


@pytest.fixture
def make_register():
    payload = {
        "name": "Registration Test User",
        "email": f"test@example.com",
        "password": "somepassword",
    }
    yield payload

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE email = %s", (payload["email"],))
    conn.commit()
    cur.close()
    conn.close()


def test_login_valid_credentials_returns_200_and_token(client):
    response = client.post("/api/auth/login",
                           json={"email": "bob@example.com", "password": "password123"})
    assert response.status_code == 200

    token = response.json()
    assert token.keys() == {"access_token", "token_type"}
    assert isinstance(token["access_token"], str)
    assert token["token_type"] == "bearer"


def test_login_user_missing_email_returns_400(client):
    response = client.post("/api/auth/login",
                           json={"password": "password123"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"


def test_login_user_email_none_returns_400(client):
    response = client.post("/api/auth/login",
                           json={"email": None, "password": "password123"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"


def test_login_user_email_empty_string_returns_400(client):
    response = client.post("/api/auth/login",
                           json={"email": "", "password": "password123"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"


def test_login_user_missing_password_returns_400(client):
    response = client.post("/api/auth/login",
                           json={"email": "bob@example.com"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"


def test_login_user_password_none_returns_400(client):
    response = client.post("/api/auth/login",
                           json={"email": "bob@example.com", "password": None})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"


def test_login_user_password_empty_string_returns_400(client):
    response = client.post("/api/auth/login",
                           json={"email": "bob@example.com", "password": ""})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"


def test_login_user_email_not_found_returns_401(client):
    response = client.post("/api/auth/login",
                           json={"email": "uniqueemail@example.com", "password": "password123"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_login_user_password_incorrect_returns_401(client):
    response = client.post("/api/auth/login",
                           json={"email": "bob@example.com", "password": "password1234"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_register_returns_created_user_without_password(client, make_register):
    response = client.post("/api/auth/register",
                           json=make_register)

    assert response.status_code == 201
    user = response.json()
    assert set(user) == {"id", "name", "email", "created_at"}
    assert user["name"] == make_register["name"]
    assert user["email"] == make_register["email"]
    assert "password" not in user

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT password FROM users WHERE email = %s",
        (make_register["email"],)
    )
    stored_password = cur.fetchone()[0]
    cur.close()
    conn.close()

    assert stored_password != make_register["password"]
    assert verify_password(
        make_register["password"], stored_password)


def test_register_duplicate_email_returns_409(client, make_register):
    first_response = client.post(
        "/api/auth/register", json=make_register)
    duplicate_response = client.post(
        "/api/auth/register", json=make_register)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409


@pytest.mark.parametrize("missing_field", ["name", "email", "password"])
def test_register_missing_required_field_returns_400(
    client, make_register, missing_field
):
    payload = make_register.copy()
    payload.pop(missing_field)

    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"


@pytest.mark.parametrize("empty_field", ["name", "email", "password"])
def test_register_empty_required_field_returns_400(
    client, make_register, empty_field
):
    payload = make_register.copy()
    payload[empty_field] = ""

    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"
