# app/ai_service.py

import requests
import json
import logging
import re
from typing import List, Dict
from .config import settings
from .jira_service import JiraService

# Configure logging
logging.basicConfig(level=logging.INFO)

class AIService:
    def __init__(
        self,
        jira_domain: str = None,
        jira_email: str = None,
        jira_api_token: str = None,
        openrouter_url: str = None,
        openrouter_api_key: str = None,
    ):
        """
        Initialize AIService with configuration from settings.
        """
        self.jira_service = JiraService(
            domain=jira_domain or settings.JIRA_DOMAIN,
            email=jira_email or settings.JIRA_EMAIL,
            api_token=jira_api_token or settings.JIRA_API_TOKEN
        )

        self.openrouter_url = openrouter_url or settings.OPENROUTER_URL
        self.openrouter_api_key = openrouter_api_key or settings.OPENROUTER_API_KEY
              
    
    @staticmethod
    def flatten_adf_description(adf: dict) -> str:
        """
        Flatten the Atlassian Document Format (ADF) description to plain text.
        :param adf: ADF structure (dict) from the Jira story's description field
        :return: Plain text description
        """
        plain_text = []

        def extract_text(nodes):
            # Recursively extract text from ADF nodes
            for node in nodes:
                if node.get("type") == "text":
                    plain_text.append(node.get("text", ""))
                elif "content" in node:
                    extract_text(node["content"])

        if adf and isinstance(adf, dict):
            extract_text(adf.get("content", []))
        
        return " ".join(plain_text)

#-----------------------------------------------------------------------------------------------------------
    @staticmethod
    def create_test_case_prompt(story_key: str, story_id: str, summary: str, description: str) -> str:
        """
        Create a prompt for OpenRouter AI to generate multiple structured test cases in a specific JSON format.
        :param story_key: Jira story key, e.g. 'TG-1'
        :param summary: Story summary
        :param description: Flattened story description
        :return: Prompt string
        """
        prompt = (
            f"You are a professional QA engineer.\n"
            f"Based on the following Jira story, generate as many relevant test cases as needed.\n"
            f"Jira Key: {story_key}\n"
            f"Story ID: {story_id}\n"
            f"Summary: {summary}\n"
            f"Description: {description}\n\n"
            "Each test case must be a JSON object with the following fields:\n"
            "- title (string)\n"
            "- description (string)\n"
            "- precondition (string, optional)\n"
            "- status (object, always exactly this value: {\"name\": \"Published\", \"description\": \"The test is ready for execution\"})\n"
            "- scriptType (object, always exactly this value: {\"name\": \"Classic\", \"description\": \"Steps represented in default representation - step, data and expected results\", \"isEnabled\": true})\n"
            "- steps (array of objects, each with: step (string), data (string, optional), expectedResult(string), stepType(string, always exactly this value):\"TEXT\")\n"
            "- jiraRequirementIDs (array of strings, always contains the story ID)\n\n"
            "Example:\n"
            "[\n"
            "  {\n"
            "    \"title\": \"Update user profile name\",\n"
            "    \"description\": \"Verify that a user can log in with valid email and password.\",\n"
            "    \"precondition\": \"User is on the login page.\",\n"
            "    \"status\": {\n"
            "      \"name\": \"Published\",\n"
            "      \"description\": \"The test is ready for execution\"\n"
            "    },\n"
            "    \"scriptType\": {\n"
            "      \"name\": \"Classic\",\n"
            "      \"description\": \"Steps represented in default representation - step, data and expected results\",\n"
            "      \"isEnabled\": true\n"
            "    },\n"
            "    \"steps\": [\n"
            "      {\n"
            "        \"step\": \"Enter valid email\",\n"
            "        \"data\": \"valid@email.com (Link: mailto:valid@email.com )\",\n"
            "        \"expectedResult\": \"Email is entered successfully\",\n"
            "        \"stepType\": \"TEXT\"\n"
            "      },\n"
            "      {\n"
            "        \"step\": \"Enter valid password\",\n"
            "        \"data\": \"valid_password123\",\n"
            "        \"expectedResult\": \"Password is entered successfully\",\n"
            "        \"stepType\": \"TEXT\"\n"
            "      },\n"
            "      {\n"
            "        \"step\": \"Click \\\"Login\\\"\",\n"
            "        \"expectedResult\": \"User is redirected to dashboard\",\n"
            "        \"stepType\": \"TEXT\"\n"
            "      }\n"
            "    ],\n"
            f"    \"jiraRequirementIDs\": [\"{story_id}\"]\n"
            "  }\n"
            "]\n\n"
            "Output only a valid JSON array of test cases, without any explanations or extra text. "
            "If the output does not fit, do not cut off in the middle—return only complete objects. "
            "If a field is missing, use an empty string (\"\") or an empty array as appropriate, instead of null or omitting the field."
        )
        return prompt
#-----------------------------------------------------------------------------------------------------------
    @staticmethod
    def send_prompt_to_openrouter(prompt: str, model: str, temperature: float, max_tokens: int) -> dict:
      url = settings.OPENROUTER_URL
      headers = {
          "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
          "Content-Type": "application/json"
      }
      data = {
          "model": model,  # Model dynamically passed
          "messages": [
              {"role": "system", "content": "You are an expert QA assistant."},
              {"role": "user", "content": prompt}
          ],
          "temperature": temperature,
          "max_tokens": max_tokens
      }
      response = requests.post(url, headers=headers, json=data)
      return response.json() if response.status_code == 200 else {"error": response.text}
    
    @staticmethod
    def safe_parse_test_cases(ai_content: str) -> List[Dict[str, str]]:
        """
        Safely parse test cases from AI response, handling incomplete or slightly invalid JSON.
        """
        if not ai_content or ai_content.strip() == "":
            logging.error("AI content is empty")
            return []

        # Use regex to extract the first JSON array from the response
        match = re.search(r'\[\s*{.*}\s*\]', ai_content, re.DOTALL)
        if not match:
            logging.error("No JSON array found in AI response")
            return []

        json_str = match.group(0)
        logging.info(f"Attempting to parse JSON of length: {len(json_str)}")

        def try_parse(s):
            try:
                return json.loads(s)
            except Exception as e:
                logging.error(f"JSON parse error: {e}")
                return None

        # First attempt
        test_cases = try_parse(json_str)
        if test_cases is None:
            # Try to auto-fix common issues: remove trailing commas before } or ]
            fixed = re.sub(r',(\s*[}\]])', r'\1', json_str)
            test_cases = try_parse(fixed)
            if test_cases is None:
                logging.error(f"Attempted to parse: {json_str[:500]}...")
                return []

        if not isinstance(test_cases, list):
            logging.error("AI response is not a list")
            return []

        # Normalize each test case to ensure all required fields exist
        normalized = []
        for i, tc in enumerate(test_cases):
            if not isinstance(tc, dict):
                logging.warning(f"Test case {i} is not a dictionary, skipping")
                continue

            try:
                steps = tc.get("steps", [])
                if not isinstance(steps, list):
                    steps = []

                # Properly structured steps
                structured_steps = [
                                    {
                                    "step": step.get("step", "").strip(),
                                    "data": step.get("data", "").strip(),
                                    "expectedResult": step.get("expectedResult", "").strip(),
                                    "stepType": "TEXT"
                                    }
                                    for step in steps
                                    if isinstance(step, dict)
                                    ]

                normalized_case = {
                    "title": str(tc.get("title") or "").strip(),
                    "description": str(tc.get("description") or "").strip(),
                    "precondition": str(tc.get("precondition") or "").strip(),
                    "status": {
                        "name": "Published",
                        "description": "The test is ready for execution"
                    },
                    "scriptType": {
                        "name": "Classic",
                        "description": "Steps represented in default representation - step, data and expected results",
                        "isEnabled": True
                    },
                    "steps": structured_steps,
                    "jiraRequirementIDs": tc.get("jiraRequirementIDs", []) if isinstance(tc.get("jiraRequirementIDs"), list) else [] 
                }

                # Skip test cases with empty title (required field)
                if not normalized_case["title"]:
                    logging.warning(f"Test case {i} has empty title, skipping")
                    continue

                normalized.append(normalized_case)
                logging.info(f"Successfully normalized test case {i}: {normalized_case['title']}")

            except Exception as e:
                logging.error(f"Error normalizing test case {i}: {e}")
                continue

        logging.info(f"Successfully normalized {len(normalized)} test cases out of {len(test_cases)}")
        return normalized

    def process_jira_story_and_send_to_openrouter(self, issue_key: str, model: str="meta-llama/llama-3-8b-instruct", temperature: float = 0.7, max_tokens: int = 666) -> dict:
        # Step 1: Fetch the Jira story using the key
        logging.info(f"Fetching Jira story for key: {issue_key}")
        jira_story = self.jira_service.get_user_story_by_key(issue_key)
        if not jira_story:
            logging.error(f"Jira story with key {issue_key} not found")
            return {"error": f"Jira story with key {issue_key} not found."}

        # Step 2: Extract story key, id, summary, and description
        story_key = jira_story.get("key", "")
        story_id = jira_story.get("id", "")
        story_summary = jira_story.get("fields", {}).get("summary", "")
        adf_description = jira_story.get("fields", {}).get("description", {})
        story_description = self.flatten_adf_description(adf_description)

        logging.info(f"Processing story: {story_id}, {story_key} - {story_summary}")
        logging.info(f"Description length: {len(story_description)} characters")

        # Step 3: Create the initial prompt
        prompt = self.create_test_case_prompt(story_key, story_id, story_summary, story_description)
        logging.info(f"Generated prompt length: {len(prompt)} characters")

        # Step 4: Send request to OpenRouter API
        logging.info(f"Sending request to OpenRouter with model: {model}, temperature: {temperature}, max_tokens: {max_tokens}")
        response = self.send_prompt_to_openrouter(prompt, model, temperature, max_tokens)

        if "error" in response:
            logging.error(f"Error from OpenRouter: {response['error']}")
            return {"error": response["error"]}

        ai_message_content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not ai_message_content:
            logging.error("No content returned from OpenRouter.")
            return {"error": "No content returned from OpenRouter."}

        logging.info("Received response from OpenRouter. Attempting to parse test cases.")
        test_cases = self.safe_parse_test_cases(ai_message_content)

        if not test_cases:
            logging.warning("No valid test cases parsed from OpenRouter response.")
            return {"error": "Failed to parse test cases from OpenRouter response."}

        logging.info(f"Returning {len(test_cases)} test cases.")
        return {
            "test_cases": test_cases,
            "raw_response": ai_message_content
        }

    def generate_and_normalize_test_cases(self, issue_key: str, model: str="meta-llama/llama-3-8b-instruct", temperature: float = 0.7, max_tokens: int = 666) -> List[Dict[str, str]]:
        """
        Complete method to generate and normalize test cases for a Jira story.
        Returns normalized test cases ready for database storage.
        """
        try:
            # Get AI response and parsed test cases
            logging.info(f"Starting test case generation for story: {issue_key}")
            result = self.process_jira_story_and_send_to_openrouter(issue_key, model, temperature, max_tokens)

            if "error" in result:
                logging.error(f"Error in AI response: {result['error']}")
                return []

            test_cases = result.get("test_cases", [])
            logging.info(f"Final result: {len(test_cases)} normalized test cases")
            return test_cases

        except Exception as e:
            logging.error(f"Error generating test cases for story {issue_key}: {e}")
            return []

