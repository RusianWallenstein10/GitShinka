from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    username: str
    github_token: Optional[str] = None
