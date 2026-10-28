import pytest
import pymupdf
from fastapi.testclient import TestClient

from app.main import app
from app.services import pdf_extraction_service


client = TestClient(app)


# Verify that a valid document is created successfully.
# The API should return HTTP 201 and the document with its generated ID.
def test_create_document_valid():
    payload = {
        "title": "Relatório Financeiro 2026",
        "description": "Relatório anual da empresa",
    }

    response = client.post("/documents", json=payload)

    assert response.status_code == 201

    assert response.json() == {
        "id": 1,
        "title": "Relatório Financeiro 2026",
        "description": "Relatório anual da empresa",
    }


# Verify that creating a document without the required title is rejected.
# The API should return HTTP 422 and identify the missing field.
def test_create_document_missing_title():
    payload = {
        "description": "Relatório anual da empresa",
    }

    response = client.post("/documents", json=payload)

    assert response.status_code == 422

    error = response.json()["detail"][0]

    assert error["type"] == "missing"
    assert error["loc"] == ["body", "title"]


# Test multiple invalid title values using parameterization.
# Empty, whitespace-only, and oversized titles should return HTTP 422.
@pytest.mark.parametrize(
    "title",
    [
        "",
        " ",
        "   ",
        "A" * 201,
    ],
)
def test_create_document_invalid_title(title):
    payload = {
        "title": title,
        "description": "Relatório anual da empresa",
    }

    response = client.post("/documents", json=payload)

    assert response.status_code == 422

    error = response.json()["detail"][0]

    assert error["loc"] == ["body", "title"]


# Verify that listing documents returns an empty list when no documents exist.
# The API should return HTTP 200 with an empty JSON array.
def test_list_documents_empty():
    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json() == []


# Verify that all previously created documents are returned by the API.
# The response should contain both documents in their creation order.
def test_list_documents_with_data():
    first_document = {
        "title": "Relatório Financeiro",
        "description": "Relatório anual de 2026",
    }

    second_document = {
        "title": "Contrato de Serviços",
        "description": "Contrato com fornecedor",
    }

    client.post("/documents", json=first_document)
    client.post("/documents", json=second_document)

    response = client.get("/documents")

    assert response.status_code == 200
    assert len(response.json()) == 2

    assert response.json()[0]["title"] == "Relatório Financeiro"
    assert response.json()[1]["title"] == "Contrato de Serviços"


# Verify that an existing document can be retrieved by its ID.
# The API should return HTTP 200 and the correct document data.
def test_get_document_by_id():
    payload = {
        "title": "Relatório Financeiro",
        "description": "Relatório anual de 2026",
    }

    create_response = client.post("/documents", json=payload)

    document_id = create_response.json()["id"]

    response = client.get(f"/documents/{document_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": document_id,
        "title": "Relatório Financeiro",
        "description": "Relatório anual de 2026",
    }


# Verify that requesting a nonexistent document returns HTTP 404.
# The API should provide a descriptive error message.
def test_get_document_not_found():
    response = client.get("/documents/9999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document not found"
    }


# Verify that a partial update changes only the provided field.
# The document description should remain unchanged.
def test_update_document_title():
    payload = {
        "title": "Relatório Financeiro",
        "description": "Relatório anual de 2026",
    }

    create_response = client.post("/documents", json=payload)
    document_id = create_response.json()["id"]

    update_payload = {
        "title": "Relatório Financeiro Atualizado",
    }

    response = client.patch(
        f"/documents/{document_id}",
        json=update_payload,
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": document_id,
        "title": "Relatório Financeiro Atualizado",
        "description": "Relatório anual de 2026",
    }


# Verify that invalid title values are rejected during document updates.
# Empty, whitespace-only, oversized, and null values should return HTTP 422.
@pytest.mark.parametrize(
    "invalid_title",
    [
        "",
        " ",
        "   ",
        "A" * 201,
        None,
    ],
)
def test_update_document_invalid_title(invalid_title):
    payload = {
        "title": "Relatório Financeiro",
        "description": "Relatório anual de 2026",
    }

    create_response = client.post("/documents", json=payload)
    document_id = create_response.json()["id"]

    response = client.patch(
        f"/documents/{document_id}",
        json={"title": invalid_title},
    )

    assert response.status_code == 422

    error = response.json()["detail"][0]

    assert error["loc"] == ["body", "title"]

    if invalid_title is None:
        assert "Title cannot be null" in error["msg"]


# Verify that updating a nonexistent document returns HTTP 404.
# The API should provide a clear error message.
def test_update_document_not_found():
    update_payload = {
        "title": "Documento Atualizado",
    }

    response = client.patch(
        "/documents/9999",
        json=update_payload,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document not found",
    }


# Verify that updating only the description preserves the original title.
def test_update_document_description():
    payload = {
        "title": "Relatório Financeiro",
        "description": "Relatório anual de 2026",
    }

    create_response = client.post("/documents", json=payload)
    document_id = create_response.json()["id"]

    update_payload = {
        "description": "Relatório financeiro revisado",
    }

    response = client.patch(
        f"/documents/{document_id}",
        json=update_payload,
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": document_id,
        "title": "Relatório Financeiro",
        "description": "Relatório financeiro revisado",
    }


# Verify that explicitly setting the description to null is rejected.
# The API should return HTTP 422 and identify the invalid field.
def test_update_document_null_description():
    payload = {
        "title": "Relatório Financeiro",
        "description": "Relatório anual de 2026",
    }

    create_response = client.post("/documents", json=payload)
    document_id = create_response.json()["id"]

    response = client.patch(
        f"/documents/{document_id}",
        json={"description": None},
    )

    assert response.status_code == 422

    error = response.json()["detail"][0]

    assert error["type"] == "value_error"
    assert error["loc"] == ["body", "description"]
    assert "Description cannot be null" in error["msg"]


# Verify that an existing document can be deleted successfully.
# The API should return HTTP 204, and the document should no longer exist.
def test_delete_document_valid():
    payload = {
        "title": "Documento para Exclusão",
        "description": "Documento criado para testar o DELETE",
    }

    create_response = client.post("/documents", json=payload)
    document_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/documents/{document_id}"
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(
        f"/documents/{document_id}"
    )

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Document not found",
    } 


# Verify that deleting a nonexistent document returns HTTP 404.
# The API should provide a clear error message.
def test_delete_document_not_found():
    response = client.delete("/documents/9999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document not found",
    }


# Verify that document IDs are not reused after deletion.
# A new document should receive an ID greater than the deleted one.
def test_document_id_not_reused_after_deletion():
    payload = {
        "title": "Relatório Financeiro",
        "description": "Relatório anual de 2026",
    }

    first_response = client.post("/documents", json=payload)
    second_response = client.post("/documents", json=payload)

    first_id = first_response.json()["id"]
    second_id = second_response.json()["id"]

    delete_response = client.delete(f"/documents/{second_id}")

    third_response = client.post("/documents", json=payload)
    third_id = third_response.json()["id"]

    assert first_id == 1
    assert second_id == 2
    assert delete_response.status_code == 204
    assert third_response.status_code == 201
    assert third_id == 3


# Verify that invalid descriptions are rejected during document creation.
# Empty, whitespace-only, and oversized descriptions should return HTTP 422.
@pytest.mark.parametrize(
    "invalid_description",
    [
        "",
        " ",
        "   ",
        "A" * 1001,
    ],
)
def test_create_document_invalid_description(invalid_description):
    payload = {
        "title": "Relatório Financeiro",
        "description": invalid_description,
    }

    response = client.post("/documents", json=payload)

    assert response.status_code == 422

    error = response.json()["detail"][0]
    assert error["loc"] == ["body", "description"]


# Verify that invalid descriptions are rejected during document updates.
# Empty, whitespace-only, and oversized descriptions should return HTTP 422.
@pytest.mark.parametrize(
    "invalid_description",
    [
        "",
        " ",
        "   ",
        "A" * 1001,
    ],
)
def test_update_document_invalid_description(invalid_description):
    payload = {
        "title": "Relatório Financeiro",
        "description": "Relatório anual de 2026",
    }

    create_response = client.post("/documents", json=payload)
    document_id = create_response.json()["id"]

    response = client.patch(
        f"/documents/{document_id}",
        json={"description": invalid_description},
    )

    assert response.status_code == 422

    error = response.json()["detail"][0]
    assert error["loc"] == ["body", "description"]


# Verify that leading and trailing whitespace is removed during document creation.
# The API should return normalized title and description values.
def test_create_document_trims_whitespace():
    response = client.post(
        "/documents",
        json={
            "title": "  Financial Report  ",
            "description": "  Quarterly financial results  ",
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Financial Report"
    assert response.json()["description"] == "Quarterly financial results"


# Verify that the length limit is checked after whitespace is stripped.
# A 200-character title surrounded by spaces should be accepted.
def test_create_document_max_length_after_trim():
    response = client.post(
        "/documents",
        json={
            "title": "  " + "A" * 200 + "  ",
            "description": "Relatório anual de 2026",
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "A" * 200


# Verify that unknown fields are rejected during document creation.
def test_create_document_unknown_field():
    response = client.post(
        "/documents",
        json={
            "title": "Relatório Financeiro",
            "description": "Relatório anual de 2026",
            "author": "Maria",
        },
    )

    assert response.status_code == 422

    error = response.json()["detail"][0]

    assert error["type"] == "extra_forbidden"
    assert error["loc"] == ["body", "author"]


# Verify that unknown fields are rejected during document updates.
# A misspelled field name should not result in a silent no-op update.
def test_update_document_unknown_field():
    create_response = client.post(
        "/documents",
        json={
            "title": "Relatório Financeiro",
            "description": "Relatório anual de 2026",
        },
    )
    document_id = create_response.json()["id"]

    response = client.patch(
        f"/documents/{document_id}",
        json={"titel": "Relatório Atualizado"},
    )

    assert response.status_code == 422

    error = response.json()["detail"][0]

    assert error["type"] == "extra_forbidden"
    assert error["loc"] == ["body", "titel"]


# Verify that an update without any fields is rejected.
def test_update_document_empty_payload():
    create_response = client.post(
        "/documents",
        json={
            "title": "Relatório Financeiro",
            "description": "Relatório anual de 2026",
        },
    )
    document_id = create_response.json()["id"]

    response = client.patch(f"/documents/{document_id}", json={})

    assert response.status_code == 422
    assert "At least one field must be provided" in response.json()["detail"][0]["msg"]


# Verify that a valid PDF can be uploaded and processed successfully.
# The API should return the filename, page count, and extracted text.
def test_upload_pdf_success():
    document = pymupdf.open()
    page = document.new_page()

    page.insert_text(
        (72, 72),
        "Hello, Document Intelligence API!",
    )

    pdf_content = document.tobytes()
    document.close()

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test_document.pdf",
                pdf_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201

    response_data = response.json()

    assert isinstance(response_data["id"], int)
    assert response_data["id"] > 0
    assert response_data["title"] == "test_document.pdf"
    assert response_data["description"] == "Document uploaded from PDF"
    assert response_data["filename"] == "test_document.pdf"
    assert response_data["page_count"] == 1
    assert "Hello, Document Intelligence API!" in response_data["extracted_text"]

    document_id = response_data["id"]

    get_response = client.get(f"/documents/{document_id}")

    assert get_response.status_code == 200
    assert get_response.json() == response_data


# Verify that non-PDF files are rejected during upload.
# Files with unsupported content types should return HTTP 415.
@pytest.mark.parametrize(
    "filename, content_type",
    [
        ("document.txt", "text/plain"),
        ("image.png", "image/png"),
        ("data.json", "application/json"),
    ],
)
def test_upload_invalid_content_type(filename, content_type):
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                filename,
                b"Test content",
                content_type,
            )
        },
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Only PDF files are allowed"


# Verify that files with invalid PDF signatures are rejected.
# Files declared as PDFs without the expected header should return HTTP 422.
@pytest.mark.parametrize(
    "file_content",
    [
        b"Plain text content",
        b"\x89PNG\r\n\x1a\n",
        b"",
        b"%PDX-1.4",
    ],
)
def test_upload_invalid_pdf_signature(file_content):
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "document.pdf",
                file_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid PDF file signature"


# Verify that PDF uploads respect the 10 MB size limit.
# Valid PDFs within the limit should succeed, while larger files return HTTP 413.
@pytest.mark.parametrize(
    "file_size, expected_status",
    [
        (10 * 1024 * 1024, 201),
        (10 * 1024 * 1024 + 1, 413),
    ],
)
def test_upload_pdf_size_limit(file_size, expected_status):
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "PDF size limit test")

    pdf_content = document.tobytes()
    document.close()

    # Pad the PDF to the requested size.
    file_content = pdf_content + b"\x00" * (file_size - len(pdf_content))

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "test_document.pdf",
                file_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == expected_status

    if expected_status == 413:
        assert response.json()["detail"] == (
            "PDF file exceeds the 10 MB size limit"
        )
    else:
        assert "PDF size limit test" in response.json()["extracted_text"]


# Verify that corrupted PDFs are rejected by the upload endpoint.
# Extraction failures should return HTTP 422 instead of an internal server error.
def test_upload_corrupted_pdf():
    corrupted_pdf = b"%PDF-1.4\nInvalid PDF content"

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "corrupted.pdf",
                corrupted_pdf,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Unable to extract text from an invalid PDF"
    )


# Verify that password-protected PDFs are rejected by the upload endpoint.
# Encrypted documents should return HTTP 422 with a descriptive error.
def test_upload_password_protected_pdf():
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Confidential document")

    encrypted_pdf = document.tobytes(
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        owner_pw="owner123",
        user_pw="secret123",
    )
    document.close()

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "protected.pdf",
                encrypted_pdf,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "Password-protected PDFs are not supported"
    )


# Verify that uploaded PDFs support listing, updating, and deletion.
def test_uploaded_pdf_crud_lifecycle():
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Document lifecycle test")

    pdf_content = document.tobytes()
    document.close()

    # Upload the PDF.
    upload_response = client.post(
        "/documents/upload",
        files={
            "file": (
                "lifecycle.pdf",
                pdf_content,
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 201

    document_id = upload_response.json()["id"]

    # Verify that the document appears in the list.
    list_response = client.get("/documents")

    assert list_response.status_code == 200
    assert any(
        item["id"] == document_id
        for item in list_response.json()
    )

    # Update the document title.
    update_response = client.patch(
        f"/documents/{document_id}",
        json={"title": "Updated PDF document"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated PDF document"
    assert update_response.json()["filename"] == "lifecycle.pdf"
    assert update_response.json()["page_count"] == 1
    assert "Document lifecycle test" in update_response.json()["extracted_text"]

    # Delete the document.
    delete_response = client.delete(f"/documents/{document_id}")

    assert delete_response.status_code == 204

    # Verify that the document is no longer available.
    get_response = client.get(f"/documents/{document_id}")

    assert get_response.status_code == 404


# Verify that PDFs without extractable text are stored successfully.
def test_upload_pdf_without_text():
    document = pymupdf.open()
    document.new_page()

    pdf_content = document.tobytes()
    document.close()

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "blank.pdf",
                pdf_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["filename"] == "blank.pdf"
    assert response_data["page_count"] == 1
    assert response_data["extracted_text"] == ""

    document_id = response_data["id"]

    get_response = client.get(f"/documents/{document_id}")

    assert get_response.status_code == 200
    assert get_response.json() == response_data


# Send a single file to the upload endpoint.
def upload_pdf(filename, content, content_type="application/pdf"):
    return client.post(
        "/documents/upload",
        files={"file": (filename, content, content_type)},
    )


# Verify that listing keeps the original structure for manual documents.
# PDF fields appear only for uploaded documents, matching GET /documents/{id}.
def test_list_documents_response_structure(make_pdf):
    client.post(
        "/documents",
        json={
            "title": "Relatório Financeiro",
            "description": "Relatório anual de 2026",
        },
    )
    upload_pdf("report.pdf", make_pdf("Report content"))

    response = client.get("/documents")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "title": "Relatório Financeiro",
            "description": "Relatório anual de 2026",
        },
        {
            "id": 2,
            "title": "report.pdf",
            "description": "Document uploaded from PDF",
            "filename": "report.pdf",
            "page_count": 1,
            "extracted_text": "Report content\n",
        },
    ]

    for item in response.json():
        assert client.get(f"/documents/{item['id']}").json() == item


# Verify that PyMuPDF errors beyond FileDataError return HTTP 422, not 500.
@pytest.mark.parametrize(
    "error",
    [
        RuntimeError("cannot load page"),
        pymupdf.mupdf.FzErrorFormat("non-page object in page tree"),
    ],
)
def test_upload_pdf_pymupdf_errors(monkeypatch, make_pdf, error):
    def raise_error(*args, **kwargs):
        raise error

    monkeypatch.setattr(pymupdf.Page, "get_text", raise_error)

    response = upload_pdf("broken.pdf", make_pdf("Page content"))

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Unable to extract text from an invalid PDF",
    }
    assert client.get("/documents").json() == []


# Verify that uploaded filenames are normalized into valid titles.
@pytest.mark.parametrize(
    "filename, expected_title",
    [
        ("report.pdf", "report.pdf"),
        ("   ", "untitled.pdf"),
        ("  report.pdf  ", "report.pdf"),
        ("../../etc/passwd.pdf", "passwd.pdf"),
        (r"C:\Users\user\report.pdf", "report.pdf"),
        ("A" * 300 + ".pdf", "A" * 196 + ".pdf"),
    ],
)
def test_upload_pdf_normalizes_filename(make_pdf, filename, expected_title):
    response = upload_pdf(filename, make_pdf("Content"))

    assert response.status_code == 201
    assert response.json()["title"] == expected_title
    assert response.json()["filename"] == expected_title

    # Updating another field must not fail because of the generated title.
    document_id = response.json()["id"]
    update_response = client.patch(
        f"/documents/{document_id}",
        json={"description": "Updated description"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == expected_title


# Verify that PDFs above the page limit return HTTP 413.
def test_upload_pdf_page_limit(monkeypatch, make_pdf):
    monkeypatch.setattr(pdf_extraction_service, "MAX_PDF_PAGES", 2)

    accepted = upload_pdf("two_pages.pdf", make_pdf("One", "Two"))
    rejected = upload_pdf("three_pages.pdf", make_pdf("One", "Two", "Three"))

    assert accepted.status_code == 201
    assert rejected.status_code == 413
    assert rejected.json() == {"detail": "PDF exceeds the 2-page limit"}


# Verify that PDFs whose extracted text exceeds the limit return HTTP 413.
def test_upload_pdf_text_limit(monkeypatch, make_pdf):
    monkeypatch.setattr(pdf_extraction_service, "MAX_EXTRACTED_TEXT_LENGTH", 10)

    response = upload_pdf("long_text.pdf", make_pdf("More than ten characters"))

    assert response.status_code == 413
    assert response.json() == {
        "detail": "Extracted text exceeds the 10-character limit",
    }


# Verify that rejected uploads do not create documents or consume IDs.
@pytest.mark.parametrize(
    "content, content_type, expected_status",
    [
        (b"Plain text", "text/plain", 415),
        (b"Plain text", "application/pdf", 422),
        (b"%PDF-1.4\nInvalid PDF content", "application/pdf", 422),
        (b"%PDF-" + b"\x00" * (10 * 1024 * 1024), "application/pdf", 413),
    ],
    # Explicit IDs keep the 10 MiB payload out of the test name.
    ids=["content-type", "signature", "corrupted", "size"],
)
def test_rejected_upload_does_not_create_document(
    content,
    content_type,
    expected_status,
):
    response = upload_pdf("document.pdf", content, content_type)

    assert response.status_code == expected_status
    assert client.get("/documents").json() == []

    create_response = client.post(
        "/documents",
        json={"title": "Next document", "description": "Created after a failure"},
    )

    assert create_response.json()["id"] == 1


# Verify that an upload request without a file is rejected.
def test_upload_without_file():
    response = client.post("/documents/upload")

    assert response.status_code == 422

    error = response.json()["detail"][0]

    assert error["type"] == "missing"
    assert error["loc"] == ["body", "file"]
