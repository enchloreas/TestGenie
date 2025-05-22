# app/schemas.py

from pydantic import BaseModel, ConfigDict
from typing import Optional

# Base schema for a test case
class CaseBase(BaseModel):
    name: str
    description: str
    expected_result: str
    tags: Optional[str] = None  # Comma-separated tags (e.g., "UI,regression")

# Schema for creating a test case
class CaseCreate(CaseBase):
    pass

# Schema for returning a test case
class CaseRead(CaseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)  # Updated to use ConfigDict
