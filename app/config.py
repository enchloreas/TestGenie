# app/config.py

import os

# Database connection string (SQLite database file will be created in the project root)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./testgenie.db")  # Production DB
TEST_DB_URL = os.getenv("TEST_DB_URL", "sqlite:///./test_db.db")      # Test DB

# Jira configuration
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN", "https://yenenchloreas.atlassian.net")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "TG")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "yen.enchloreas@gmail.com")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "ATATT3xFfGF0kinYZlMhMgoPdLHo88oy0D68vtJZWvc1k4f7SdolqtS7S9i3U8jFGm9k0DCvTqfSrHlGJe6LzY4oCMsPBAM0UT-ZKoE0gblLUXZ2M_OpFPWm-ohfannvRmS3UZUeymeDBwb4B-CXA_8g-78CCvK1WSRHvVaZ91nAf2JnmNaknIM=F2AE91D8")
