from sqlalchemy.orm import Session

from ..models.todo import Todos
from ..schemas.todo import TodoRequest
from ..repositories import todo_repository


def create_todo(db: Session, todo_request: TodoRequest, user_id: int) -> Todos:
    todo_model = Todos(**todo_request.model_dump(), owner_id=user_id)

    return todo_repository.create_todo(db, todo_model)

def get_todos_by_owner(db: Session, user_id: int) -> list[Todos]:
    return todo_repository.get_todos_by_owner(db, user_id)

def get_todo_by_id_and_owner(
    db: Session,
    todo_id: int,
    user_id: int
) -> Todos | None:
    return todo_repository.get_todo_by_id_and_owner(
        db=db,
        todo_id=todo_id,
        user_id=user_id
    )

def update_todo(
    db: Session,
    todo_model: Todos,
    todo_request: TodoRequest
) -> Todos:
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    return todo_repository.update_todo(db, todo_model)

def delete_todo(db: Session, todo_model: Todos) -> None:
    todo_repository.delete_todo(db, todo_model)