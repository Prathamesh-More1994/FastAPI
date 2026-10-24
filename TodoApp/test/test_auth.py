import asyncio
import pytest
from ..core import config
from starlette import status
from starlette.requests import Request
from .utils import *
from ..routers.auth import get_db, get_current_user, authenticate_user
from ..core.security import create_access_token
from ..core.config import SECRET_KEY, ALGORITHM
from jose import jwt
from datetime import timedelta
from fastapi import HTTPException
from fastapi.testclient import TestClient

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def create_request_with_cookie(token=None):
    headers = []

    if token:
        headers.append(
            (
                b"cookie",
                f"access_token={token}".encode()
            )
        )

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": headers,
    }

    return Request(scope)

def test_authenticate_user(test_users):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_users.username, 'testpassword', db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_users.username

    non_existent_user = authenticate_user('WrongUserName', 'testpassword', db)
    assert non_existent_user is False

    wrong_password_user = authenticate_user(test_users.username, 'wrongpassword', db)
    assert wrong_password_user is False


def test_create_access_token(test_users):
    username = 'testuser'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role

@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {
        "sub": "testuser",
        "id": 1,
        "role": "admin"
    }

    token = jwt.encode(
        encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    request = create_request_with_cookie(token)

    user = await get_current_user(request)

    assert user == {
        "username": "testuser",
        "id": 1,
        "user_role": "admin"
    }

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {
        "role": "user"
    }

    token = jwt.encode(
        encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    request = create_request_with_cookie(token)

    with pytest.raises(HTTPException) as exeinfo:
        await get_current_user(request)

    assert exeinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exeinfo.value.detail == "Could not validate credentials"

def test_login_for_access_token_success(test_users):
    client = TestClient(app)

    response = client.post(
        "/auth/token",
        data={
            "username": test_users.username,
            "password": "testpassword"
        }
    )

    assert response.status_code == 200

    response_data = response.json()
    assert response_data["message"] == "Login successful"

    assert "access_token" in response.cookies

    cookie = response.cookies["access_token"]
    assert cookie
    set_cookie = response.headers["set-cookie"]

    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie
    assert "Path=/" in set_cookie

def test_login_for_access_token_invalid_credentials(test_users):
    client = TestClient(app)

    response = client.post(
        "/auth/token",
        data={
            "username": test_users.username,
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401

def test_register_user_cannot_choose_admin_role():
    client = TestClient(app)

    response = client.post(
        "/auth/",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "testpassword",
            "phone_number": "9999999999"
        }
    )

    assert response.status_code == 201
    assert response.json()["role"] == "user"

@pytest.mark.asyncio
async def test_get_current_user_missing_cookie():
    request = create_request_with_cookie()

    with pytest.raises(HTTPException) as exeinfo:
        await get_current_user(request)

    assert exeinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exeinfo.value.detail == "Could not validate credentials"

def test_logout():
    client = TestClient(app)

    client.cookies.set("access_token", "fake-token")

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert response.json()["message"] == "Logout successful"

    set_cookie = response.headers.get("set-cookie")
    assert "access_token=" in set_cookie
    assert "Max-Age=0" in set_cookie

def test_login_sets_secure_cookie_when_enabled(test_users, monkeypatch):
    monkeypatch.setattr(config, "COOKIE_SECURE", True)

    client = TestClient(app)

    response = client.post(
        "/auth/token",
        data={
            "username": test_users.username,
            "password": "testpassword"
        }
    )

    assert response.status_code == 200

    set_cookie = response.headers["set-cookie"]

    assert "Secure" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie

def test_login_invalid_username():
    response = client.post(
        "/auth/token",
        data={
            "username": "does_not_exist",
            "password": "testpassword"
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Could not validate credentials"
    }


def test_login_invalid_password(test_users):
    response = client.post(
        "/auth/token",
        data={
            "username": "user1",
            "password": "wrong_password"
        }
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "detail": "Could not validate credentials"
    }

def test_get_current_user_invalid_token():
    request = Request({
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [
            (b"cookie", b"access_token=this-is-not-a-valid-jwt")
        ],
    })

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_current_user(request))

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"

def test_get_current_user_expired_token():
    token = create_access_token(
        username="user1",
        user_id=1,
        role="user",
        expires_delta=timedelta(seconds=-1)
    )

    request = Request({
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [
            ("cookie", f"access_token={token}".encode())
        ],
    })

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_current_user(request))

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"