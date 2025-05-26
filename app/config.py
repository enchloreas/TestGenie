# app/config.py

import os
from dotenv import load_dotenv
load_dotenv()
# Database connection string (SQLite database file will be created in the project root)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./testgenie.db")  # Production DB
TEST_DB_URL = os.getenv("TEST_DB_URL", "sqlite:///./test_db.db")      # Test DB

# Jira configuration
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
