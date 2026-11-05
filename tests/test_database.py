import os
import subprocess
import sys

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import PROJECT_ROOT
from app.db import database
from app.db.database import get_db
from app.models.document import Document
from app.repositories import document_repository


# Import the database module in a fresh interpreter and return the path of the
# database file used by the engine.
# A subprocess avoids re-importing the module, which would redefine Base.
# The default URL is tested in test_config.py, isolated from any local .env;
# here the environment variable takes precedence over .env.
def read_database_path(working_directory, database_url):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    env["DATABASE_URL"] = database_url

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from app.db.database import engine; print(engine.url.database)",
        ],
        cwd=working_directory,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


# Verify that the engine uses DATABASE_URL, even when the process starts
# from another directory.
def test_database_url_from_environment(tmp_path):
    database_path = (tmp_path / "custom.db").as_posix()

    assert read_database_path(tmp_path, f"sqlite:///{database_path}") == database_path


# Verify the request lifecycle of the real get_db dependency: it yields a
# session and, when the request ends, closes it and discards uncommitted work.
def test_get_db_closes_session_and_discards_uncommitted_changes(
    session_factory,
    monkeypatch,
):
    monkeypatch.setattr(database, "SessionLocal", session_factory)

    dependency = get_db()
    db = next(dependency)

    assert isinstance(db, Session)

    # Flush without committing, as a failed request would.
    document_repository.create_document(
        db=db,
        title="Uncommitted",
        description="Discarded when the request ends",
    )

    assert db.in_transaction()

    # FastAPI resumes the generator after sending the response.
    with pytest.raises(StopIteration):
        next(dependency)

    assert not db.in_transaction()

    with session_factory() as verification_session:
        assert verification_session.scalars(select(Document)).all() == []
