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
