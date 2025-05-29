# app/jira_service.py

import requests
from requests.auth import HTTPBasicAuth
from typing import List, Dict

class JiraService:
    def __init__(self, domain: str, email: str, api_token: str):
        """
        Initialize JiraService with connection configuration.
        :param domain: Jira domain, e.g. 'https://yourcompany.atlassian.net'
        :param email: Jira user email
        :param api_token: API token for authentication
        """
        self.domain = domain
        self.email = email
        self.api_token = api_token
        self.auth = HTTPBasicAuth(email, api_token)
        self.headers = {"Accept": "application/json"}
        print(f"JiraService initialized for {domain} with user {email}")

    def get_all_user_stories(self, project_key: str, issue_type: str) -> List[Dict]:
        """
        Retrieve all issues of the specified type in the project.
        :param project_key: Jira project key, e.g. 'TG'
        :param issue_type: Issue type, e.g. 'Story'
        :return: List of dictionaries containing issue key, summary, description, and status
        """
        print("get_all_user_stories method called")
        url = f"{self.domain}/rest/api/3/search"
        jql = f"project={project_key} AND issuetype={issue_type}"
        params = {
            "jql": jql,
            "fields": "summary,description,status"
        }

        print(f"Request URL: {url}")
        print(f"Request Params: {params}")

        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        if response.status_code == 200:
            issues = response.json()["issues"]
            return [
                {
                    "key": issue["key"],
                    "summary": issue["fields"]["summary"],
                    "description": issue["fields"]["description"],
                    "status": issue["fields"]["status"]["name"]
                }
                for issue in issues
            ]
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []

    def get_user_story_by_key(self, issue_key: str) -> Dict:
        """
        Retrieve issue details by key.
        :param issue_key: Jira issue key, e.g. 'TG-1'
        :return: Dictionary containing issue data
        """
        print(f"get_user_story_by_key method called with {issue_key}")
        url = f"{self.domain}/rest/api/3/issue/{issue_key}"
        params = {
            "fields": "summary,description,status"
        }

        print(f"Request URL: {url}")
        print(f"Request Params: {params}")

        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        if response.status_code == 200:
            issue = response.json()
            return {
                "key": issue["key"],
                "summary": issue["fields"]["summary"],
                "description": issue["fields"]["description"],
                "status": issue["fields"]["status"]["name"]
            }
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return {}
   