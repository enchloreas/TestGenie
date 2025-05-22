# tests/test_main.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import schemas, crud
from app.database import get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_get_db(db_session):
    """
    Override the get_db dependency with the test db_session.
    """
    def _get_test_db():
        yield db_session
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()

def test_create_case_api(test_db, db_session):
    """
    Test creating a case via the API.
    """
    payload = {
        "name": "API Case",
        "description": "Test case created through API",
        "expected_result": "Success",
        "tags": "api"
    }

    response = client.post("/cases/", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] is not None
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["expected_result"] == payload["expected_result"]
    assert data["tags"] == payload["tags"]

def test_get_cases_api(test_db, db_session):
    """
    Test retrieving all cases via API.
    """
    # Prepare data using CRUD directly
    crud.create_case(db_session, schemas.CaseCreate(
        name="Case 1",
        description="Desc 1",
        expected_result="Pass",
        tags="tag1"
    ))
    crud.create_case(db_session, schemas.CaseCreate(
        name="Case 2",
        description="Desc 2",
        expected_result="Fail",
        tags="tag2"
    ))

    response = client.get("/cases/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] == "Case 1"
    assert data[1]["name"] == "Case 2"

def test_get_case_by_id_api(test_db, db_session):
    """
    Test retrieving a case by ID via API.
    """
    new_case = crud.create_case(db_session, schemas.CaseCreate(
        name="Single Case",
        description="Only one",
        expected_result="Pass",
        tags="single"
    ))

    response = client.get(f"/cases/{new_case.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == new_case.id
    assert data["name"] == "Single Case"

def test_update_case_api(test_db, db_session):
    """
    Test updating a case via the API.
    """
    existing_case = crud.create_case(db_session, schemas.CaseCreate(
        name="Old Case",
        description="Old Desc",
        expected_result="Fail",
        tags="old"
    ))

    payload = {
        "name": "Updated Case",
        "description": "Updated Desc",
        "expected_result": "Pass",
        "tags": "new"
    }

    response = client.put(f"/cases/{existing_case.id}", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == existing_case.id
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["expected_result"] == payload["expected_result"]
    assert data["tags"] == payload["tags"]

def test_delete_case_api(test_db, db_session):
    """
    Test deleting a case via the API.
    """
    new_case = crud.create_case(db_session, schemas.CaseCreate(
        name="Delete Me",
        description="To be removed",
        expected_result="Fail",
        tags="delete"
    ))

    response = client.delete(f"/cases/{new_case.id}")
    assert response.status_code == 200

    # Confirm deletion via GET
    get_response = client.get(f"/cases/{new_case.id}")
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Case not found"}
    