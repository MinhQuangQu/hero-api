import os
from typing import Annotated

from fastapi import Depends
from sqlalchemy import event
from sqlmodel import Session, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite") else {}
)
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
