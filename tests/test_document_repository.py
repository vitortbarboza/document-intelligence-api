import pytest
from sqlalchemy.exc import IntegrityError

from app.repositories.document_repository import (
    create_document,
    delete_document,
    get_all_documents,
    get_document_by_id,
    update_document,
)
from app.schemas.document import DocumentResponse


def test_create_document(db_session):
    document = create_document(
        db=db_session,
        title="Test document",
        description="Repository persistence test",
    )

    assert document.id == 1
    assert document.title == "Test document"
    assert document.description == "Repository persistence test"
    assert document.filename is None
    assert document.page_count is None
    assert document.extracted_text is None


def test_get_document_by_id(db_session):
    created_document = create_document(
        db=db_session,
        title="Test document",
        description="Repository retrieval test",
    )

    retrieved_document = get_document_by_id(
        db=db_session,
        document_id=created_document.id,
    )

    assert retrieved_document is not None
    assert retrieved_document.id == created_document.id
    assert retrieved_document.title == "Test document"


def test_get_document_by_id_not_found(db_session):
    document = get_document_by_id(
        db=db_session,
        document_id=999,
    )

    assert document is None


def test_get_all_documents(db_session):
    create_document(
        db=db_session,
        title="First document",
        description="First description",
    )

    create_document(
        db=db_session,
        title="Second document",
        description="Second description",
    )

    documents = get_all_documents(db_session)

    assert len(documents) == 2
    assert documents[0].title == "First document"
    assert documents[1].title == "Second document"


def test_get_all_documents_empty(db_session):
    documents = get_all_documents(db_session)

    assert documents == []


def test_update_document(db_session):
    document = create_document(
        db=db_session,
        title="Original title",
        description="Original description",
    )

    updated_document = update_document(
        db=db_session,
        document_id=document.id,
        title="Updated title",
    )

    assert updated_document is not None
    assert updated_document.title == "Updated title"
    assert updated_document.description == "Original description"


def test_update_document_not_found(db_session):
    updated_document = update_document(
        db=db_session,
        document_id=999,
        title="Updated title",
    )

    assert updated_document is None


def test_delete_document(db_session):
    document = create_document(
        db=db_session,
        title="Document to delete",
        description="Delete test",
    )

    document_id = document.id

    deleted = delete_document(
        db=db_session,
        document_id=document_id,
    )

    assert deleted is True
    assert get_document_by_id(db_session, document_id) is None


def test_delete_document_not_found(db_session):
    deleted = delete_document(
        db=db_session,
        document_id=999,
    )

    assert deleted is False


def test_convert_orm_document_to_pydantic(db_session):
    # Create a document in the test database.
    document = create_document(
        db=db_session,
        title="Pydantic Test",
        description="Testing ORM conversion",
    )

    # Convert the SQLAlchemy object into a Pydantic schema.
    response = DocumentResponse.model_validate(document)

    assert isinstance(response, DocumentResponse)
    assert response.id == document.id
    assert response.title == "Pydantic Test"
    assert response.description == "Testing ORM conversion"
    assert response.filename is None


def test_create_document_rollback_on_integrity_error(db_session):
    # Attempt to create a document with an invalid title.
    with pytest.raises(IntegrityError):
        create_document(
            db=db_session,
            title=None,
            description="Invalid document",
        )

    # Verify that the session can still be used after rollback.
    valid_document = create_document(
        db=db_session,
        title="Valid Document",
        description="Created after rollback",
    )

    assert valid_document.id is not None
    assert valid_document.title == "Valid Document"

    # Verify that only the valid document was persisted.
    documents = get_all_documents(db_session)

    assert len(documents) == 1
    assert documents[0].title == "Valid Document"
