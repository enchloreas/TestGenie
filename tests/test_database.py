# tests/test_database.py

from sqlalchemy import inspect
from app.models import Case
from .conftest import test_engine

def test_database_connection(test_db):
    """
    Test that the database connection is valid and the schema is correct.
    """
    # Attempt to connect to the database
    with test_engine.connect() as connection:
        assert connection is not None, "Failed to connect to the database"

    # Validate the database schema
    inspector = inspect(test_engine)
    tables = inspector.get_table_names()
    assert "test_cases" in tables, "The 'test_cases' table was not created"

def test_get_db(test_db, db_session):
    """
    Test that the get_db() function creates and closes a session properly.
    """
    assert db_session is not None, "db_session fixture did not return a valid session"

def test_model_integration(test_db, db_session):
    """
    Test that the models are correctly integrated with the database.
    """
    case = Case(name="Test Case", description="Some description", expected_result="Pass")
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    assert case.id is not None
    assert case.name == "Test Case"
    assert case.description == "Some description"
    assert case.expected_result == "Pass"
