from __future__ import annotations

import hashlib

from app.dao.system_dao import SystemDAO
from app.db.connection import Database
from app.models.entities import LoginUser


class AuthService:
    def __init__(self, database: Database):
        self.dao = SystemDAO(database)

    def login(self, role: str, username: str, password: str) -> LoginUser:
        hashed = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if role == "管理员":
            record = self.dao.get_admin_by_username(username)
            if not record or record["password_hash"] != hashed:
                raise ValueError("管理员账号或密码错误。")
            return LoginUser("管理员", record["id"], record["username"], record["full_name"])

        record = self.dao.get_student_by_student_no(username)
        if not record or record["password_hash"] != hashed:
            raise ValueError("学生账号或密码错误。")
        return LoginUser("学生", record["id"], record["student_no"], record["name"])
