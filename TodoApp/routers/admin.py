from typing import Annotated
from fastapi import Depends, HTTPException, Path, APIRouter
from sqlalchemy.orm import Session
from starlette import status
from ..database.dependencies import get_db
from ..schemas.todo import TodoResponse
from ..services.admin_service import get_all_todos, delete_todo
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

db_dependencies = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/todo', response_model=list[TodoResponse], status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependencies):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return get_all_todos(db)


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(user: user_dependency, db: db_dependencies, todo_id: int = Path(gt=0)):
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail="Authentication Failed")

    todo_model = delete_todo(db, todo_id)

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')