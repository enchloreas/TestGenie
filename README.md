# TestGenie

TestGenie helps QA engineers generate, manage, and integrate test cases from user stories and change requests.  
It provides seamless integration with Jira and GitHub Actions for CI/CD automation.

# Structure

TestGenie/
├── app/                 # Main application code
│   ├── __init__.py      # Initialize app
│   ├── models.py        # Database models (SQLAlchemy)
│   ├── schemas.py       # Pydantic models for request validation
│   ├── crud.py          # CRUD operations
│   ├── main.py          # FastAPI app initialization
├── migrations/          # For database migrations (alembic or similar)
├── tests/               # Unit tests for your application
│   ├── __init__.py      # Init file for tests folder
│   ├── test_main.py     # Example test file
├── .gitignore           # Git ignore file
├── requirements.txt     # List of all dependencies
├── README.md            # Project overview and documentation
└── venv/                # Virtual environment folder

# Notes for Contributors:
- The app/ directory contains all the main logic of the application and should be treated as a Python package.
- Each subdirectory within app/ serves a specific purpose (routes, models, services, schemas, config).
- tests/ must mirror the structure of app/ for proper unit test coverage.
main.py is where you mount routes and include middlewares.
- Do not commit .env or venv/ — these are personal and environment-specific.