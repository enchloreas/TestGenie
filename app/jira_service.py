# app/jira_service.py

import requests
from requests.auth import HTTPBasicAuth
from typing import List, Dict
from app.config import JIRA_DOMAIN, JIRA_PROJECT_KEY, JIRA_EMAIL, JIRA_API_TOKEN

def get_user_stories() -> List[Dict]:
    print("get_user_stories function called") 
    url = f"{JIRA_DOMAIN}/rest/api/3/search"
    jql = f"project={JIRA_PROJECT_KEY} AND issuetype=Story"  # Adjust JQL as needed
    headers = {"Accept": "application/json"}
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    params = {
        "jql": jql,
        "fields": "summary,description"
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
                "description": issue["fields"]["description"]
            }
            for issue in issues
        ]
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []
