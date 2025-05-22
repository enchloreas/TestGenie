# tests/conftest.py

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import TEST_DB_URL
from app.database import Base

# Create a test engine using the test database URL
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="module")
def test_db():
    """
    Fixture to set up and tear down the test database.
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)  # This is where the tables are created
    yield test_engine  # Provide the test engine to the test
    # Drop all tables after the test
    Base.metadata.drop_all(bind=test_engine) # This is where the tables are dropped
    # Dispose of the engine
    test_engine.dispose()

@pytest.fixture
def db_session():
    """
    Fixture to provide a database session for each test.
    """
    # Truncate all tables to ensure a clean state
    with test_engine.connect() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(text(f"DELETE FROM {table.name}"))  # Use text() for raw SQL
        connection.commit()

    # Create a new session
    db = TestingSessionLocal() # Create a new session
    
    try:
        yield db
    finally:
        db.close()
