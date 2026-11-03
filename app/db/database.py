import os
from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# An absolute default keeps the API and Alembic on the same file
# regardless of the working directory.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{(PROJECT_ROOT / 'documents.db').as_posix()}",
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    with SessionLocal() as db:
        yield db
