from __future__ import annotations

from typing import Any

from app.db.connection import Database


class SystemDAO:
    def __init__(self, database: Database):
        self.db = database

    def get_admin_by_username(self, username: str) -> dict[str, Any] | None:
        return self.db.query_one(
            """
            SELECT id, username, password_hash, full_name
            FROM admin_user
            WHERE username=%s
            """,
            (username,),
        )

    def get_student_by_student_no(self, student_no: str) -> dict[str, Any] | None:
        return self.db.query_one(
            """
            SELECT s.id, s.student_no, s.password_hash, s.name, s.gender, s.phone, s.email,
                   s.enrollment_year, s.status, m.name AS major_name, c.name AS class_name,
                   s.major_id, s.class_id
            FROM student s
            JOIN major m ON s.major_id = m.id
            JOIN class c ON s.class_id = c.id
            WHERE s.student_no=%s
            """,
            (student_no,),
        )

    def get_dashboard_stats(self) -> dict[str, int]:
        return {
            "student_count": self.db.query_one("SELECT COUNT(*) AS value FROM student")["value"],
            "course_count": self.db.query_one("SELECT COUNT(*) AS value FROM course")["value"],
            "selection_count": self.db.query_one("SELECT COUNT(*) AS value FROM course_selection")["value"],
            "attachment_count": self.db.query_one("SELECT COUNT(*) AS value FROM student_attachment")["value"],
        }

    def list_majors(self) -> list[dict[str, Any]]:
        return self.db.query_all("SELECT id, name, description FROM major ORDER BY id")

    def list_classes(self) -> list[dict[str, Any]]:
        return self.db.query_all(
            """
            SELECT c.id, c.name, c.grade_year, m.name AS major_name, c.major_id
            FROM class c
            JOIN major m ON c.major_id = m.id
            ORDER BY c.id
            """
        )

    def list_students(self, keyword: str = "") -> list[dict[str, Any]]:
        keyword_pattern = f"%{keyword}%"
        return self.db.query_all(
            """
            SELECT s.id, s.student_no, s.name, s.gender, s.phone, s.email, s.enrollment_year,
                   s.status, m.name AS major_name, c.name AS class_name, s.major_id, s.class_id
            FROM student s
            JOIN major m ON s.major_id = m.id
            JOIN class c ON s.class_id = c.id
            WHERE s.student_no LIKE %s OR s.name LIKE %s
            ORDER BY s.student_no
            """,
            (keyword_pattern, keyword_pattern),
        )

    def create_student(self, payload: dict[str, Any]) -> None:
        self.db.execute(
            """
            CALL sp_upsert_student_profile(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                payload["student_no"],
                payload["password"],
                payload["name"],
                payload["gender"],
                payload["phone"],
                payload["email"],
                payload["enrollment_year"],
                payload["status"],
                payload["major_id"],
                payload["class_id"],
            ),
        )

    def update_student(self, student_id: int, payload: dict[str, Any]) -> None:
        student_no = self.db.query_one("SELECT student_no FROM student WHERE id=%s", (student_id,))
        if not student_no:
            raise ValueError("学生不存在。")
        self.db.execute(
            """
            CALL sp_upsert_student_profile(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                student_no["student_no"],
                payload.get("password", ""),
                payload["name"],
                payload["gender"],
                payload["phone"],
                payload["email"],
                payload["enrollment_year"],
                payload["status"],
                payload["major_id"],
                payload["class_id"],
            ),
        )

    def delete_student(self, student_id: int) -> None:
        self.db.execute("DELETE FROM student WHERE id=%s", (student_id,))

    def list_courses(self) -> list[dict[str, Any]]:
        return self.db.query_all(
            """
            SELECT id, course_code, name, credit, hours, semester
            FROM course
            ORDER BY course_code
            """
        )

    def create_course(self, payload: dict[str, Any]) -> None:
        self.db.execute(
            """
            INSERT INTO course (course_code, name, credit, hours, semester)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                payload["course_code"],
                payload["name"],
                payload["credit"],
                payload["hours"],
                payload["semester"],
            ),
        )

    def update_course(self, course_id: int, payload: dict[str, Any]) -> None:
        self.db.execute(
            """
            UPDATE course
            SET course_code=%s, name=%s, credit=%s, hours=%s, semester=%s
            WHERE id=%s
            """,
            (
                payload["course_code"],
                payload["name"],
                payload["credit"],
                payload["hours"],
                payload["semester"],
                course_id,
            ),
        )

    def delete_course(self, course_id: int) -> None:
        self.db.execute("DELETE FROM course WHERE id=%s", (course_id,))

    def list_course_selections(self) -> list[dict[str, Any]]:
        return self.db.query_all(
            """
            SELECT cs.id, s.student_no, s.name AS student_name, c.course_code, c.name AS course_name,
                   cs.selection_date, sc.usual_score, sc.final_score, sc.total_score, sc.grade_level
            FROM course_selection cs
            JOIN student s ON cs.student_id = s.id
            JOIN course c ON cs.course_id = c.id
            LEFT JOIN score sc ON sc.selection_id = cs.id
            ORDER BY cs.id DESC
            """
        )

    def create_selection(self, student_id: int, course_id: int) -> None:
        self.db.execute(
            """
            INSERT INTO course_selection (student_id, course_id, selection_date)
            VALUES (%s, %s, CURRENT_DATE())
            """,
            (student_id, course_id),
        )

    def save_score(self, selection_id: int, usual_score: float, final_score: float) -> None:
        self.db.execute(
            """
            INSERT INTO score (selection_id, usual_score, final_score, total_score, grade_level)
            VALUES (%s, %s, %s, fn_calculate_total_score(%s, %s), fn_score_to_level(fn_calculate_total_score(%s, %s)))
            ON DUPLICATE KEY UPDATE
              usual_score=VALUES(usual_score),
              final_score=VALUES(final_score),
              total_score=VALUES(total_score),
              grade_level=VALUES(grade_level)
            """,
            (selection_id, usual_score, final_score, usual_score, final_score, usual_score, final_score),
        )

    def list_rewards(self) -> list[dict[str, Any]]:
        return self.db.query_all(
            """
            SELECT rp.id, s.student_no, s.name AS student_name, rp.record_type, rp.title, rp.description, rp.record_date
            FROM reward_punishment rp
            JOIN student s ON rp.student_id = s.id
            ORDER BY rp.record_date DESC, rp.id DESC
            """
        )

    def create_reward(self, payload: dict[str, Any]) -> None:
        self.db.execute(
            """
            INSERT INTO reward_punishment (student_id, record_type, title, description, record_date)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                payload["student_id"],
                payload["record_type"],
                payload["title"],
                payload["description"],
                payload["record_date"],
            ),
        )

    def delete_reward(self, reward_id: int) -> None:
        self.db.execute("DELETE FROM reward_punishment WHERE id=%s", (reward_id,))

    def list_status_changes(self) -> list[dict[str, Any]]:
        return self.db.query_all(
            """
            SELECT ssc.id, s.student_no, s.name AS student_name, ssc.change_type, ssc.old_value,
                   ssc.new_value, ssc.change_reason, ssc.change_date
            FROM student_status_change ssc
            JOIN student s ON ssc.student_id = s.id
            ORDER BY ssc.change_date DESC, ssc.id DESC
            """
        )

    def add_status_change(self, payload: dict[str, Any]) -> None:
        def operations(connection):
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO student_status_change
                    (student_id, change_type, old_value, new_value, change_reason, change_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        payload["student_id"],
                        payload["change_type"],
                        payload["old_value"],
                        payload["new_value"],
                        payload["change_reason"],
                        payload["change_date"],
                    ),
                )
                if payload["change_type"] == "专业变更":
                    cursor.execute(
                        "UPDATE student SET major_id=%s WHERE id=%s",
                        (payload["new_ref_id"], payload["student_id"]),
                    )
                elif payload["change_type"] == "班级变更":
                    cursor.execute(
                        "UPDATE student SET class_id=%s WHERE id=%s",
                        (payload["new_ref_id"], payload["student_id"]),
                    )
                elif payload["change_type"] == "状态变更":
                    cursor.execute(
                        "UPDATE student SET status=%s WHERE id=%s",
                        (payload["new_value"], payload["student_id"]),
                    )

        self.db.execute_transaction(operations)

    def list_attachments(self) -> list[dict[str, Any]]:
        return self.db.query_all(
            """
            SELECT sa.id, s.student_no, s.name AS student_name, sa.file_name, sa.file_type,
                   sa.file_path, sa.description, sa.uploaded_at
            FROM student_attachment sa
            JOIN student s ON sa.student_id = s.id
            ORDER BY sa.uploaded_at DESC, sa.id DESC
            """
        )

    def create_attachment(self, payload: dict[str, Any]) -> None:
        self.db.execute(
            """
            INSERT INTO student_attachment (student_id, file_name, file_type, file_path, description, uploaded_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            """,
            (
                payload["student_id"],
                payload["file_name"],
                payload["file_type"],
                payload["file_path"],
                payload["description"],
            ),
        )

    def delete_attachment(self, attachment_id: int) -> None:
        self.db.execute("DELETE FROM student_attachment WHERE id=%s", (attachment_id,))

    def list_student_courses(self, student_id: int) -> list[dict[str, Any]]:
        return self.db.query_all(
            """
            SELECT c.course_code, c.name AS course_name, c.credit, c.hours, c.semester,
                   sc.usual_score, sc.final_score, sc.total_score, sc.grade_level
            FROM course_selection cs
            JOIN course c ON cs.course_id = c.id
            LEFT JOIN score sc ON sc.selection_id = cs.id
            WHERE cs.student_id=%s
            ORDER BY c.semester, c.course_code
            """,
            (student_id,),
        )

    def list_student_rewards(self, student_id: int) -> list[dict[str, Any]]:
        return self.db.query_all(
            """
            SELECT record_type, title, description, record_date
            FROM reward_punishment
            WHERE student_id=%s
            ORDER BY record_date DESC
            """,
            (student_id,),
        )

    def list_student_status_changes(self, student_id: int) -> list[dict[str, Any]]:
        return self.db.query_all(
            """
            SELECT change_type, old_value, new_value, change_reason, change_date
            FROM student_status_change
            WHERE student_id=%s
            ORDER BY change_date DESC
            """,
            (student_id,),
        )

    def list_student_attachments(self, student_id: int) -> list[dict[str, Any]]:
        return self.db.query_all(
            """
            SELECT file_name, file_type, file_path, description, uploaded_at
            FROM student_attachment
            WHERE student_id=%s
            ORDER BY uploaded_at DESC
            """,
            (student_id,),
        )
