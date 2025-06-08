# app/models.py

from sqlalchemy import Column, Integer, String
from .database import Base

"""
Represents a test case entity stored in the database.

This model includes basic fields required for QA automation:
- Title: a short summary of the test case
- Description: detailed test steps or notes
- Expected result: what should happen when the test passes
"""
class Case(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    expected_result = Column(String, index=True)
    tags = Column(String, index=True)  # Tags field as comma-separated string

# Represents a generated test case entity stored in the database.
class GeneratedTestCase(Base):
    __tablename__ = "generated_test_cases"

    id = Column(Integer, primary_key=True, index=True)
    story_key = Column(String(50), index=True)  # Key or identifier for the user story
    title = Column(String(255), index=True)     # Title of the generated test case
    preconditions = Column(String)              # Preconditions for the test case
    steps = Column(String)                      # Steps to execute the test case
    expected_results = Column(String)           # Expected results after execution
    postconditions = Column(String)             # Postconditions after the test case
    tags = Column(String)                       # Tags for categorization, e.g., "TG-1-TC-1"