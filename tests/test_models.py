# tests/test_models.py

import pytest
from sqlalchemy import inspect
from app.models import Case

# Test to check if the table name is correctly set and exists in the database
def test_table_name(test_db):
    """
    Validate that the table name is correctly set and exists in the database.
    """
    assert Case.__tablename__ == "test_cases", "Table name is incorrect"

    # Validate that the table exists in the database
    inspector = inspect(test_db)  # Pass the engine directly to inspect
    tables = inspector.get_table_names()
    assert "test_cases" in tables, "The 'test_cases' table does not exist in the database"

# Test all fields except `id`
@pytest.mark.parametrize(
    "name, description, expected_result, tags",
    [
        ("Test Login", "Check login with valid credentials", "User is logged in", "UI,smoke"),
        ("Test Logout", "Check logout functionality", "User is logged out", "UI,regression"),
    ],
)
def test_case_fields(name: str, description: str, expected_result: str, tags: str):
    """
    Test that the fields of the Case model are correctly set.
    """
    case = Case(name=name, description=description, expected_result=expected_result, tags=tags)

    assert isinstance(case.name, str)
    assert case.name == name

    assert isinstance(case.description, str)
    assert case.description == description

    assert isinstance(case.expected_result, str)
    assert case.expected_result == expected_result

    assert isinstance(case.tags, str)
    assert case.tags == tags

# Test the 'id' field before DB commit
def test_case_id_initially_none():
    """
    Test that the 'id' field is None before the Case object is committed to the database.
    """
    case = Case(
        name="Check ID",
        description="ID should be None before saving",
        expected_result="Unset ID",
        tags="unit",
    )
    assert case.id is None

# Integration test: verify ID is set after commit to DB
def test_case_id_after_commit(db_session):
    """
    Test that the 'id' field is set after the Case object is committed to the database.
    """
    case = Case(
        name="DB Save",
        description="Should get ID",
        expected_result="ID assigned",
        tags="db",
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    assert isinstance(case.id, int)
    assert case.id > 0

    # Cleanup
    db_session.delete(case)
    db_session.commit()

# Optional: test that all fields are of expected types
def test_case_field_types():
    """
    Test that all fields of the Case model are of the expected types.
    """
    case = Case(
        name="Type Test",
        description="Test all types",
        expected_result="Pass",
        tags="smoke",
    )
    assert isinstance(case.name, str)
    assert isinstance(case.description, str)
    assert isinstance(case.expected_result, str)
    assert isinstance(case.tags, str)
    assert case.id is None or isinstance(case.id, int)
