from .utils import TestingSessionLocal, clean_database
from ..models.todo import Todos
from ..repositories import todo_repository


def test_create_todo(clean_database):
    db = TestingSessionLocal()

    todo = Todos(
        title="Learn Python",
        description="Practice every day",
        priority=5,
        complete=False,
        owner_id=1,
    )

    result = todo_repository.create_todo(db, todo)

    assert result.id is not None
    assert result.title == "Learn Python"
    assert result.owner_id == 1

    db.close()


def test_get_todos_by_owner(clean_database):
    db = TestingSessionLocal()

    todo1 = Todos(
        title="Learn Python",
        description="Practice every day",
        priority=5,
        complete=False,
        owner_id=1,
    )

    todo2 = Todos(
        title="Learn FastAPI",
        description="Build an API",
        priority=4,
        complete=False,
        owner_id=1,
    )

    todo3 = Todos(
        title="Other User Todo",
        description="Should not be returned",
        priority=3,
        complete=False,
        owner_id=2,
    )

    db.add_all([todo1, todo2, todo3])
    db.commit()

    result = todo_repository.get_todos_by_owner(db, user_id=1)

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

    result = todo_repository.get_todo_by_id_and_owner(
        db,
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
        description="Belongs to user 1",
        priority=5,
        complete=False,
        owner_id=1,
    )

    db.add(todo)
    db.commit()
    db.refresh(todo)

    result = todo_repository.get_todo_by_id_and_owner(
        db,
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

    todo.title = "Learn Advanced Python"
    todo.priority = 5
    todo.complete = True

    result = todo_repository.update_todo(db, todo)

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

    todo_repository.delete_todo(db, todo)

    result = db.query(Todos).filter(Todos.id == todo.id).first()

    assert result is None

    db.close()