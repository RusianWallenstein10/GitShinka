from typing import List, Dict, Any
from core.ports.classroom_repository import ClassroomRepository
from core.ports.github_client import GithubClient

class AutomationUseCases:
    def __init__(self, classroom_repo: ClassroomRepository, github_client: GithubClient):
        self.classroom_repo = classroom_repo
        self.github_client = github_client

    def dispatch_issue_to_classroom(
        self, classroom_id: int, target_repo_name: str, title: str, body: str, teacher_token: str
    ) -> Dict[str, Any]:
        """
        Dispatches an issue to a specific repository name for every student in the classroom.
        Returns a summary of successes and failures.
        """
        classroom = self.classroom_repo.get_classroom_by_id(classroom_id)
        if not classroom:
            return {"error": "Classroom no encontrado"}

        results = {
            "total_attempted": len(classroom.students),
            "successes": [],
            "failures": []
        }

        for username in classroom.students:
            # We assume the student repository is owned by the student or the teacher.
            # In standard GitHub classroom, repos might be named `assignment-username` under a Teacher Org.
            # Here, we'll try to create it in the student's namespace: `username/target_repo_name`.
            # NOTE: The teacher's token MUST have permission to write to this repository.
            res = self.github_client.create_issue(
                owner=username,
                repo=target_repo_name,
                title=title,
                body=body,
                token=teacher_token
            )

            if "error" in res:
                results["failures"].append({
                    "username": username,
                    "repo": target_repo_name,
                    "error": res["error"]
                })
            else:
                results["successes"].append({
                    "username": username,
                    "repo": target_repo_name,
                    "issue_url": res.get("html_url")
                })

        return results
