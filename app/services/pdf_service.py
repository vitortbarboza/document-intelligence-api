from fastapi import HTTPException, UploadFile, status

MAX_PDF_SIZE = 10 * 1024 * 1024
PDF_SIGNATURE = b"%PDF-"


def read_pdf_upload(file: UploadFile) -> bytes:
    # Validate the declared content type.
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are allowed",
        )

    # Read at most one byte beyond the allowed size.
    pdf_content = file.file.read(MAX_PDF_SIZE + 1)

    # Validate the PDF file signature.
    if not pdf_content.startswith(PDF_SIGNATURE):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid PDF file signature",
        )

    # Validate the file size.
    if len(pdf_content) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="PDF file exceeds the 10 MB size limit",
        )

    return pdf_content
