import pytest

from app.schemas.document import TITLE_MAX_LENGTH, DocumentCreate
from app.services.document_service import (
    create_document,
    create_document_from_pdf,
    get_document,
    normalize_filename,
)


# Verify that an uploaded PDF is stored with its extracted metadata.
def test_create_document_from_pdf():
    document = create_document_from_pdf(
        filename="example.pdf",
        page_count=3,
        extracted_text="Example extracted text",
    )

    assert document.id > 0
    assert document.title == "example.pdf"
    assert document.description == "Document uploaded from PDF"
    assert document.filename == "example.pdf"
    assert document.page_count == 3
    assert document.extracted_text == "Example extracted text"

    stored_document = get_document(document.id)

    assert stored_document == document


# Verify that manual documents and uploaded PDFs share the same ID counter.
def test_documents_share_id_counter():
    manual_document = create_document(
        DocumentCreate(
            title="Manual document",
            description="Created through the CRUD service",
        )
    )

    pdf_document = create_document_from_pdf(
        filename="report.pdf",
        page_count=2,
        extracted_text="Report content",
    )

    assert pdf_document.id == manual_document.id + 1
    assert get_document(manual_document.id) == manual_document
    assert get_document(pdf_document.id) == pdf_document


# Verify that uploaded filenames are normalized into valid document titles.
@pytest.mark.parametrize(
    "filename, expected",
    [
        ("report.pdf", "report.pdf"),
        ("Relatório Anual 2026.pdf", "Relatório Anual 2026.pdf"),
        ("  report.pdf  ", "report.pdf"),
        ("../../etc/passwd.pdf", "passwd.pdf"),
        ("/home/user/report.pdf", "report.pdf"),
        (r"C:\Users\user\report.pdf", "report.pdf"),
        (r"folder\sub/report.pdf", "report.pdf"),
        (None, "untitled.pdf"),
        ("", "untitled.pdf"),
        ("   ", "untitled.pdf"),
        ("folder/", "folder"),
        ("C:\\", "C:"),
        ("../", "untitled.pdf"),
        ("..", "untitled.pdf"),
        ("A" * 200, "A" * 200),
        ("A" * 196 + ".pdf", "A" * 196 + ".pdf"),
        ("A" * 300 + ".pdf", "A" * 196 + ".pdf"),
        ("A" * 300, "A" * 200),
        ("x." + "a" * 300, ("x." + "a" * 300)[:200]),
    ],
)
def test_normalize_filename(filename, expected):
    normalized = normalize_filename(filename)

    assert normalized == expected
    assert 1 <= len(normalized) <= TITLE_MAX_LENGTH

    # The result must also satisfy the regular title validation rules.
    assert DocumentCreate(title=normalized, description="d").title == normalized


# Verify that the stored title and filename both use the normalized name.
def test_create_document_from_pdf_normalizes_filename():
    document = create_document_from_pdf(
        filename="C:\\fakepath\\" + "A" * 300 + ".pdf",
        page_count=1,
        extracted_text="",
    )

    assert document.title == "A" * 196 + ".pdf"
    assert document.filename == document.title
