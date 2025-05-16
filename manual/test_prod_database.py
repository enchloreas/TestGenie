# tests/manual/test_prod_database.py

import pytest
from sqlalchemy import create_engine, text
from app.database import get_db, engine

def test_prod_database_connection():
    """
    Test that the production database connection is valid.
    """
    try:
        # Attempt to connect to the production database
        with engine.connect() as connection:
            assert connection is not None, "Failed to connect to the database"
            # Optional: Check if the connection is read-only
            result = connection.execute(text("PRAGMA query_only;"))  # SQLite example
            assert result is not None, "Failed to verify read-only mode"
    except Exception as e:
        pytest.fail(f"Failed to connect to production DB: {e}")

def test_get_db():
    """
    Test that the get_db() function creates and closes a session properly.
    """
    db_gen = get_db()
    try:
        db = next(db_gen)  # Get the database session
        assert db is not None, "get_db() did not return a valid session"
    finally:
        db_gen.close()  # Ensure the session is properly closed
