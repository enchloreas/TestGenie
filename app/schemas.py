# app/schemas.py

from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict

# ---------------------------
# Base models for FastAPI
# ---------------------------

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
    
# ----------------------------------------
# Models for OpenRouter (LLM) integration
# ----------------------------------------
class GeneratedTestCaseBase(BaseModel):
    story_key: str
    title: str
    preconditions: Optional[str] = None
    steps: str
    expected_results: str
    postconditions: Optional[str] = None
    tags: Optional[str] = None  # Comma-separated tags (e.g., "TG-1-TC-1")

class GeneratedTestCaseCreate(GeneratedTestCaseBase):
    pass  # Inherits all fields from base for creation

class GeneratedTestCaseResponse(GeneratedTestCaseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)  # Updated to use ConfigDict

# ---------------------------
# Models for creating AIO Test via Jira API
# ---------------------------

# --- Test Case ---
class JiraTestCaseCreate(BaseModel):
    user_story_key: str  # Jira user story key where the test case will be added
    title: str  # Title of the test case in AIO
    description: str  # Detailed description of the test case
    issue_type: str = "Test"  # Jira issue type for the test case (AIO uses Test)
    expected_result: Optional[str] = None  # Expected result of the test case
    steps: Optional[List[str]] = None  # Steps of the test case
    pre_condition: Optional[str] = None  # Pre-condition for the test case
    tags: Optional[List[str]] = None  # Tags or labels for the test case

# --- Test Set ---
class JiraTestSetCreate(BaseModel):
    name: str  # Name of the test set
    description: Optional[str] = None  # Description of the test set
    test_case_keys: List[str]  # List of test case issue keys to include in set

# --- Test Cycle ---
class JiraTestCycleCreate(BaseModel):
    name: str  # Name of the test cycle
    description: Optional[str] = None  # Description of the test cycle
    test_set_keys: List[str]  # List of test set issue keys to include in cycle

