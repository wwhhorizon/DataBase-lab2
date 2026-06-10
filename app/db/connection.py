from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterable

import pymysql
from pymysql.connections import Connection
from pymysql.cursors import DictCursor

from app.config.settings import DatabaseConfig


class Database:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._connection = self._connect()

    def _connect(self) -> Connection:
        return pymysql.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            database=self.config.database,
            charset=self.config.charset,
            cursorclass=DictCursor,
            autocommit=False,
        )

    def ensure_connection(self) -> Connection:
        try:
            self._connection.ping(reconnect=True)
        except Exception:
            self._connection = self._connect()
        return self._connection

    @contextmanager
    def cursor(self):
        connection = self.ensure_connection()
        cursor = connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    def query_all(self, sql: str, params: Iterable[Any] | None = None) -> list[dict[str, Any]]:
        with self.cursor() as cursor:
            cursor.execute(sql, params or ())
            return list(cursor.fetchall())

    def query_one(self, sql: str, params: Iterable[Any] | None = None) -> dict[str, Any] | None:
        with self.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchone()

    def execute(self, sql: str, params: Iterable[Any] | None = None) -> int:
        with self.cursor() as cursor:
            affected = cursor.execute(sql, params or ())
        self.ensure_connection().commit()
        return affected

    def executemany(self, sql: str, params: list[Iterable[Any]]) -> int:
        with self.cursor() as cursor:
            affected = cursor.executemany(sql, params)
        self.ensure_connection().commit()
        return affected

    def execute_transaction(self, operations):
        connection = self.ensure_connection()
        try:
            result = operations(connection)
            connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
