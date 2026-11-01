from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document


def get_document_by_id(
    db: Session,
    document_id: int,
) -> Document | None:
    statement = select(Document).where(Document.id == document_id)

    return db.scalar(statement)


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

    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        raise

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

    try:
        if title is not None:
            document.title = title

        if description is not None:
            document.description = description

        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        raise

    return document


def delete_document(
    db: Session,
    document_id: int,
) -> bool:
    document = get_document_by_id(db, document_id)

    if document is None:
        return False

    try:
        db.delete(document)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return True