# app/config.py

import os

# Database connection string (SQLite database file will be created in the project root)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./testgenie.db")  # Production DB
TEST_DB_URL = os.getenv("TEST_DB_URL", "sqlite:///./test_db.db")      # Test DB

# Jira configuration
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN", "yen.enchloreas@gmail.com")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "TG")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "yen.enchloreas@gmail.com")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "ATATT3xFfGF0XZHivUf-zV1UHlrN8-fRI9rGFA-eavXu3g5BOM0ZwLhfEgNYucxA1RIyrtYLflagrmWAKYIhn9LJdstqhsd4GqkNQ0oOoGd7_PtcKiT4Q6W3y-1GbpL7Kq_-t6Nlnhb9BDuBRqF8SXIiuTE0NQCPkV8tQJw44NaD3SO7dTPpEtU=29B5C169")
