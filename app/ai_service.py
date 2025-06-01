# app/ai_service.py

import requests
import json
from .config import settings
from .jira_service import JiraService

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
          "Each test case should include:\n"
          "- Title\n"
          "- Preconditions\n"
          "- Steps\n"
          "- Expected results\n"
          "- Postconditions\n\n"
          "Output the results in JSON format as a list of test cases.\n"
          "Return only the JSON, without any explanations or extra text."
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

    def process_jira_story_and_send_to_openrouter(self, issue_key: str, model: str="gpt-4", temperature: float = 0.7, max_tokens: int = 666) -> dict:
        # Step 1: Fetch the Jira story using the key
        jira_story = self.jira_service.get_user_story_by_key(issue_key)
        if not jira_story:
            return {"error": f"Jira story with key {issue_key} not found."}

        # Step 2: Extract story key, summary, and description
        story_key = jira_story.get("key", "")
        story_summary = jira_story.get("fields", {}).get("summary", "")
        adf_description = jira_story.get("fields", {}).get("description", {})
        story_description = self.flatten_adf_description(adf_description)

        # Step 3: Create the initial prompt
        prompt = self.create_test_case_prompt(story_key, story_summary, story_description)

        # Step 4: Send request to OpenRouter API
        response = self.send_prompt_to_openrouter(prompt, model, temperature, max_tokens)

        return response