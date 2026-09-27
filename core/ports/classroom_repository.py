from abc import ABC, abstractmethod
from typing import List, Optional
from core.entities.classroom import Classroom

class ClassroomRepository(ABC):
    @abstractmethod
    def create_classroom(self, name: str, teacher_id: int) -> Optional[int]:
        pass

    @abstractmethod
    def get_classrooms_by_teacher(self, teacher_id: int) -> List[Classroom]:
        pass

    @abstractmethod
    def get_classroom_by_id(self, classroom_id: int) -> Optional[Classroom]:
        pass

    @abstractmethod
    def add_student_to_classroom(self, classroom_id: int, github_username: str) -> bool:
        pass

    @abstractmethod
    def get_students_in_classroom(self, classroom_id: int) -> List[str]:
        pass
