from typing import Annotated
from fastapi import Depends, HTTPException, Path, APIRouter, Request
from pathlib import Path
from ..schemas.todo import TodoRequest, TodoResponse
from ..services.todo_service import (
    create_todo,
    get_todos_by_owner,
    get_todo_by_id_and_owner,
    update_todo as update_todo_service,
    delete_todo as delete_todo_service
)
from sqlalchemy.orm import Session
from starlette import status
from ..database.dependencies import get_db
from .auth import get_current_user, get_current_user_or_none
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

router = APIRouter(
    prefix='/todos',
    tags=['todos']
)

db_dependencies = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


def redirect_to_login():
    redirect_response = RedirectResponse(url='/auth/login-page', status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key='access_token')
    return redirect_response


###Pages###
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependencies):
    user = await get_current_user_or_none(request)

    if user is None:
        return redirect_to_login()

    todos = get_todos_by_owner(db=db, user_id=user.get('id'))

    return templates.TemplateResponse(
        name="todo.html",
        request=request,
        context={"todos": todos, "user": user}
    )


@router.get('/add-todo-page')
async def render_add_todo_page(request: Request):
    user = await get_current_user_or_none(request)

    if user is None:
        return redirect_to_login()

    return templates.TemplateResponse(
        name="add-todo.html",
        request=request,
        context={"user": user}
    )


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(
    request: Request,
    todo_id: int,
    db: db_dependencies
):
    user = await get_current_user_or_none(request)

    if user is None:
        return redirect_to_login()

    todo = get_todo_by_id_and_owner(
        db=db,
        todo_id=todo_id,
        user_id=user.get('id')
    )

    if todo is None:
        return redirect_to_login()

    return templates.TemplateResponse(
        name="edit-todo.html",
        request=request,
        context={"todo": todo, "user": user}
    )


### EndPoints ###
@router.get("/", response_model=list[TodoResponse])
async def read_all(user: user_dependency, db: db_dependencies):
    return get_todos_by_owner(db=db, user_id=user.get('id'))


@router.get(
    "/{todo_id}", response_model=TodoResponse)
async def read_todo(user: user_dependency, db: db_dependencies, todo_id: int = Path(gt=0)):
    todo_model = get_todo_by_id_and_owner(
        db=db,
        todo_id=todo_id,
        user_id=user.get('id')
    )

    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Not found")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo_endpoint(
        user: user_dependency,
        db: db_dependencies,
        todo_request: TodoRequest
):
    create_todo(
        db=db,
        todo_request=todo_request,
        user_id=user.get('id')
    )


@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependencies, todo_request: TodoRequest, todo_id: int = Path(gt=0)):

    todo_model = get_todo_by_id_and_owner(
        db=db,
        todo_id=todo_id,
        user_id=user.get('id')
    )

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Not found")

    update_todo_service(
        db=db,
        todo_model=todo_model,
        todo_request=todo_request
    )


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependencies, todo_id: int = Path(gt=0)):
    todo_model = get_todo_by_id_and_owner(
        db=db,
        todo_id=todo_id,
        user_id=user.get('id')
    )

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Not found")

    delete_todo_service(
        db=db,
        todo_model=todo_model
    )