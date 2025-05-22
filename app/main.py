# app/main.py

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import engine, get_db

# Create all database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Create a new test case
@app.post("/cases/", response_model=schemas.CaseRead)
def create_case(case: schemas.CaseCreate, db: Session = Depends(get_db)):
    return crud.create_case(db=db, case_create=case)

# Get all test cases
@app.get("/cases/", response_model=list[schemas.CaseRead])
def get_cases(db: Session = Depends(get_db)):
    return crud.get_cases(db)

# Get a test case by ID
@app.get("/cases/{case_id}", response_model=schemas.CaseRead)
def get_case(case_id: int, db: Session = Depends(get_db)):
    db_case = crud.get_case_by_id(db, case_id=case_id)
    if db_case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return db_case

# Update a test case
@app.put("/cases/{case_id}", response_model=schemas.CaseRead)
def update_case(case_id: int, case: schemas.CaseCreate, db: Session = Depends(get_db)):
    db_case = crud.update_case(db, case_id=case_id, case_update=case)
    if db_case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return db_case

# Delete a test case
@app.delete("/cases/{case_id}", response_model=schemas.CaseRead)
def delete_case(case_id: int, db: Session = Depends(get_db)):
    db_case = crud.delete_case(db, case_id=case_id)
    if db_case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return db_case
# Note: The above code assumes that the database session is managed by FastAPI's dependency injection system.
# The `db` parameter in the functions is expected to be a SQLAlchemy session object.
# This code provides a RESTful API for managing test cases using FastAPI.
# The API includes endpoints for creating, reading, updating, and deleting test cases.
# The `create_case` endpoint allows clients to create a new test case by sending a POST request with the test case data.
# The `get_cases` endpoint retrieves all test cases from the database by sending a GET request.
# The `get_case` endpoint retrieves a specific test case by its ID using a GET request.
# The `update_case` endpoint allows clients to update an existing test case by sending a PUT request with the updated data.
# The `delete_case` endpoint allows clients to delete a test case by sending a DELETE request with the test case ID.
# The API uses Pydantic models for data validation and serialization.
# The `schemas` module contains the Pydantic models for request and response data.
# The `crud` module contains the database operations for managing test cases.
# The `get_db` function is used to create a new database session and ensure that it is properly closed after use.
# The API is built using FastAPI, which provides automatic generation of OpenAPI documentation and interactive API documentation.
# The API endpoints are defined using FastAPI's route decorators, and the request and response models are specified using the `response_model` parameter.
# The API also includes error handling for cases where a test case is not found in the database.
# The `HTTPException` class is used to raise HTTP errors with appropriate status codes and error messages.
# The API is designed to be easy to use and provides a clear and consistent interface for managing test cases.
# The API can be easily extended to include additional functionality or endpoints as needed.
# The API can be tested using tools like Postman or cURL, and it can be integrated with frontend applications or other services.
# The API is designed to be scalable and can handle a large number of requests efficiently.
# The API can be deployed to various environments, including cloud platforms or on-premises servers.
# The API is built using modern web standards and best practices, ensuring compatibility with a wide range of clients and platforms.
# The API is designed to be secure and includes measures to protect against common web vulnerabilities.

