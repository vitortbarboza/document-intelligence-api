import pymupdf
import pytest

from app.services import pdf_extraction_service
from app.services.pdf_extraction_service import (
    PDFExtractionError,
    PDFLimitExceededError,
    extract_pdf_text,
    extract_pdf_data,
)


# Verify that text can be extracted from a valid PDF.
# The extracted content should match the text inserted into the document.
def test_extract_pdf_text_success():
    document = pymupdf.open()
    page = document.new_page()

    page.insert_text(
        (72, 72),
        "Hello, Document Intelligence API!",
    )

    pdf_content = document.tobytes()
    document.close()

    extracted_text = extract_pdf_text(pdf_content)

    assert "Hello, Document Intelligence API!" in extracted_text


# Verify that text is extracted from every page of a PDF.
# Content from multiple pages should be included in the result.
def test_extract_pdf_text_multiple_pages():
    document = pymupdf.open()

    page_1 = document.new_page()
    page_1.insert_text((72, 72), "Content from page one")

    page_2 = document.new_page()
    page_2.insert_text((72, 72), "Content from page two")

    page_3 = document.new_page()
    page_3.insert_text((72, 72), "Content from page three")

    pdf_content = document.tobytes()
    document.close()

    extracted_text = extract_pdf_text(pdf_content)

    assert "Content from page one" in extracted_text
    assert "Content from page two" in extracted_text
    assert "Content from page three" in extracted_text    


# Verify that a PDF without text returns an empty string.
# Documents containing no extractable text should not cause errors.
def test_extract_pdf_text_empty_page():
    document = pymupdf.open()
    document.new_page()

    pdf_content = document.tobytes()
    document.close()

    extracted_text = extract_pdf_text(pdf_content)

    assert extracted_text == ""


# Verify that corrupted PDFs raise a custom extraction error.
# Library-specific exceptions should not leak from the service.
def test_extract_pdf_text_corrupted_pdf():
    corrupted_pdf = b"%PDF-1.4\nInvalid PDF content"

    with pytest.raises(
        PDFExtractionError,
        match="Unable to extract text from an invalid PDF",
    ):
        extract_pdf_text(corrupted_pdf)


# Verify that password-protected PDFs are rejected.
# Encrypted documents should raise a custom extraction error.
def test_extract_pdf_text_password_protected():
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Confidential document")

    encrypted_pdf = document.tobytes(
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        owner_pw="owner123",
        user_pw="secret123",
    )
    document.close()

    with pytest.raises(
        PDFExtractionError,
        match="Password-protected PDFs are not supported",
    ):
        extract_pdf_text(encrypted_pdf)


# Verify that PDF data extraction returns the correct page count and text.
# The result should contain information from all pages.
def test_extract_pdf_data_success():
    document = pymupdf.open()

    page_1 = document.new_page()
    page_1.insert_text((72, 72), "First page content")

    page_2 = document.new_page()
    page_2.insert_text((72, 72), "Second page content")

    pdf_content = document.tobytes()
    document.close()

    result = extract_pdf_data(pdf_content)

    assert result["page_count"] == 2
    assert "First page content" in result["extracted_text"]
    assert "Second page content" in result["extracted_text"]


# Verify that PyMuPDF errors other than FileDataError are converted.
# Malformed pages can raise these while the document is being read.
@pytest.mark.parametrize(
    "error",
    [
        RuntimeError("cannot load page"),
        pymupdf.mupdf.FzErrorFormat("non-page object in page tree"),
    ],
)
def test_extract_pdf_data_converts_pymupdf_errors(monkeypatch, make_pdf, error):
    def raise_error(*args, **kwargs):
        raise error

    monkeypatch.setattr(pymupdf.Page, "get_text", raise_error)

    with pytest.raises(
        PDFExtractionError,
        match="Unable to extract text from an invalid PDF",
    ) as exc_info:
        extract_pdf_data(make_pdf("Page content"))

    # The original exception is kept for diagnostics.
    assert exc_info.value.__cause__ is error


# Verify that programming errors are not hidden as invalid PDFs.
def test_extract_pdf_data_does_not_hide_programming_errors(monkeypatch, make_pdf):
    def raise_type_error(*args, **kwargs):
        raise TypeError("unexpected argument")

    monkeypatch.setattr(pymupdf.Page, "get_text", raise_type_error)

    with pytest.raises(TypeError, match="unexpected argument"):
        extract_pdf_data(make_pdf("Page content"))


# Verify the page limit boundary: the limit is accepted, one more page is not.
@pytest.mark.parametrize(
    "page_count, should_fail",
    [
        (3, False),
        (4, True),
    ],
)
def test_extract_pdf_data_page_limit(monkeypatch, make_pdf, page_count, should_fail):
    monkeypatch.setattr(pdf_extraction_service, "MAX_PDF_PAGES", 3)
    pdf_content = make_pdf(*["Page"] * page_count)

    if should_fail:
        with pytest.raises(PDFLimitExceededError, match="3-page limit"):
            extract_pdf_data(pdf_content)
    else:
        assert extract_pdf_data(pdf_content)["page_count"] == page_count


# Verify the text limit boundary, including the separators between pages.
@pytest.mark.parametrize(
    "limit_offset, should_fail",
    [
        (0, False),
        (-1, True),
    ],
)
def test_extract_pdf_data_text_limit(monkeypatch, make_pdf, limit_offset, should_fail):
    pdf_content = make_pdf("First page", "Second page")
    text_length = len(extract_pdf_data(pdf_content)["extracted_text"])

    monkeypatch.setattr(
        pdf_extraction_service,
        "MAX_EXTRACTED_TEXT_LENGTH",
        text_length + limit_offset,
    )

    if should_fail:
        with pytest.raises(PDFLimitExceededError, match="character limit"):
            extract_pdf_data(pdf_content)
    else:
        assert len(extract_pdf_data(pdf_content)["extracted_text"]) == text_length


# Verify that extraction stops at the first page that exceeds the text limit.
def test_extract_pdf_data_stops_at_text_limit(monkeypatch, make_pdf):
    monkeypatch.setattr(pdf_extraction_service, "MAX_EXTRACTED_TEXT_LENGTH", 5)

    calls = []
    original_get_text = pymupdf.Page.get_text

    def counting_get_text(self, *args, **kwargs):
        calls.append(self.number)
        return original_get_text(self, *args, **kwargs)

    monkeypatch.setattr(pymupdf.Page, "get_text", counting_get_text)

    with pytest.raises(PDFLimitExceededError):
        extract_pdf_data(make_pdf("Long first page", "Second", "Third"))

    assert calls == [0]
