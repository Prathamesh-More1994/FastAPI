from .utils import *
from ..routers.users import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_users):
    response = client.get('/user')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'user1'
    assert response.json()['email'] == 'user1@email.com'
    assert response.json()['first_name'] == 'user1'
    assert response.json()['last_name'] == 'roby'
    assert response.json()['phone_number'] == '(111)-111-1111'

def test_change_password_success(test_users):
    response = client.put('/user/password',json={
        'password': 'testpassword',
        'new_password': 'newpassword'
    })
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_invalid(test_users):
    response = client.put('/user/password',json={
        'password': 'wrong_password',
        'new_password': 'newpassword'
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect Password'}

def test_change_phone_number_success(test_users):
    response = client.put('/user/phonenumber/2222222222')
    assert response.status_code == status.HTTP_204_NO_CONTENT
