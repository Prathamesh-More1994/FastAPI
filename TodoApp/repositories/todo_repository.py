from sqlalchemy.orm import Session

from ..models.todo import Todos


def create_todo(db: Session, todo: Todos) -> Todos:
    db.add(todo)
    db.commit()
    db.refresh(todo)

    return todo


def get_todos_by_owner(db: Session, user_id: int) -> list[Todos]:
    return db.query(Todos).filter(Todos.owner_id == user_id).all()


def get_todo_by_id_and_owner(db: Session, todo_id: int, user_id: int) -> Todos | None:
    return (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user_id)
        .first()
    )

def update_todo(db: Session, todo: Todos) -> Todos:
    db.add(todo)
    db.commit()
    db.refresh(todo)

    return todo

def delete_todo(db: Session, todo: Todos) -> None:
    db.delete(todo)
    db.commit()