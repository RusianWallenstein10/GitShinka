from typing import List, Optional, Dict, Any
from core.ports.classroom_repository import ClassroomRepository
from core.ports.github_client import GithubClient
from core.entities.classroom import Classroom

class ClassroomUseCases:
    def __init__(self, classroom_repo: ClassroomRepository, github_client: GithubClient):
        self.classroom_repo = classroom_repo
        self.github_client = github_client

    def create_classroom(self, name: str, teacher_id: int) -> Optional[int]:
        return self.classroom_repo.create_classroom(name, teacher_id)

    def get_classrooms_by_teacher(self, teacher_id: int) -> List[Classroom]:
        return self.classroom_repo.get_classrooms_by_teacher(teacher_id)

    def get_classroom_by_id(self, classroom_id: int) -> Optional[Classroom]:
        return self.classroom_repo.get_classroom_by_id(classroom_id)

    def add_student_to_classroom(self, classroom_id: int, github_username: str) -> bool:
        return self.classroom_repo.add_student_to_classroom(classroom_id, github_username)

    def get_classroom_metrics(self, classroom_id: int, teacher_token: str) -> Dict[str, Any]:
        """
        Orchestrates calls to GitHub API to get metrics for all students in the classroom
        using the teacher's token (or an admin token).
        """
        classroom = self.get_classroom_by_id(classroom_id)
        if not classroom:
            return {"error": "Classroom not found"}

        students_metrics = []
        for username in classroom.students:
            # We fetch user repos for each student. 
            # Note: For a real GitHub Classroom scale, this should be paginated or async.
            try:
                # The github client needs a method to fetch repos for a specific username
                # Currently get_summary_metrics uses the authenticated user's repos.
                # We will add a get_user_repos method to the client.
                repos = self.github_client.get_user_repos(username, teacher_token)
                
                # Calculate some basic metrics
                total_stars = sum(r.get("stargazers_count", 0) for r in repos)
                recent_repos = sorted(repos, key=lambda x: x.get("pushed_at", ""), reverse=True)[:3]
                
                students_metrics.append({
                    "username": username,
                    "total_repos": len(repos),
                    "total_stars": total_stars,
                    "recent_repos": [
                        {
                            "name": r.get("name"), 
                            "updated_at": r.get("pushed_at"),
                            "url": r.get("html_url")
                        } 
                        for r in recent_repos
                    ]
                })
            except Exception as e:
                students_metrics.append({
                    "username": username,
                    "error": str(e)
                })

        return {
            "classroom_name": classroom.name,
            "students_metrics": students_metrics
        }
