from sqlalchemy.orm import Session
from ..models.todo import Todos


def get_all_todos(db: Session) -> list[Todos]:
    return db.query(Todos).all()


def delete_todo(db: Session, todo_id: int) -> Todos | None:
    todo = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo is None:
        return None

    db.delete(todo)
    db.commit()

    return todo