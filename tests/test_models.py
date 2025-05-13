import pytest
from app.models import Case

# Test to check if the table name is correctly set
def test_table_name():
    assert Case.__tablename__ == "test_cases", "Table name is incorrect"

# Test to check if the class name is correctly set
def test_class_name():
    assert Case.__name__ == "Case", "Class name is incorrect"

def test_case_fields():
    # Create a case with tags
    case = Case(
        name="Test Login",
        description="Check login with valid credentials",
        expected_result="User is logged in",
        tags="UI,smoke"
    )

    # Check the field type and value for name
    assert isinstance(case.name, str)  # Name should be a string
    assert case.name == "Test Login"  # Name should match the input string

    # Check the field type and value for description
    assert isinstance(case.description, str)  # Description should be a string
    assert case.description == "Check login with valid credentials"  # Description should match the input string

    # Check the field type and value for expected_result
    assert isinstance(case.expected_result, str)  # Expected result should be a string
    assert case.expected_result == "User is logged in"  # Expected result should match the input stringg

    # Check the field type and value for tags
    assert isinstance(case.tags, str)  # Tags should be a string
    assert case.tags == "UI,smoke"     # Tags should match the input string