# app/crud.py

from sqlalchemy.orm import Session  # Correct type for DB session
from app import models, schemas

# Create a new test case
def create_case(db: Session, case_create: schemas.CaseCreate):
    db_case = models.Case(**case_create.model_dump())  # Unpack Pydantic model with model_dump
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

# Get all test cases
def get_cases(db: Session):
    return db.query(models.Case).all()

# Get a test case by ID
def get_case_by_id(db: Session, case_id: int):
    return db.query(models.Case).filter(models.Case.id == case_id).first()

# Update an existing test case
def update_case(db: Session, case_id: int, case_update: schemas.CaseCreate):
    db_case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if db_case:
        for var, value in case_update.model_dump().items():
            setattr(db_case, var, value)
        db.commit()
        db.refresh(db_case)
    return db_case

# Delete a test case
def delete_case(db: Session, case_id: int):
    db_case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if db_case:
        db.delete(db_case)
        db.commit()
    return db_case

# ----------------------------------------
# Models for OpenRouter (LLM) integration
# ----------------------------------------
def create_generated_test_case(db: Session, test_case: schemas.GeneratedTestCaseCreate):
    # Create a new GeneratedTestCase object and add it to the database
    db_test_case = models.GeneratedTestCase(**test_case.dict())
    db.add(db_test_case)
    db.commit()
    db.refresh(db_test_case)
    return db_test_case

def get_generated_test_case(db: Session, test_case_id: int):
    # Retrieve a GeneratedTestCase by its ID
    return db.query(models.GeneratedTestCase).filter(models.GeneratedTestCase.id == test_case_id).first()

def get_generated_test_cases(db: Session, skip: int = 0, limit: int = 10):
    # Retrieve a list of GeneratedTestCase objects with pagination
    return db.query(models.GeneratedTestCase).offset(skip).limit(limit).all()


# Note: The above code assumes that the database session is managed by FastAPI's dependency injection system.
# The `db` parameter in the functions is expected to be a SQLAlchemy session object.
# This code provides basic CRUD operations for managing test cases in a database.
# The functions include creating, reading, updating, and deleting test cases.   
# The `create_case` function creates a new test case in the database.
# The `get_cases` function retrieves all test cases from the database.  
# The `get_case_by_id` function retrieves a specific test case by its ID.
# The `update_case` function updates an existing test case in the database.
# The `delete_case` function deletes a test case from the database.
# The code uses SQLAlchemy ORM to interact with the database and Pydantic models for data validation.
# The `model_dump` method is used to convert the Pydantic model to a dictionary, which is then unpacked into the SQLAlchemy model.
# The `setattr` function is used to update the attributes of the SQLAlchemy model with the new values from the Pydantic model.
# The `db.commit()` method is called to save the changes to the database, and `db.refresh()` is used to refresh the instance with the latest data from the database.
# The `db.delete()` method is used to delete the test case from the database.
# The code also includes error handling to check if the test case exists before attempting to update or delete it.
# The `db.query()` method is used to create a query object for the specified model, and the `filter()` method is used to filter the results based on the specified condition.
# The `first()` method is used to retrieve the first result of the query, or `None` if no results are found.
# The `all()` method is used to retrieve all results of the query.
# The code is designed to be used with FastAPI, which provides a convenient way to manage database sessions using dependency injection.
# The `get_db()` function is used to create a new database session and ensure that it is properly closed after use.
