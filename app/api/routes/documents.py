from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
)
from app.services.document_service import (
    create_document as create_document_service,
    create_document_from_pdf,
    delete_document as delete_document_service,
    get_document as get_document_service,
    list_documents as list_documents_service,
    update_document as update_document_service,
)
from app.services.pdf_extraction_service import (
    PDFExtractionError,
    PDFLimitExceededError,
    extract_pdf_data,
)
from app.services.pdf_service import read_pdf_upload


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "",
    response_model=DocumentResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
) -> DocumentResponse:
    return create_document_service(db, document)


@router.get(
    "",
    response_model=list[DocumentResponse],
    response_model_exclude_none=True,
)
def list_documents(
    db: Session = Depends(get_db),
) -> list[DocumentResponse]:
    return list_documents_service(db)


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    response_model_exclude_none=True,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
) -> DocumentResponse:
    document = get_document_service(db, document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.patch(
    "/{document_id}",
    response_model=DocumentResponse,
    response_model_exclude_none=True,
)
def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db),
) -> DocumentResponse:
    updated_document = update_document_service(
        db,
        document_id,
        document_update,
    )

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
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
) -> None:
    deleted = delete_document_service(db, document_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    pdf_content = await read_pdf_upload(file)

    try:
        pdf_data = extract_pdf_data(pdf_content)
    except PDFLimitExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=str(exc),
        ) from exc
    except PDFExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    document = create_document_from_pdf(
        db=db,
        filename=file.filename,
        page_count=pdf_data["page_count"],
        extracted_text=pdf_data["extracted_text"],
    )

    return document