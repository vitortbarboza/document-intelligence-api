import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.services.document_service import (
    create_document,
    delete_document,
    update_document,
)


def test_create_document_service_commits_transaction(db_session, session_factory):
    # Create a document through the service layer.
    document_data = DocumentCreate(
        title="Transaction Test",
        description="Testing service commit",
    )

    created_document = create_document(
        db=db_session,
        document=document_data,
    )

    # Verify that the document received an ID.
    assert created_document.id is not None

    # Open a new session to verify that the document was committed.
    with session_factory() as verification_session:
        statement = select(Document).where(Document.id == created_document.id)

        persisted_document = verification_session.scalar(statement)

        assert persisted_document is not None
        assert persisted_document.title == "Transaction Test"
        assert persisted_document.description == "Testing service commit"


def test_create_document_service_calls_commit(db_session, monkeypatch):
    # Track calls to commit while preserving its original behavior.
    original_commit = db_session.commit
    commit_calls = []

    def tracked_commit():
        commit_calls.append(True)
        original_commit()

    monkeypatch.setattr(db_session, "commit", tracked_commit)

    document_data = DocumentCreate(
        title="Commit Test",
        description="Verify transaction ownership",
    )

    created_document = create_document(
        db=db_session,
        document=document_data,
    )

    assert created_document.id is not None
    assert len(commit_calls) == 1


def test_create_document_service_rolls_back_on_integrity_error(db_session):
    # Attempt to create a document that violates a database constraint.
    invalid_document = DocumentCreate(
        title="Invalid Document",
        description="Testing rollback",
    )

    # Bypass Pydantic validation to trigger a database-level error.
    invalid_document.title = None

    with pytest.raises(IntegrityError):
        create_document(
            db=db_session,
            document=invalid_document,
        )

    # Verify that the session can be reused after the service rollback.
    valid_document = DocumentCreate(
        title="Valid Document",
        description="Created after rollback",
    )

    created_document = create_document(
        db=db_session,
        document=valid_document,
    )

    assert created_document.id is not None
    assert created_document.title == "Valid Document"

    # Verify that the failed operation did not persist a document.
    documents = db_session.scalars(select(Document)).all()

    assert len(documents) == 1
    assert documents[0].title == "Valid Document"


def test_create_document_service_calls_rollback(db_session, monkeypatch):
    # Track rollback calls while preserving the original behavior.
    original_rollback = db_session.rollback
    rollback_calls = []

    def tracked_rollback():
        rollback_calls.append(True)
        original_rollback()

    monkeypatch.setattr(db_session, "rollback", tracked_rollback)

    # Create invalid data to trigger a database integrity error.
    invalid_document = DocumentCreate(
        title="Invalid Document",
        description="Testing rollback calls",
    )
    invalid_document.title = None

    with pytest.raises(IntegrityError):
        create_document(
            db=db_session,
            document=invalid_document,
        )

    # Verify that the service explicitly rolled back the transaction.
    assert len(rollback_calls) == 1


def test_update_document_service_calls_commit(db_session, monkeypatch):
    # Create a document before tracking the update transaction.
    document = create_document(
        db=db_session,
        document=DocumentCreate(
            title="Original Title",
            description="Original description",
        ),
    )

    original_commit = db_session.commit
    commit_calls = []

    def tracked_commit():
        commit_calls.append(True)
        original_commit()

    monkeypatch.setattr(db_session, "commit", tracked_commit)

    # Update the document through the service layer.
    updated_document = update_document(
        db=db_session,
        document_id=document.id,
        document_update=DocumentUpdate(title="Updated Title"),
    )

    assert updated_document is not None
    assert updated_document.title == "Updated Title"
    assert len(commit_calls) == 1


def test_delete_document_service_calls_commit(db_session, monkeypatch):
    # Create a document before tracking the delete transaction.
    document = create_document(
        db=db_session,
        document=DocumentCreate(
            title="Document to Delete",
            description="Testing delete commit",
        ),
    )

    original_commit = db_session.commit
    commit_calls = []

    def tracked_commit():
        commit_calls.append(True)
        original_commit()

    monkeypatch.setattr(db_session, "commit", tracked_commit)

    # Delete the document through the service layer.
    deleted = delete_document(
        db=db_session,
        document_id=document.id,
    )

    assert deleted is True
    assert len(commit_calls) == 1

    # Verify that the document no longer exists.
    assert db_session.get(Document, document.id) is None


def test_update_document_service_rolls_back_on_error(db_session, monkeypatch):
    # Create a valid document before simulating an update failure.
    document = create_document(
        db=db_session,
        document=DocumentCreate(
            title="Original Title",
            description="Original description",
        ),
    )

    original_flush = db_session.flush
    original_rollback = db_session.rollback
    rollback_calls = []

    def failing_flush(*args, **kwargs):
        raise RuntimeError("Simulated database failure")

    def tracked_rollback():
        rollback_calls.append(True)
        original_rollback()

    monkeypatch.setattr(db_session, "flush", failing_flush)
    monkeypatch.setattr(db_session, "rollback", tracked_rollback)

    # Attempt an update that fails before committing.
    with pytest.raises(RuntimeError, match="Simulated database failure"):
        update_document(
            db=db_session,
            document_id=document.id,
            document_update=DocumentUpdate(title="Updated Title"),
        )

    assert len(rollback_calls) == 1

    # Restore the original flush method before querying.
    monkeypatch.setattr(db_session, "flush", original_flush)

    # Verify that the original data was preserved.
    db_session.expire_all()
    stored_document = db_session.get(Document, document.id)

    assert stored_document is not None
    assert stored_document.title == "Original Title"


def test_delete_document_service_rolls_back_on_error(db_session, monkeypatch):
    # Create a document before simulating a delete failure.
    document = create_document(
        db=db_session,
        document=DocumentCreate(
            title="Document to Preserve",
            description="Testing delete rollback",
        ),
    )

    original_flush = db_session.flush
    original_rollback = db_session.rollback
    rollback_calls = []

    def failing_flush(*args, **kwargs):
        raise RuntimeError("Simulated database failure")

    def tracked_rollback():
        rollback_calls.append(True)
        original_rollback()

    monkeypatch.setattr(db_session, "flush", failing_flush)
    monkeypatch.setattr(db_session, "rollback", tracked_rollback)

    # Attempt to delete the document.
    with pytest.raises(RuntimeError, match="Simulated database failure"):
        delete_document(
            db=db_session,
            document_id=document.id,
        )

    # Verify that the service rolled back the transaction.
    assert len(rollback_calls) == 1

    # Restore normal database behavior.
    monkeypatch.setattr(db_session, "flush", original_flush)

    # Reload the document from the database.
    db_session.expire_all()
    stored_document = db_session.get(Document, document.id)

    # The document must still exist after rollback.
    assert stored_document is not None
    assert stored_document.title == "Document to Preserve"
