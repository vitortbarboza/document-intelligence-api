from fastapi import APIRouter, HTTPException, status

from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
)
from app.services.document_service import (
    create_document as create_document_service,
    delete_document as delete_document_service,
    get_document as get_document_service,
    list_documents as list_documents_service,
    update_document as update_document_service,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(document: DocumentCreate) -> DocumentResponse:
    return create_document_service(document)


@router.get(
    "",
    response_model=list[DocumentResponse],
)
def list_documents() -> list[DocumentResponse]:
    return list_documents_service()


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(document_id: int) -> DocumentResponse:
    document = get_document_service(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.patch(
    "/{document_id}",
    response_model=DocumentResponse,
)
def update_document(
    document_id: int,
    document_update: DocumentUpdate,
) -> DocumentResponse:
    updated_document = update_document_service(document_id, document_update)

    if updated_document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return updated_document


# Delete a document by its ID.
# Return HTTP 404 if the document does not exist.
@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(document_id: int) -> None:
    deleted = delete_document_service(document_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )