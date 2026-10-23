from starlette import status

from .utils import *
from ..routers.auth import get_db, get_current_user, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM
from jose import jwt
from datetime import timedelta
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

app.dependency_overrides[get_db] = get_db
app.dependency_overrides[get_current_user] = get_current_user


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
async def test_get_current_user_valid_token(test_users):
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {'username': 'testuser', 'id': 1, 'user_role': 'admin'}

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role':'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as exeinfo:
        await get_current_user(token=token)

    assert exeinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exeinfo.value.detail == 'Could not validate credentials'

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

    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"

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