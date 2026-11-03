from pathlib import PurePosixPath

from sqlalchemy.orm import Session

from app.repositories import document_repository
from app.schemas.document import (
    TITLE_MAX_LENGTH,
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
)

DEFAULT_PDF_FILENAME = "untitled.pdf"


def create_document(
    db: Session,
    document: DocumentCreate,
) -> DocumentResponse:
    # Persist the document using the repository.
    new_document = document_repository.create_document(
        db=db,
        title=document.title,
        description=document.description,
    )

    # Convert the ORM object into a Pydantic response.
    return DocumentResponse.model_validate(new_document)


def list_documents(db: Session) -> list[DocumentResponse]:
    # Retrieve all documents from the database.
    stored_documents = document_repository.get_all_documents(db)

    # Convert ORM objects into Pydantic responses.
    return [DocumentResponse.model_validate(document) for document in stored_documents]


def get_document(
    db: Session,
    document_id: int,
) -> DocumentResponse | None:
    # Retrieve the document from the database.
    document = document_repository.get_document_by_id(
        db=db,
        document_id=document_id,
    )

    if document is None:
        return None

    # Convert the ORM object into a Pydantic response.
    return DocumentResponse.model_validate(document)


def update_document(
    db: Session,
    document_id: int,
    document_update: DocumentUpdate,
) -> DocumentResponse | None:
    # Extract only the fields provided in the request.
    update_data = document_update.model_dump(exclude_unset=True)

    # Update the document in the database.
    updated_document = document_repository.update_document(
        db=db,
        document_id=document_id,
        **update_data,
    )

    if updated_document is None:
        return None

    # Convert the ORM object into a Pydantic response.
    return DocumentResponse.model_validate(updated_document)


def delete_document(
    db: Session,
    document_id: int,
) -> bool:
    # Delete the document using the repository.
    return document_repository.delete_document(
        db=db,
        document_id=document_id,
    )


def normalize_filename(filename: str | None) -> str:
    # Keep only the base name; clients may send Unix or Windows paths.
    name = PurePosixPath((filename or "").replace("\\", "/")).name.strip()

    # Relative path entries are not meaningful names.
    if name in {".", ".."}:
        name = ""

    if len(name) > TITLE_MAX_LENGTH:
        # Truncate the stem so the extension is preserved when possible.
        suffix = PurePosixPath(name).suffix

        if len(suffix) >= TITLE_MAX_LENGTH:
            suffix = ""

        stem = name[: len(name) - len(suffix)]
        name = stem[: TITLE_MAX_LENGTH - len(suffix)].rstrip() + suffix

    return name or DEFAULT_PDF_FILENAME


def create_document_from_pdf(
    db: Session,
    filename: str | None,
    page_count: int,
    extracted_text: str,
) -> DocumentResponse:
    # Normalize the uploaded filename.
    safe_filename = normalize_filename(filename)

    # Persist the extracted PDF information.
    document = document_repository.create_document(
        db=db,
        title=safe_filename,
        description="Document uploaded from PDF",
        filename=safe_filename,
        page_count=page_count,
        extracted_text=extracted_text,
    )

    # Convert the ORM object into a Pydantic response.
    return DocumentResponse.model_validate(document)
