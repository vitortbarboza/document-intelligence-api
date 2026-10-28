from itertools import count

import pymupdf
import pytest

from app.services import document_service


# Build an in-memory PDF with one page per text (an empty string adds a blank page).
@pytest.fixture
def make_pdf():
    def _make_pdf(*page_texts: str) -> bytes:
        document = pymupdf.open()

        for text in page_texts:
            page = document.new_page()

            if text:
                page.insert_text((72, 72), text)

        pdf_content = document.tobytes()
        document.close()

        return pdf_content

    return _make_pdf


# Reset the in-memory storage and ID counter before and after each test.
@pytest.fixture(autouse=True)
def clear_documents():
    document_service.documents.clear()
    document_service.document_id_counter = count(start=1)

    yield

    document_service.documents.clear()
    document_service.document_id_counter = count(start=1)