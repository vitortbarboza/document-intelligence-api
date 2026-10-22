from itertools import count

from app.schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate


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