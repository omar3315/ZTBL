from fastapi import FastAPI
from .database.db import create_db_and_tables
from .routers import auth, users

app = FastAPI(title="JWT Oracle Auth")

app.add_event_handler("startup", create_db_and_tables)
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])

@app.get("/")
def greet():
    return "Server is runing"