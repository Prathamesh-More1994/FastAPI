from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pathlib import Path
from ..schemas.auth import CreateUserRequest
from ..schemas.user import UserResponse
from sqlalchemy.orm import Session
from starlette import status
from fastapi.templating import Jinja2Templates
from ..database.dependencies import get_db
from ..models.user import Users
from ..core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..core import config
from ..core.security import (
    hash_password,
    verify_password,
    create_access_token,
)

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


db_dependencies = Annotated[Session, Depends(get_db)]

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


## Pages ##
@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse(name="login.html", request=request)


@router.get("/register-page")
def render_register_page(request: Request):
    return templates.TemplateResponse(name="register.html", request=request)


## Endpoints ##
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        return False

    if not verify_password(password, user.hashed_password):
        return False

    return user

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

        return {
            "username": username,
            "id": user_id,
            "user_role": user_role
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_user_or_none(request: Request):
    try:
        return await get_current_user(request)
    except HTTPException:
        return None

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependencies, create_user_request: CreateUserRequest):
    create_user_model = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=hash_password(create_user_request.password),
        role="user",
        is_active=True,
        phone_number=create_user_request.phone_number
    )
    db.add(create_user_model)
    db.commit()
    return create_user_model

@router.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependencies
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite="lax",
        path="/"
    )

    return {"message": "Login successful"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/"
    )
    return {"message": "Logout successful"}