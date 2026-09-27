from typing import List

class Classroom:
    def __init__(self, id: int, name: str, teacher_id: int):
        self.id = id
        self.name = name
        self.teacher_id = teacher_id
        self.students: List[str] = [] # List of github usernames
