from typing import Optional
from core.ports.user_repository import UserRepository
from core.ports.github_client import GithubClient

class AuthUseCases:
    def __init__(self, user_repo: UserRepository, github_client: GithubClient = None):
        self.user_repo = user_repo
        self.github_client = github_client

    def login(self, username: str, password: str) -> Optional[int]:
        return self.user_repo.authenticate_user(username, password)

    def register(self, username: str, password: str) -> Optional[int]:
        return self.user_repo.create_user(username, password)

    def get_github_token(self, user_id: int) -> Optional[str]:
        return self.user_repo.get_github_token(user_id)

    def save_github_token(self, user_id: int, token: Optional[str]) -> None:
        self.user_repo.save_github_token(user_id, token)

    def handle_github_oauth_callback(self, client_id: str, client_secret: str, code: str, user_id: int) -> str:
        if not self.github_client:
            return "ERROR:No github client"
        token = self.github_client.exchange_code_for_token(client_id, client_secret, code)
        if token and not token.startswith("ERROR:"):
            self.save_github_token(user_id, token)
            return "SUCCESS"
        return token if token else "ERROR:Unknown"
