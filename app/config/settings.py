from __future__ import annotations

from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    charset: str


@dataclass(slots=True)
class StorageConfig:
    attachment_root: str


@dataclass(slots=True)
class Settings:
    database: DatabaseConfig
    storage: StorageConfig

    @classmethod
    def load(cls) -> "Settings":
        config_path = Path(__file__).with_name("config.ini")
        if not config_path.exists():
            config_path = Path(__file__).with_name("config.ini.example")

        parser = ConfigParser()
        parser.read(config_path, encoding="utf-8")

        return cls(
            database=DatabaseConfig(
                host=parser.get("database", "host"),
                port=parser.getint("database", "port"),
                user=parser.get("database", "user"),
                password=parser.get("database", "password"),
                database=parser.get("database", "database"),
                charset=parser.get("database", "charset", fallback="utf8mb4"),
            ),
            storage=StorageConfig(
                attachment_root=parser.get("storage", "attachment_root", fallback="attachments")
            ),
        )
