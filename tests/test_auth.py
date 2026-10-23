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
