import sqlite3
from typing import List, Optional
from core.ports.classroom_repository import ClassroomRepository
from core.entities.classroom import Classroom

class SqliteClassroomRepository(ClassroomRepository):
    def __init__(self, db_path: str = "gitshinka.db"):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def create_classroom(self, name: str, teacher_id: int) -> Optional[int]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO classrooms (name, teacher_id) VALUES (?, ?)", (name, teacher_id))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error creating classroom: {e}")
            return None

    def get_classrooms_by_teacher(self, teacher_id: int) -> List[Classroom]:
        classrooms = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, teacher_id FROM classrooms WHERE teacher_id = ?", (teacher_id,))
                rows = cursor.fetchall()
                for row in rows:
                    classrooms.append(Classroom(id=row[0], name=row[1], teacher_id=row[2]))
        except Exception as e:
            print(f"Error fetching classrooms: {e}")
        return classrooms

    def get_classroom_by_id(self, classroom_id: int) -> Optional[Classroom]:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, teacher_id FROM classrooms WHERE id = ?", (classroom_id,))
                row = cursor.fetchone()
                if row:
                    classroom = Classroom(id=row[0], name=row[1], teacher_id=row[2])
                    classroom.students = self.get_students_in_classroom(classroom_id)
                    return classroom
        except Exception as e:
            print(f"Error fetching classroom: {e}")
        return None

    def add_student_to_classroom(self, classroom_id: int, github_username: str) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO classroom_students (classroom_id, github_username) VALUES (?, ?)", 
                    (classroom_id, github_username)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # Student might already be added
            return False
        except Exception as e:
            print(f"Error adding student: {e}")
            return False

    def get_students_in_classroom(self, classroom_id: int) -> List[str]:
        students = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT github_username FROM classroom_students WHERE classroom_id = ?", (classroom_id,))
                rows = cursor.fetchall()
                for row in rows:
                    students.append(row[0])
        except Exception as e:
            print(f"Error fetching students: {e}")
        return students
