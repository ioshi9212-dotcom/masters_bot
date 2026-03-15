from __future__ import annotations

import aiosqlite


class Database:
    def __init__(self, path: str) -> None:
        self.path = path

    async def connect(self) -> aiosqlite.Connection:
        conn = await aiosqlite.connect(self.path)
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA foreign_keys = ON;")
        return conn
