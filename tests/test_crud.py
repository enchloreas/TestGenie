# tests/test_crud.py

import pytest
from app import crud, schemas
from sqlalchemy import inspect
from app.models import Case

def test_create_case(test_db, db_session):
    """
    Test the creation of a new test case.
    """
    case_data = schemas.CaseCreate(
        name="Test Case 1",
        description="This is a test case",
        expected_result="Pass",
        tags="unit"
    )
    created_case = crud.create_case(db_session, case_data)

    assert created_case.id is not None, "Case ID should not be None after creation"
    assert created_case.name == case_data.name
    assert created_case.description == case_data.description
    assert created_case.expected_result == case_data.expected_result
    assert created_case.tags == case_data.tags

def test_get_cases(test_db, db_session):
    """
    Test retrieving all test cases.
    """
    case_data_1 = schemas.CaseCreate(
        name="Test Case 1",
        description="This is the first test case",
        expected_result="Pass",
        tags="unit"
    )
    case_data_2 = schemas.CaseCreate(
        name="Test Case 2",
        description="This is the second test case",
        expected_result="Fail",
        tags="integration"
    )
    crud.create_case(db_session, case_data_1)
    crud.create_case(db_session, case_data_2)

    cases = crud.get_cases(db_session)
    assert len(cases) == 2, "There should be 2 test cases in the database"
    assert cases[0].name == case_data_1.name
    assert cases[1].name == case_data_2.name

def test_get_case_by_id(db_session):
    """
    Test retrieving a test case by its ID.
    """
    case_data = schemas.CaseCreate(
        name="Test Case 1",
        description="This is a test case",
        expected_result="Pass",
        tags="unit"
    )
    created_case = crud.create_case(db_session, case_data)

    retrieved_case = crud.get_case_by_id(db_session, created_case.id)
    assert retrieved_case is not None, "Retrieved case should not be None"
    assert retrieved_case.id == created_case.id
    assert retrieved_case.name == created_case.name

def test_update_case(db_session):
    """
    Test updating an existing test case.
    """
    case_data = schemas.CaseCreate(
        name="Test Case 1",
        description="This is a test case",
        expected_result="Pass",
        tags="unit"
    )
    created_case = crud.create_case(db_session, case_data)

    updated_data = schemas.CaseCreate(
        name="Updated Test Case",
        description="This is an updated test case",
        expected_result="Fail",
        tags="integration"
    )
    updated_case = crud.update_case(db_session, created_case.id, updated_data)

    assert updated_case is not None, "Updated case should not be None"
    assert updated_case.id == created_case.id
    assert updated_case.name == updated_data.name
    assert updated_case.description == updated_data.description
    assert updated_case.expected_result == updated_data.expected_result
    assert updated_case.tags == updated_data.tags

def test_delete_case(db_session):
    """
    Test deleting a test case.
    """
    case_data = schemas.CaseCreate(
        name="Test Case 1",
        description="This is a test case",
        expected_result="Pass",
        tags="unit"
    )
    created_case = crud.create_case(db_session, case_data)

    deleted_case = crud.delete_case(db_session, created_case.id)
    assert deleted_case is not None, "Deleted case should not be None"
    assert deleted_case.id == created_case.id

    # Verify the case is no longer in the database
    retrieved_case = crud.get_case_by_id(db_session, created_case.id)
    assert retrieved_case is None, "Case should no longer exist in the database"