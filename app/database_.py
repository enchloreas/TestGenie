# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base 
from .config import DATABASE_URL, TEST_DB_URL  # Import the database URL from config
import pytest

# Check if pytest is running in test mode (this could be passed via command-line options)
def get_database_url():
    if pytest.config.getoption("--test"):
        return TEST_DB_URL  # Use the test database
    return DATABASE_URL  # Otherwise, use the main database URL

db_url = get_database_url()
print(db_url)
# Create engine for SQLite DB
engine = create_engine(
    db_url, connect_args={"check_same_thread": False}
)

# Session factory for the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
