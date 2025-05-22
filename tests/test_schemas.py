# tests/test_schemas.py

from app.schemas import CaseBase, CaseCreate, CaseRead

def test_case_base_schema():
    data = {
        "name": "Login test",
        "description": "Test login with valid credentials",
        "expected_result": "User should be logged in",
        "tags": "UI,smoke"
    }

    schema = CaseBase(**data)
    assert schema.name == data["name"]
    assert schema.description == data["description"]
    assert schema.expected_result == data["expected_result"]
    assert schema.tags == data["tags"]

def test_case_create_schema():
    data = {
        "name": "Register test",
        "description": "Test registration with valid data",
        "expected_result": "User should be registered",
        "tags": "UI,regression"
    }

    schema = CaseCreate(**data)
    assert isinstance(schema, CaseCreate)

def test_case_read_schema():
    data = {
        "id": 1,
        "name": "Reset password",
        "description": "Test reset password flow",
        "expected_result": "User should receive reset link",
        "tags": "API,critical"
    }

    schema = CaseRead(**data)
    assert schema.id == 1
    assert schema.name == data["name"]
    assert schema.description == data["description"]
    assert schema.expected_result == data["expected_result"]
    assert schema.tags == data["tags"]
    