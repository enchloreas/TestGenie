# app/pm_service.py

import requests
import json
import logging
import re
from typing import List, Dict
from .config import settings
from .jira_service import JiraService
from .ai_service import AIService
# Configure logging
logging.basicConfig(level=logging.INFO)

class PMService:
    def __init__(
        self,
        aio_api_url: str,
        aio_api_token: str,
        jira_domain: str,
        jira_email: str,
        jira_api_token: str,
        openrouter_url: str,
        openrouter_api_key: str

    ):
        """
        Initialize PMService with configuration from settings.
        """
        self.aio_api_url = aio_api_url or settings.AIO_API_URL
        self.aio_api_token = aio_api_token or settings.AIO_API_TOKEN
        self.jira_service = JiraService(
            domain=jira_domain or settings.JIRA_DOMAIN,
            email=jira_email or settings.JIRA_EMAIL,
            api_token=jira_api_token or settings.JIRA_API_TOKEN
        )

        self.ai_service = AIService(
            jira_domain=jira_domain or settings.JIRA_DOMAIN,
            jira_email=jira_email or settings.JIRA_EMAIL,
            jira_api_token=jira_api_token or settings.JIRA_API_TOKEN,
            openrouter_url=openrouter_url or settings.OPENROUTER_URL,
            openrouter_api_key=openrouter_api_key or settings.OPENROUTER_API_KEY
        )
        # Set authorization headers
        self.headers = {
            "Authorization": f"AioAuth {self.aio_api_token}",
            "Content-Type": "application/json"
        }

    def test_aio_connection(self) -> bool:
        """
        Test connection to AIO API by making a simple GET request to a known endpoint.
        """
        jira_project_id = "TG"  # заменишь на реальный ID проекта
        url = f"{self.aio_api_url}/project/{jira_project_id}/testcase"  # или другой рабочий endpoint AIO
        # https://tcms.aiojiraapps.com/aio-tcms/api/v1/project/TG/testcase
        print(f"Testing AIO connection to URL: {url}")
        headers = {
            "Authorization": f"AioAuth {self.aio_api_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
            logging.info(f"AIO connection test status: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Failed to connect to AIO API: {e}")
            return False

    def test_jira_connection(self) -> bool:
        """
        Test connection to Jira by fetching a dummy issue (replace key with a real one).
        """
        try:
            issue = self.jira_service.get_all_user_stories("TG", "Story")  # заменишь на реальный ключ
            logging.info(f"Connected to Jira. Found {len(issue)} issues.")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to Jira: {e}")
            return False
        
    def test_ai_connection(self) -> bool:
        """
        Test connection to AI service by making a simple request.
        """
        try:
            response = self.ai_service.process_jira_story_and_send_to_openrouter(
                issue_key="TG-1",  
                model="meta-llama/llama-3-8b-instruct",  
                temperature=0.7,
                max_tokens=1000
            )
            if "error" in response:
                logging.error(f"AI connection test failed: {response['error']}")
                return False
            logging.info("AI connection test succeeded.")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to AI service: {e}")
            return False

#------------------------------------------------------------------------------------------------------
# Add generated test cases to Jira story
#------------------------------------------------------------------------------------------------------
    def send_to_aio(self, project_key: str, test_case: dict):

        aio_url = f"{self.aio_api_url}/project/{project_key}/testcase" 
        headers = {
            "Authorization": f"AioAuth {self.aio_api_token}",  # Use the instance's token
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(aio_url, json=test_case, headers=headers)
            if response.status_code == 200:
                logging.info(f"AIO: Test case created successfully: {test_case['title']}")
            else:
                logging.error(f"AIO: Test case failed {test_case['title']} | Status: {response.status_code} | Response: {response.text}")
        except Exception as e:
            logging.error(f"AIO: ConnectionError {test_case['title']}: {e}")
        
        return "Test case created successfully" if response.status_code == 200 else {"error": response.text}
            
    def add_generated_test_cases_to_jira(
            self, 
            project_key: str, 
            issue_key: str, 
            model: str="meta-llama/llama-3-8b-instruct",
            temperature: float=0.7,
            max_tokens: int=666
            ) -> List[Dict]:
        """
        Add generated test cases to a Jira story.
        :param issue_key: Jira issue key, e.g. 'TG-1'
        :param test_cases: List of test case dictionaries to add
        :return: True if successful, False otherwise
        """
        test_cases = self.ai_service.generate_and_normalize_test_cases(
            issue_key,
            model,
            temperature,
            max_tokens
        )
        try:
            for case in test_cases:
                # Assuming the AI service returns a dictionary with 'summary' and 'description'
                send_to_aio_response = self.send_to_aio(project_key, case)
                
            logging.info(f"Added {len(test_cases)} test cases to Jira story {issue_key}.")
            return test_cases
        except Exception as e:
            logging.error(f"Failed to add test cases to Jira: {e}")
            return f"Added {len(test_cases)} test cases to Jira story {issue_key}."
            
                
if __name__ == "__main__":
    service = PMService(
        aio_api_url=settings.AIO_API_URL,
        aio_api_token=settings.AIO_API_TOKEN,
        jira_domain=settings.JIRA_DOMAIN,
        jira_email=settings.JIRA_EMAIL,
        jira_api_token=settings.JIRA_API_TOKEN,
        openrouter_url=settings.OPENROUTER_URL,
        openrouter_api_key=settings.OPENROUTER_API_KEY
    )
    print("AIO URL from settings:", settings.AIO_API_URL)
    print("Jira Domain from settings:", settings.JIRA_DOMAIN)
    print("OpenRouter url ffrom setting:", settings.OPENROUTER_URL)
    
    print("Testing AIO connection:")
    print(service.test_aio_connection())

    print("Testing Jira connection:")
    print(service.test_jira_connection())

    print("Testing AI connection:")
    print(service.test_ai_connection())

    print("Adding generated test cases to Jira:")
    result = service.add_generated_test_cases_to_jira("TG", "TG-2")
    print("Result of adding test cases:", result)
