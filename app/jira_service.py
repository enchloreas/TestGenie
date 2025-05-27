# app/jira_service.py

import requests
from requests.auth import HTTPBasicAuth
from typing import List, Dict
from app.config import JIRA_DOMAIN, JIRA_EMAIL, JIRA_API_TOKEN

def get_all_user_stories(project_key: str, issue_type: str) -> List[Dict]:
    print("get_all_user_stories function called") 
    url = f"{JIRA_DOMAIN}/rest/api/3/search"
    jql = f"project={project_key} AND issuetype={issue_type}"  # Adjust JQL as needed
    headers = {"Accept": "application/json"}
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    params = {
        "jql": jql,
        "fields": "summary,description,status"
    }
    # Debugging: Log the request details
    print(f"Request URL: {url}")
    print(f"Request Headers: {headers}")
    print(f"Request Params: {params}")
    print(f"Request Auth: {JIRA_EMAIL}, [API_TOKEN_HIDDEN]")

    response = requests.get(url, headers=headers, auth=auth, params=params)
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
