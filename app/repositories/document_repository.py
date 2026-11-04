from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document


def get_document_by_id(
    db: Session,
    document_id: int,
) -> Document | None:
    return db.get(Document, document_id)


def create_document(
    db: Session,
    title: str,
    description: str,
    filename: str | None = None,
    page_count: int | None = None,
    extracted_text: str | None = None,
) -> Document:
    document = Document(
        title=title,
        description=description,
        filename=filename,
        page_count=page_count,
        extracted_text=extracted_text,
    )

    db.add(document)
    db.flush()

    return document


def get_all_documents(db: Session) -> list[Document]:
    statement = select(Document).order_by(Document.id)

    return list(db.scalars(statement).all())


def update_document(
    db: Session,
    document_id: int,
    title: str | None = None,
    description: str | None = None,
) -> Document | None:
    document = get_document_by_id(db, document_id)

    if document is None:
        return None

    if title is not None:
        document.title = title

    if description is not None:
        document.description = description

    db.flush()

    return document


def delete_document(
    db: Session,
    document_id: int,
) -> bool:
    document = get_document_by_id(db, document_id)

    if document is None:
        return False

    db.delete(document)
    db.flush()

    return True
