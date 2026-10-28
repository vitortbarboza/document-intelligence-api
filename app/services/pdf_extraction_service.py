import pymupdf


MAX_PDF_PAGES = 500
MAX_EXTRACTED_TEXT_LENGTH = 2_000_000
PAGE_SEPARATOR = "\n"

# PyMuPDF signals invalid input through several unrelated exception types:
# FileDataError (a RuntimeError subclass), plain RuntimeError, and MuPDF
# errors such as FzErrorFormat. Programming errors are not caught.
PYMUPDF_ERRORS = (RuntimeError, pymupdf.mupdf.FzErrorBase)


class PDFExtractionError(Exception):
    pass


class PDFLimitExceededError(PDFExtractionError):
    pass


def extract_pdf_data(pdf_content: bytes) -> dict:
    try:
        # Open the PDF and extract its content and metadata.
        with pymupdf.open(stream=pdf_content, filetype="pdf") as document:

            # Reject password-protected documents.
            if document.needs_pass:
                raise PDFExtractionError(
                    "Password-protected PDFs are not supported"
                )

            if document.page_count > MAX_PDF_PAGES:
                raise PDFLimitExceededError(
                    f"PDF exceeds the {MAX_PDF_PAGES}-page limit"
                )

            pages_text = []
            text_length = 0

            # Extract text from every page, stopping once the limit is exceeded.
            for page in document:
                page_text = page.get_text()

                # Include the separator added by the final join.
                separator_length = len(PAGE_SEPARATOR) if pages_text else 0
                text_length += separator_length + len(page_text)

                if text_length > MAX_EXTRACTED_TEXT_LENGTH:
                    raise PDFLimitExceededError(
                        "Extracted text exceeds the "
                        f"{MAX_EXTRACTED_TEXT_LENGTH}-character limit"
                    )

                pages_text.append(page_text)

            return {
                "page_count": document.page_count,
                "extracted_text": PAGE_SEPARATOR.join(pages_text),
            }

    except PYMUPDF_ERRORS as exc:
        raise PDFExtractionError(
            "Unable to extract text from an invalid PDF"
        ) from exc


def extract_pdf_text(pdf_content: bytes) -> str:
    # Reuse the main extraction function.
    pdf_data = extract_pdf_data(pdf_content)

    return pdf_data["extracted_text"]
