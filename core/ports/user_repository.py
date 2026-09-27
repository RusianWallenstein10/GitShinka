from abc import ABC, abstractmethod
from typing import Optional

class UserRepository(ABC):
    @abstractmethod
    def authenticate_user(self, username: str, password: str) -> Optional[int]:
        pass

    @abstractmethod
    def create_user(self, username: str, password: str) -> Optional[int]:
        pass

    @abstractmethod
    def save_github_token(self, user_id: int, token: Optional[str]) -> None:
        pass

    @abstractmethod
    def get_github_token(self, user_id: int) -> Optional[str]:
        pass
