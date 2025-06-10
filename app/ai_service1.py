# app/ai_service.py

import requests
import json
import logging
from typing import List, Dict
from .config import settings
from .jira_service import JiraService

# Configure logging
logging.basicConfig(level=logging.INFO)

class AIService:
    def __init__(
        self,
        jira_domain: str,
        jira_email: str,
        jira_api_token: str,
        openrouter_url: str,
        openrouter_api_key: str
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
    
    @staticmethod
    def create_test_case_prompt(story_key: str, summary: str, description: str) -> str:
      """
      Create a prompt for OpenRouter AI to generate multiple structured test cases.
      :param story_key: Jira story key, e.g. 'TG-1'
      :param summary: Story summary
      :param description: Flattened story description
      :return: Prompt string
      """
      # Compose the instruction prompt
      prompt = (
            f"You are a professional QA engineer.\n"
            f"Based on the following Jira story, generate as many relevant test cases as needed.\n\n"
            f"Jira Key: {story_key}\n"
            f"Summary: {summary}\n"
            f"Description: {description}\n\n"
            "Each test case must be a JSON object with the following fields:\n"
            "- title (string)\n"
            "- preconditions (string)\n"
            "- steps (array of strings)\n"
            "- expected_results (string)\n"
            "- postconditions (string)\n\n"
            "Example:\n"
            "[\n"
            "  {\n"
            "    \"title\": \"Update user profile name\",\n"
            "    \"preconditions\": \"User is logged in and on the profile page\",\n"
            "    \"steps\": [\"Click edit\", \"Enter new name\", \"Click save\"],\n"
            "    \"expected_results\": \"The new name is saved and displayed on the profile page\",\n"
            "    \"postconditions\": \"User sees the updated name on their profile\"\n"
            "  }\n"
            "]\n\n"
            "Output only a valid JSON array of test cases, without any explanations or extra text. "
            "If the output does not fit, do not cut off in the middle—return only complete objects. "
            "If a field is missing, use an empty string (\"\") instead of null or omitting the field."
      )
      return prompt

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
        Safely parse test cases from AI response, handling incomplete JSON.
        """
        if not ai_content or ai_content.strip() == "":
            logging.error("AI content is empty")
            return []

        # Trim the string to the last closing bracket of the array
        last_bracket = ai_content.rfind(']')
        if last_bracket == -1:
            logging.error("No closing bracket found in AI response")
            return []

        json_str = ai_content[:last_bracket+1]
        logging.info(f"Attempting to parse JSON of length: {len(json_str)}")

        try:
            test_cases = json.loads(json_str)
            if not isinstance(test_cases, list):
                logging.error("AI response is not a list")
                return []
        except Exception as e:
            logging.error(f"JSON parse error: {e}")
            logging.error(f"Attempted to parse: {json_str[:200]}...")
            return []

        # Normalize each test case to ensure all required fields exist
        normalized = []
        for i, tc in enumerate(test_cases):
            if not isinstance(tc, dict):
                logging.warning(f"Test case {i} is not a dictionary, skipping")
                continue

            try:
                # Convert steps to string if it's a list
                steps = tc.get("steps", [])
                if isinstance(steps, list):
                    steps_str = "; ".join(str(step) for step in steps if step)
                else:
                    steps_str = str(steps) if steps else ""

                # Normalize all fields to strings
                normalized_case = {
                    "title": str(tc.get("title") or "").strip(),
                    "preconditions": str(tc.get("preconditions") or "").strip(),
                    "steps": steps_str.strip(),
                    "expected_results": str(tc.get("expected_results") or "").strip(),
                    "postconditions": str(tc.get("postconditions") or "").strip(),
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

    def process_jira_story_and_send_to_openrouter(self, issue_key: str, model: str="gpt-4", temperature: float = 0.7, max_tokens: int = 666) -> dict:
        # Step 1: Fetch the Jira story using the key
        logging.info(f"Fetching Jira story for key: {issue_key}")
        jira_story = self.jira_service.get_user_story_by_key(issue_key)
        if not jira_story:
            logging.error(f"Jira story with key {issue_key} not found")
            return {"error": f"Jira story with key {issue_key} not found."}

        # Step 2: Extract story key, summary, and description
        story_key = jira_story.get("key", "")
        story_summary = jira_story.get("fields", {}).get("summary", "")
        adf_description = jira_story.get("fields", {}).get("description", {})
        story_description = self.flatten_adf_description(adf_description)

        logging.info(f"Processing story: {story_key} - {story_summary}")
        logging.info(f"Description length: {len(story_description)} characters")

        # Step 3: Create the initial prompt
        prompt = self.create_test_case_prompt(story_key, story_summary, story_description)
        logging.info(f"Generated prompt length: {len(prompt)} characters")

        # Step 4: Send request to OpenRouter API
        logging.info(f"Sending request to OpenRouter with model: {model}, temperature: {temperature}, max_tokens: {max_tokens}")
        response = self.send_prompt_to_openrouter(prompt, model, temperature, max_tokens)

        if "error" in response:
            logging.error(f"OpenRouter API error: {response['error']}")
        else:
            logging.info("Successfully received response from OpenRouter")

        return response

    def generate_and_normalize_test_cases(self, issue_key: str, model: str="meta-llama/llama-3-8b-instruct", temperature: float = 0.7, max_tokens: int = 666) -> List[Dict[str, str]]:
        """
        Complete method to generate and normalize test cases for a Jira story.
        Returns normalized test cases ready for database storage.
        """
        try:
            # Get raw AI response
            logging.info(f"Starting test case generation for story: {issue_key}")
            raw_response = self.process_jira_story_and_send_to_openrouter(issue_key, model, temperature, max_tokens)

            # Check for errors in response
            if "error" in raw_response:
                logging.error(f"Error in AI response: {raw_response['error']}")
                return []

            # Check if response contains choices
            if "choices" not in raw_response or not raw_response["choices"]:
                logging.error(f"AI service error or unexpected response structure: {raw_response}")
                return []

            # Extract content from AI response
            content = raw_response["choices"][0]["message"]["content"]
            logging.info(f"AI response content length: {len(content) if content else 0} characters")

            if not content or content.strip() == "":
                logging.error("AI returned empty content")
                return []

            # Parse and normalize test cases
            normalized_test_cases = self.safe_parse_test_cases(content)
            logging.info(f"Final result: {len(normalized_test_cases)} normalized test cases")

            return normalized_test_cases

        except Exception as e:
            logging.error(f"Error generating test cases for story {issue_key}: {e}")
            return []