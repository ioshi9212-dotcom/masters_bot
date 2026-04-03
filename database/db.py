from __future__ import annotations

import aiosqlite
import logging


class Database:
    def __init__(self, path: str) -> None:
        self.path = path

    async def connect(self) -> aiosqlite.Connection:
        logging.info(f"Подключение к БД: {self.path}")

        conn = await aiosqlite.connect(self.path)

        conn.row_factory = aiosqlite.Row

        # Включаем внешние ключи
        await conn.execute("PRAGMA foreign_keys = ON;")

        # Улучшение для стабильности SQLite
        await conn.execute("PRAGMA journal_mode = WAL;")
        await conn.execute("PRAGMA synchronous = NORMAL;")

        return conn
