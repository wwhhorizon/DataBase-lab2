from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LoginUser:
    role: str
    user_id: int
    username: str
    display_name: str
