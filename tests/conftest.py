import pymupdf
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app
from app.models.document import Document  # noqa: F401  Registers the table in Base.metadata.


# Build an in-memory PDF with one page per text (an empty string adds a blank page).
@pytest.fixture
def make_pdf():
    def _make_pdf(*page_texts: str) -> bytes:
        document = pymupdf.open()

        for text in page_texts:
            page = document.new_page()

            if text:
                page.insert_text((72, 72), text)

        pdf_content = document.tobytes()
        document.close()

        return pdf_content

    return _make_pdf


# Create an isolated in-memory SQLite database for each test.
@pytest.fixture
def session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    try:
        yield sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
        )
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


# Session used by tests to call services directly or inspect the database.
@pytest.fixture
def db_session(session_factory):
    with session_factory() as session:
        yield session


@pytest.fixture
def db_client(session_factory):
    # Give each request its own session, as in production, so changes that
    # were never committed are discarded when the request ends.
    def override_get_db():
        with session_factory() as session:
            yield session

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)