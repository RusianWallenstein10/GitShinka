from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class GithubClient(ABC):
    @abstractmethod
    def get_summary_metrics(self, token: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_other_user_metrics(self, token: str, username: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_repo_details(self, token: str, username: str, repo_name: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def search_github(self, token: str, query: str, search_type: str = "users") -> Dict[str, Any]:
        pass

    @abstractmethod
    def exchange_code_for_token(self, client_id: str, client_secret: str, code: str) -> Optional[str]:
        pass

    @abstractmethod
    def get_user_repos(self, username: str, token: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def create_issue(self, owner: str, repo: str, title: str, body: str, token: str) -> Dict[str, Any]:
        pass
