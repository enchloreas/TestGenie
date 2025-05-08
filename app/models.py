from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

# Base class for all SQLAlchemy models
Base = declarative_base()

class Case(Base):
    """
    Represents a test case entity stored in the database.

    This model includes basic fields required for QA automation:
    - Title: a short summary of the test case
    - Description: detailed test steps or notes
    - Expected result: what should happen when the test passes
    """
    __tablename__ = "test_cases"  # Defines the name of the database table

    id = Column(Integer, primary_key=True, index=True)  # Unique ID for each test case
    title = Column(String(255), nullable=False)         # Required field: test case title
    description = Column(Text, nullable=True)           # Optional field: test case description
    expected_result = Column(Text, nullable=False)      # Required field: expected result of test