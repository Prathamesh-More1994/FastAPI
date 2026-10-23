from sqlalchemy.orm import Session
from ..repositories import admin_repository
from ..models.todo import Todos


def get_all_todos(db: Session) -> list[Todos]:
    return admin_repository.get_all_todos(db)


def delete_todo(db: Session, todo_id: int) -> Todos | None:
    return admin_repository.delete_todo(db, todo_id)