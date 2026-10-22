from itertools import count

import pytest
from fastapi.testclient import TestClient

import app.services.document_service as document_service
from app.main import app


client = TestClient(app)


# Reset the in-memory storage and ID counter so each test runs in isolation.
@pytest.fixture(autouse=True)
def clear_documents():
    document_service.documents.clear()
    document_service.document_id_counter = count(start=1)

    yield

    document_service.documents.clear()


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
