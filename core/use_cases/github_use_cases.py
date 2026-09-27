from typing import Dict, Any
from core.ports.github_client import GithubClient

class GithubUseCases:
    def __init__(self, github_client: GithubClient):
        self.github_client = github_client

    def get_dashboard_summary(self, token: str) -> Dict[str, Any]:
        return self.github_client.get_summary_metrics(token)
    
    def search(self, token: str, query: str, search_type: str = "users") -> Dict[str, Any]:
        return self.github_client.search_github(token, query, search_type)

    def get_repo_details(self, token: str, username: str, repo_name: str) -> Dict[str, Any]:
        return self.github_client.get_repo_details(token, username, repo_name)
