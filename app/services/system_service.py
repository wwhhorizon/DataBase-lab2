from __future__ import annotations

from pathlib import Path
import shutil

from app.config.settings import Settings
from app.dao.system_dao import SystemDAO
from app.db.connection import Database
from app.utils.score import classify_file_type


class SystemService:
    def __init__(self, database: Database, settings: Settings):
        self.dao = SystemDAO(database)
        self.settings = settings
        self.attachment_root = Path(settings.storage.attachment_root)
        self.attachment_root.mkdir(parents=True, exist_ok=True)

    def get_dashboard_stats(self):
        return self.dao.get_dashboard_stats()

    def list_students(self, keyword: str = ""):
        return self.dao.list_students(keyword)

    def list_majors(self):
        return self.dao.list_majors()

    def list_classes(self):
        return self.dao.list_classes()

    def create_student(self, payload):
        self.dao.create_student(payload)

    def update_student(self, student_id: int, payload):
        self.dao.update_student(student_id, payload)

    def delete_student(self, student_id: int):
        self.dao.delete_student(student_id)

    def list_courses(self):
        return self.dao.list_courses()

    def create_course(self, payload):
        self.dao.create_course(payload)

    def update_course(self, course_id: int, payload):
        self.dao.update_course(course_id, payload)

    def delete_course(self, course_id: int):
        self.dao.delete_course(course_id)

    def list_course_selections(self):
        return self.dao.list_course_selections()

    def create_selection(self, student_id: int, course_id: int):
        self.dao.create_selection(student_id, course_id)

    def save_score(self, selection_id: int, usual_score: float, final_score: float):
        self.dao.save_score(selection_id, usual_score, final_score)

    def list_rewards(self):
        return self.dao.list_rewards()

    def create_reward(self, payload):
        self.dao.create_reward(payload)

    def delete_reward(self, reward_id: int):
        self.dao.delete_reward(reward_id)

    def list_status_changes(self):
        return self.dao.list_status_changes()

    def add_status_change(self, payload):
        self.dao.add_status_change(payload)

    def list_attachments(self):
        return self.dao.list_attachments()

    def add_attachment(self, student_id: int, source_file: str, description: str):
        source_path = Path(source_file)
        file_type = classify_file_type(source_path.suffix)
        target_dir = self.attachment_root / str(student_id)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / source_path.name
        shutil.copy2(source_path, target_path)
        self.dao.create_attachment(
            {
                "student_id": student_id,
                "file_name": source_path.name,
                "file_type": file_type,
                "file_path": str(target_path),
                "description": description,
            }
        )

    def delete_attachment(self, attachment_id: int, file_path: str):
        path = Path(file_path)
        if path.exists():
            path.unlink()
        self.dao.delete_attachment(attachment_id)

    def list_student_courses(self, student_id: int):
        return self.dao.list_student_courses(student_id)

    def get_student_profile(self, student_no: str):
        return self.dao.get_student_by_student_no(student_no)

    def list_student_rewards(self, student_id: int):
        return self.dao.list_student_rewards(student_id)

    def list_student_status_changes(self, student_id: int):
        return self.dao.list_student_status_changes(student_id)

    def list_student_attachments(self, student_id: int):
        return self.dao.list_student_attachments(student_id)
