from app.repositories import document_repository


def test_create_document_persists_in_database(db_client, db_session):
    # Send a request to the API.
    response = db_client.post(
        "/documents",
        json={
            "title": "Database Integration Test",
            "description": "Testing SQLite persistence",
        },
    )

    # Verify the HTTP response.
    assert response.status_code == 201

    response_data = response.json()

    assert response_data["id"] == 1
    assert response_data["title"] == "Database Integration Test"
    assert response_data["description"] == "Testing SQLite persistence"

    # Verify that the document was actually saved in SQLite.
    saved_document = document_repository.get_document_by_id(
        db=db_session,
        document_id=response_data["id"],
    )

    assert saved_document is not None
    assert saved_document.title == "Database Integration Test"
    assert saved_document.description == "Testing SQLite persistence"


def test_list_documents_from_database(db_client):
    # Create two documents through the API.
    db_client.post(
        "/documents",
        json={
            "title": "First Document",
            "description": "First description",
        },
    )

    db_client.post(
        "/documents",
        json={
            "title": "Second Document",
            "description": "Second description",
        },
    )

    # Retrieve all documents.
    response = db_client.get("/documents")

    assert response.status_code == 200

    documents = response.json()

    assert len(documents) == 2
    assert documents[0]["title"] == "First Document"
    assert documents[1]["title"] == "Second Document"
    assert documents[0]["id"] == 1
    assert documents[1]["id"] == 2


def test_list_documents_empty_database(db_client):
    # Retrieve documents from an empty database.
    response = db_client.get("/documents")

    assert response.status_code == 200
    assert response.json() == []


def test_get_document_from_database(db_client):
    create_response = db_client.post(
        "/documents",
        json={
            "title": "Document Details",
            "description": "Testing document retrieval",
        },
    )

    document_id = create_response.json()["id"]

    response = db_client.get(f"/documents/{document_id}")

    assert response.status_code == 200
    assert response.json()["id"] == document_id
    assert response.json()["title"] == "Document Details"
    assert response.json()["description"] == "Testing document retrieval"


def test_get_document_not_found_in_database(db_client):
    response = db_client.get("/documents/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}


def test_update_document_in_database(db_client):
    create_response = db_client.post(
        "/documents",
        json={
            "title": "Original Title",
            "description": "Original Description",
        },
    )

    document_id = create_response.json()["id"]

    response = db_client.patch(
        f"/documents/{document_id}",
        json={"title": "Updated Title"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["description"] == "Original Description"

    # Verify the updated data was persisted.
    get_response = db_client.get(f"/documents/{document_id}")

    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Updated Title"
    assert get_response.json()["description"] == "Original Description"


def test_update_document_not_found_in_database(db_client):
    response = db_client.patch(
        "/documents/999",
        json={"title": "Updated Title"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}


def test_delete_document_from_database(db_client):
    # Create a document.
    create_response = db_client.post(
        "/documents",
        json={
            "title": "Document to Delete",
            "description": "Testing deletion",
        },
    )

    assert create_response.status_code == 201
    document_id = create_response.json()["id"]

    # Delete the document.
    delete_response = db_client.delete(
        f"/documents/{document_id}"
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    # Verify the document no longer exists.
    get_response = db_client.get(
        f"/documents/{document_id}"
    )

    assert get_response.status_code == 404


def test_delete_document_not_found_in_database(db_client):
    response = db_client.delete("/documents/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document not found"
    }


def test_upload_pdf_persists_in_database(
    db_client,
    db_session,
    make_pdf,
):
    # Generate a valid PDF for testing.
    pdf_content = make_pdf("SQLite PDF Integration Test")

    # Upload the PDF through the API.
    response = db_client.post(
        "/documents/upload",
        files={
            "file": (
                "integration_test.pdf",
                pdf_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["title"] == "integration_test.pdf"
    assert response_data["filename"] == "integration_test.pdf"
    assert response_data["page_count"] == 1
    assert "SQLite PDF Integration Test" in response_data["extracted_text"]

    # Verify the PDF information was saved in SQLite.
    saved_document = document_repository.get_document_by_id(
        db=db_session,
        document_id=response_data["id"],
    )

    assert saved_document is not None
    assert saved_document.filename == "integration_test.pdf"
    assert saved_document.page_count == 1
    assert "SQLite PDF Integration Test" in saved_document.extracted_text


def test_uploaded_pdf_can_be_retrieved(db_client, make_pdf):
    pdf_content = make_pdf("Persistent PDF Content")

    upload_response = db_client.post(
        "/documents/upload",
        files={
            "file": (
                "persistent.pdf",
                pdf_content,
                "application/pdf",
            )
        },
    )

    assert upload_response.status_code == 201

    document_id = upload_response.json()["id"]

    # Retrieve the uploaded document through the API.
    response = db_client.get(f"/documents/{document_id}")

    assert response.status_code == 200
    assert response.json()["filename"] == "persistent.pdf"
    assert response.json()["page_count"] == 1
    assert "Persistent PDF Content" in response.json()["extracted_text"]