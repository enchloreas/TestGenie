# app/config.py

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env", override=True)  # Load variables from .env file

class Settings(BaseSettings):

    # Available AI models
    AVAILABLE_MODELS: list[str] = ["gpt-3.5-turbo", "gpt-4"]  # Default models, can be overridden

    # TestGenie configuration
    TESTGENIE_VERSION: str = "1.0.0"  # Default version, can be overridden
    TESTGENIE_NAME: str = "TestGenie"  # Default name, can be overridden
    TESTGENIE_DESCRIPTION: str = "AI-powered test case generation tool"  # Default description, can be overridden
    TESTGENIE_AUTHOR: str = "YenEnchloreas"  # Default author, can be overridden
    TESTGENIE_LICENSE: str = "MIT"  # Default license, can be overridden
    TESTGENIE_API_URL: str = "http://localhost:8000"  # Default URL, can be overridden
    
    # Database configuration
    DATABASE_URL: str = "sqlite:///./testgenie.db"  # Production DB
    TEST_DB_URL: str = "sqlite:///./test_db.db"     # Test DB

    # Jira configuration
    JIRA_DOMAIN: str = "your-domain.atlassian.net"
    JIRA_PROJECT_KEY: str = "PROJ"
    JIRA_EMAIL: str = "your-email@example.com"
    JIRA_API_TOKEN: str = "your-jira-api-token"

    # OpenRouter AI configuration
    OPENROUTER_URL: str = "https://openrouter.ai/api"
    OPENROUTER_API_KEY: str = "your-openrouter-api-key"

    # AIO Tests configuration
    AIO_API_TOKEN: str = "your-aio-api-token"
    AIO_API_URL: str = "https://api.aio.com/v1"  # Default URL, can be overridden

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instantiate the settings object
settings = Settings()

print("Loaded JIRA_DOMAIN from env:", settings.JIRA_DOMAIN)
print("Loaded AIO_API_URL from env:", settings.AIO_API_URL)
print("Loaded OPENROUTER_URL from env:", settings.OPENROUTER_URL)
print("Loaded OPENROUTER_API_KEY from env:", settings.OPENROUTER_API_KEY)
print("Loaded AIO_API_TOKEN from env:", settings.AIO_API_TOKEN)