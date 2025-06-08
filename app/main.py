# app/main.py

from fastapi import FastAPI, Depends, HTTPException, Path, Query, Body
from typing import List, Dict
from sqlalchemy.orm import Session
from app import models, schemas, crud
from app.database import engine, get_db
from app.jira_service import JiraService
from app.ai_service import AIService
from app.pm_service import PMService
from app.config import settings
from app.schemas import JiraTestCaseCreate
import logging


# Create all database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Initialize JiraService instance with configuration from config.py
jira_service = JiraService(settings.JIRA_DOMAIN, settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)

# Initialize the AIService
ai_service = AIService(
    jira_domain=settings.JIRA_DOMAIN,
    jira_email=settings.JIRA_EMAIL,
    jira_api_token=settings.JIRA_API_TOKEN,
    openrouter_url=settings.OPENROUTER_URL,
    openrouter_api_key=settings.OPENROUTER_API_KEY
)
# Initialize the PMService
pm_service = PMService(
    jira_domain=settings.JIRA_DOMAIN,
    jira_email=settings.JIRA_EMAIL,
    jira_api_token=settings.JIRA_API_TOKEN,
    openrouter_url=settings.OPENROUTER_URL,
    openrouter_api_key=settings.OPENROUTER_API_KEY,
    aio_api_url=settings.AIO_API_URL,           # <-- add this
    aio_api_token=settings.AIO_API_TOKEN        # <-- add this
)

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

# Endpoint to generate test cases with AI for a Jira story
@app.post("/jira/story/{issue_key}/generate-test-cases")
async def generate_test_cases(
    issue_key: str = Path(..., description="Jira issue key, e.g., TG-1"),
    model: str = Query("meta-llama/llama-3-8b-instruct", description="OpenRouter model to use. Available options: " + ", ".join(settings.AVAILABLE_MODELS)),
    temperature: float = Query(0.7, description="Temperature setting for OpenRouter"),
    max_tokens: int = Query(666, description="Maximum token limit for OpenRouter"),
    db: Session = Depends(get_db)
):
    """
    Generate structured test cases for a Jira story using OpenRouter AI.
    """
    try:
        # Use the new method from AIService that handles normalization
        test_cases = ai_service.generate_and_normalize_test_cases(
            issue_key=issue_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        if not test_cases:
            raise HTTPException(status_code=500, detail="No valid test cases could be generated")

        # Return the results
        return {
            "message": f"Successfully generated and saved {len(test_cases)} test cases",
            "total_generated": len(test_cases),
            "test_cases": test_cases
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging.error(f"Unexpected error in generate_test_cases: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Endpoint to create in Jira generated test cases with AI for a Jira story    
@app.post("/jira/project/{project_key}/story/{issue_key}/create-generated-test-cases")
async def generate_test_cases(
    project_key: str = Path(..., description="Jira project key, e.g. 'TG'"),   
    issue_key: str = Path(..., description="Jira issue key, e.g., TG-1"),
    model: str = Query("meta-llama/llama-3-8b-instruct", description="OpenRouter model to use. Available options: " + ", ".join(settings.AVAILABLE_MODELS)),
    temperature: float = Query(0.7, description="Temperature setting for OpenRouter"),
    max_tokens: int = Query(666, description="Maximum token limit for OpenRouter"),
    db: Session = Depends(get_db)
):
    """
    Generate structured test cases for a Jira story using OpenRouter AI.
    """
    try:
        # Use the new method from AIService that handles normalization
        test_cases = pm_service.add_generated_test_cases_to_jira(
            project_key, 
            issue_key, 
            model,
            temperature,
            max_tokens
            )

        if not test_cases:
            raise HTTPException(status_code=500, detail="No valid test cases could be generated")

       

        # Return the results
        return {
            "message": f"Successfully generated and saved {len(test_cases)} test cases",
            "total_generated": len(test_cases),
            "test_cases": test_cases
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logging.error(f"Unexpected error in generate_test_cases: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")