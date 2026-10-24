from fastapi import status

from .utils import *
from ..main import app
from ..models.todo import Todos
from ..routers.todos import get_db, get_current_user
from datetime import timedelta
from ..core.security import create_access_token

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todos):
    response = client.get('/todos')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete': False,
                                'title': 'Learn to Code',
                                'description': 'Need to learn everyday',
                                'priority': 5,
                                'owner_id': 1,
                                'id': 1}]


def test_read_one_authenticated(test_todos):
    response = client.get('/todos/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'complete': False,
                               'title': 'Learn to Code',
                               'description': 'Need to learn everyday',
                               'priority': 5,
                               'owner_id': 1,
                               'id': 1}


def test_read_one_authenticated_not_found(test_todos):
    response = client.get('/todos/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not found'}


def test_create_todo(test_todos):
    request_data = {
        'title': 'New Todo!',
        'description': 'Need to learn everyday',
        'priority': 5,
        'complete': False,
        'owner_id': 1,
    }
    response = client.post('/todos', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = (db.query(Todos)
             .filter(Todos.id == 2)
             .first())
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')

def test_update_todo(test_todos):
    request_data = {
        'title': 'Change the title of the todo already saved!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'complete': False,
    }

    response = client.put('/todos/1', json=request_data)
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = (db.query(Todos)
             .filter(Todos.id == 1)
             .first())
    assert model.title == 'Change the title of the todo already saved!'

def test_update_todo_not_found(test_todos):
    request_data = {
        'title': 'Change the title of the todo already saved!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'complete': False,
    }

    response = client.put('/todos/999', json=request_data)
    assert response.status_code == 404

def test_delete_todo(test_todos):
    response = client.delete('/todos/1')
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = (db.query(Todos)
             .filter(Todos.id == 1)
             .first())
    assert model is None

def test_delete_todo_not_found():
    response = client.delete('/todos/999')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not found'}

def test_read_one_todo_owned_by_another_user(test_todos):
    db = TestingSessionLocal()

    other_todo = Todos(
        title="Other user's todo",
        description="This belongs to another user",
        priority=3,
        complete=False,
        owner_id=2,
    )

    db.add(other_todo)
    db.commit()
    db.refresh(other_todo)

    response = client.get(f'/todos/{other_todo.id}')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Not found'}


def test_update_todo_owned_by_another_user(test_todos):
    db = TestingSessionLocal()

    other_todo = Todos(
        title="Other user's todo",
        description="This belongs to another user",
        priority=3,
        complete=False,
        owner_id=2,
    )

    db.add(other_todo)
    db.commit()
    db.refresh(other_todo)

    request_data = {
        'title': 'Attempted unauthorized update',
        'description': 'Should not be allowed',
        'priority': 5,
        'complete': True,
    }

    response = client.put(
        f'/todos/{other_todo.id}',
        json=request_data
    )

    assert response.status_code == 404
    assert response.json() == {'detail': 'Not found'}

    db.refresh(other_todo)
    assert other_todo.title == "Other user's todo"


def test_delete_todo_owned_by_another_user(test_todos):
    db = TestingSessionLocal()

    other_todo = Todos(
        title="Other user's todo",
        description="This belongs to another user",
        priority=3,
        complete=False,
        owner_id=2,
    )

    db.add(other_todo)
    db.commit()
    db.refresh(other_todo)

    response = client.delete(f'/todos/{other_todo.id}')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Not found'}

    db.refresh(other_todo)
    assert other_todo.id is not None

def test_create_todo_title_too_short():
    response = client.post(
        '/todos/',
        json={
            'title': 'ab',
            'description': 'Need to learn everyday',
            'priority': 5,
            'complete': False
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_todo_description_too_short():
    response = client.post(
        '/todos/',
        json={
            'title': 'Learn Python',
            'description': 'ab',
            'priority': 5,
            'complete': False
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_todo_description_too_long():
    response = client.post(
        '/todos/',
        json={
            'title': 'Learn Python',
            'description': 'a' * 101,
            'priority': 5,
            'complete': False
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_todo_priority_zero():
    response = client.post(
        '/todos/',
        json={
            'title': 'Learn Python',
            'description': 'Need to learn everyday',
            'priority': 0,
            'complete': False
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_todo_priority_six():
    response = client.post(
        '/todos/',
        json={
            'title': 'Learn Python',
            'description': 'Need to learn everyday',
            'priority': 6,
            'complete': False
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_todo_invalid_complete():
    response = client.post(
        '/todos/',
        json={
            'title': 'Learn Python',
            'description': 'Need to learn everyday',
            'priority': 5,
            'complete': 'not-a-bool'
        }
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

def test_render_todo_page_authenticated(test_todos):
    authenticated_client = get_authenticated_client()

    response = authenticated_client.get('/todos/todo-page')

    assert response.status_code == status.HTTP_200_OK
    assert "Learn to Code" in response.text


def test_render_add_todo_page_authenticated():
    authenticated_client = get_authenticated_client()

    response = authenticated_client.get('/todos/add-todo-page')

    assert response.status_code == status.HTTP_200_OK


def test_render_edit_todo_page_authenticated(test_todos):
    authenticated_client = get_authenticated_client()

    response = authenticated_client.get(
        f'/todos/edit-todo-page/{test_todos.id}'
    )

    assert response.status_code == status.HTTP_200_OK
    assert "Learn to Code" in response.text

#Helper
def get_authenticated_client():
    token = create_access_token(
        username="user1",
        user_id=1,
        role="admin",
        expires_delta=timedelta(minutes=20),
    )
    client.cookies.set("access_token", token)
    return client