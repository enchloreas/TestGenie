# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base 
from .config import settings
# Create engine for SQLite DB
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
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
