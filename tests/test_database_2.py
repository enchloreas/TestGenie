# tests/test_database.py
# Test database connection and model integration
import pytest
from sqlalchemy import inspect
from app.database import Base, engine, db_url, get_db, get_database_url
from app.models import Case

@pytest.fixture(scope="module")
def test_db():
    """
    Fixture to set up and tear down the database.
    """
    print("test_db fixture is being executed")  # Debugging: Ensure the fixture is running
    print(f"Using database URL: {db_url}")  # Debugging: Print the selected database URL
    get_database_url()  # Ensure the correct database URL is used
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)
    # Dispose of the engine to close all connections
    engine.dispose()
    return get_database_url()

def test_database_connection():
    """
    Test that the database connection is valid.
    """
    try:
        # Attempt to connect to the database
        with engine.connect() as connection:
            assert connection is not None, "Failed to connect to the database"
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")

def test_get_db(test_db):
    """
    Test that the get_db() function creates and closes a session properly.
    """
    db_gen = get_db()
    db = next(db_gen)  # Get the database session
    assert db is not None, "get_db() did not return a valid session"
    db_gen.close()  # Close the session

def test_model_integration(test_db):
    """
    Test that the models are correctly integrated with the database.
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "test_cases" in tables, "The 'test_cases' table was not created"

    # Add a new case to verify the model works with the database
    db_gen = get_db()
    db = next(db_gen)
    case = Case(name="Test Case", description="Some description", expected_result="Pass")
    db.add(case)
    db.commit()
    db.refresh(case)

    # Verify the case was added
    assert case.id is not None, "Case ID should not be None after insertion"
    assert case.name == "Test Case", "Case name does not match"
    assert case.description == "Some description", "Case description does not match"
    assert case.expected_result == "Pass", "Case expected result does not match"
    
    # Clean up
    db.close()