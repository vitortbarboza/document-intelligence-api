from fastapi import HTTPException, UploadFile, status


MAX_PDF_SIZE = 10 * 1024 * 1024
PDF_SIGNATURE = b"%PDF-"


# Starlette spools the full multipart body to a temporary file before the
# endpoint runs, so this check bounds memory and processing, not the request
# body itself. Rejecting oversized bodies earlier requires a reverse proxy
# limit or ASGI middleware.
async def read_pdf_upload(file: UploadFile) -> bytes:
    # Validate the declared content type.
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are allowed",
        )

    # Read at most one byte past the limit so oversized files are detected
    # without loading them entirely.
    pdf_content = await file.read(MAX_PDF_SIZE + 1)

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
