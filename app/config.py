# app/config.py

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

class Settings(BaseSettings):
    # Database configuration
    DATABASE_URL: str = "sqlite:///./testgenie.db"  # Production DB
    TEST_DB_URL: str = "sqlite:///./test_db.db"     # Test DB

    # Jira configuration
    JIRA_DOMAIN: str
    JIRA_PROJECT_KEY: str
    JIRA_EMAIL: str
    JIRA_API_TOKEN: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instantiate the settings object
settings = Settings()
