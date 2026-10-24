from fastapi import FastAPI, Request, status
from .routers import auth, todos, admin, users
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def test(request: Request):
    return RedirectResponse(url="/todos/todo-page",status_code=status.HTTP_302_FOUND)

@app.get("/healthy")
def health_check():
    return {"status": "healthy"}

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
