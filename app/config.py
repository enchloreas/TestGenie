# app/config.py

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

class Settings(BaseSettings):

    # Available AI models
    AVAILABLE_MODELS: list[str]
    
    # Database configuration
    DATABASE_URL: str = "sqlite:///./testgenie.db"  # Production DB
    TEST_DB_URL: str = "sqlite:///./test_db.db"     # Test DB

    # Jira configuration
    JIRA_DOMAIN: str
    JIRA_PROJECT_KEY: str
    JIRA_EMAIL: str
    JIRA_API_TOKEN: str

    # OpenRouter AI configuration
    OPENROUTER_URL: str
    OPENROUTER_API_KEY: str

    # AIO Tests configuration
    AIO_API_TOKEN: str
    AIO_API_URL: str = "https://api.aio.com/v1"  # Default URL, can be overridden

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instantiate the settings object
settings = Settings()
