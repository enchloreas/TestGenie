import pytest
from app.models import Case

# Test to check if the table name is correctly set
def test_table_name():
    assert Case.__tablename__ == "test_cases", "Table name is incorrect"

# Test to check if the class name is correctly set
def test_class_name():
    assert Case.__name__ == "Case", "Class name is incorrect"