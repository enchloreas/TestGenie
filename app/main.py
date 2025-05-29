# app/main.py

from fastapi import FastAPI, Depends, HTTPException, Path, Query
from typing import List, Dict
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import engine, get_db
from app.jira_service import JiraService
from app.config import JIRA_DOMAIN, JIRA_EMAIL, JIRA_API_TOKEN

# Create all database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Initialize JiraService instance with configuration from config.py
jira_service = JiraService(JIRA_DOMAIN, JIRA_EMAIL, JIRA_API_TOKEN)

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

### JIRA INTEGRATION ENDPOINTS ###

# Jira stories endpoint
@app.get("/jira/stories/")
def get_jira_stories(
    project_key: str = Query(..., description="Jira project key, e.g. 'TG'"),
    issue_type: str = Query(..., description="Jira issue type, e.g. 'Story'")
) -> List[Dict]:
    # Fetch all user stories from Jira for the specified project and issue type
    print("Endpoint /jira/stories/ called")
    try:
        stories = jira_service.get_all_user_stories(project_key, issue_type)
        return stories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stories: {str(e)}")

# Jira single story endpoint by issue key
@app.get("/jira/story/{issue_key}")
def get_jira_story_by_key(
    issue_key: str = Path(..., description="Jira issue key, e.g. 'TG-1'")
) -> Dict:
    # Fetch a single user story from Jira by its issue key
    print(f"Endpoint /jira/story/{issue_key} called")
    try:
        story = jira_service.get_user_story_by_key(issue_key)
        return story
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch story: {str(e)}")
