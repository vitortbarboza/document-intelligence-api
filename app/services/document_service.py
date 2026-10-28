from itertools import count
from pathlib import PurePosixPath

from app.schemas.document import (
    TITLE_MAX_LENGTH,
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
)


DEFAULT_PDF_FILENAME = "untitled.pdf"

documents: dict[int, DocumentResponse] = {}
document_id_counter = count(start=1)


def create_document(document: DocumentCreate) -> DocumentResponse:
    document_id = next(document_id_counter)

    new_document = DocumentResponse(
        id=document_id,
        title=document.title,
        description=document.description,
    )

    documents[document_id] = new_document

    return new_document


def list_documents() -> list[DocumentResponse]:
    return list(documents.values())


def get_document(document_id: int) -> DocumentResponse | None:
    return documents.get(document_id)


def update_document(
    document_id: int,
    document_update: DocumentUpdate,
) -> DocumentResponse | None:
    existing_document = documents.get(document_id)

    if existing_document is None:
        return None

    update_data = document_update.model_dump(exclude_unset=True)

    updated_document = existing_document.model_copy(
        update=update_data
    )

    documents[document_id] = updated_document

    return updated_document


def delete_document(document_id: int) -> bool:
    if document_id not in documents:
        return False

    del documents[document_id]
    return True


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
    filename: str | None,
    page_count: int,
    extracted_text: str,
) -> DocumentResponse:
    safe_filename = normalize_filename(filename)

    # Generate an ID using the existing counter.
    document_id = next(document_id_counter)

    # Create a document with the extracted PDF information.
    new_document = DocumentResponse(
        id=document_id,
        title=safe_filename,
        description="Document uploaded from PDF",
        filename=safe_filename,
        page_count=page_count,
        extracted_text=extracted_text,
    )

    # Store the document in the existing in-memory dictionary.
    documents[document_id] = new_document

    return new_document