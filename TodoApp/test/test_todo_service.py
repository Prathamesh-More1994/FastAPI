from .utils import TestingSessionLocal, clean_database
from ..models.todo import Todos
from ..schemas.todo import TodoRequest
from ..services import todo_service


def test_create_todo(clean_database):
    db = TestingSessionLocal()

    todo_request = TodoRequest(
        title="Learn Python",
        description="Practice every day",
        priority=5,
        complete=False,
    )

    result = todo_service.create_todo(
        db=db,
        todo_request=todo_request,
        user_id=1,
    )

    assert result.id is not None
    assert result.title == "Learn Python"
    assert result.owner_id == 1

    db.close()


def test_get_todos_by_owner(clean_database):
    db = TestingSessionLocal()

    todo1 = Todos(
        title="Todo 1",
        description="Description 1",
        priority=3,
        complete=False,
        owner_id=1,
    )
    todo2 = Todos(
        title="Todo 2",
        description="Description 2",
        priority=4,
        complete=True,
        owner_id=1,
    )
    todo3 = Todos(
        title="Todo 3",
        description="Description 3",
        priority=5,
        complete=False,
        owner_id=2,
    )

    db.add_all([todo1, todo2, todo3])
    db.commit()

    result = todo_service.get_todos_by_owner(db=db, user_id=1)

    assert len(result) == 2
    assert all(todo.owner_id == 1 for todo in result)

    db.close()


def test_get_todo_by_id_and_owner(clean_database):
    db = TestingSessionLocal()

    todo = Todos(
        title="Learn Python",
        description="Practice every day",
        priority=5,
        complete=False,
        owner_id=1,
    )

    db.add(todo)
    db.commit()
    db.refresh(todo)

    result = todo_service.get_todo_by_id_and_owner(
        db=db,
        todo_id=todo.id,
        user_id=1,
    )

    assert result is not None
    assert result.id == todo.id
    assert result.owner_id == 1

    db.close()


def test_get_todo_by_id_and_owner_rejects_wrong_owner(clean_database):
    db = TestingSessionLocal()

    todo = Todos(
        title="Private Todo",
        description="Owner only",
        priority=5,
        complete=False,
        owner_id=1,
    )

    db.add(todo)
    db.commit()
    db.refresh(todo)

    result = todo_service.get_todo_by_id_and_owner(
        db=db,
        todo_id=todo.id,
        user_id=2,
    )

    assert result is None

    db.close()


def test_update_todo(clean_database):
    db = TestingSessionLocal()

    todo = Todos(
        title="Learn Python",
        description="Practice every day",
        priority=3,
        complete=False,
        owner_id=1,
    )

    db.add(todo)
    db.commit()
    db.refresh(todo)

    todo_request = TodoRequest(
        title="Learn Advanced Python",
        description="Practice every day",
        priority=5,
        complete=True,
    )

    result = todo_service.update_todo(
        db=db,
        todo_model=todo,
        todo_request=todo_request,
    )

    assert result.title == "Learn Advanced Python"
    assert result.priority == 5
    assert result.complete is True

    db.close()


def test_delete_todo(clean_database):
    db = TestingSessionLocal()

    todo = Todos(
        title="Delete Me",
        description="This todo will be deleted",
        priority=3,
        complete=False,
        owner_id=1,
    )

    db.add(todo)
    db.commit()
    db.refresh(todo)

    todo_service.delete_todo(
        db=db,
        todo_model=todo,
    )

    result = db.query(Todos).filter(Todos.id == todo.id).first()

    assert result is None

    db.close()