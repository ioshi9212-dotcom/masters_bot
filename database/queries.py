from __future__ import annotations

import json
import random
from datetime import datetime, timezone

from database.models import SCHEMA_SQL


DEFAULT_MANUAL_DURATIONS = [30, 60, 90, 120, 150, 180, 210, 240]


class Queries:
    def __init__(self, conn):
        self.conn = conn

    async def init_schema(self) -> None:
        await self.conn.executescript(SCHEMA_SQL)
        await self.conn.commit()

    async def get_master_by_telegram_id(self, telegram_id: int):
        cur = await self.conn.execute(
            "SELECT * FROM masters WHERE telegram_id = ? AND is_active = 1", (telegram_id,)
        )
        return await cur.fetchone()

    async def get_client_by_telegram_id(self, telegram_id: int):
        cur = await self.conn.execute(
            "SELECT * FROM clients WHERE telegram_id = ? AND is_active = 1", (telegram_id,)
        )
        return await cur.fetchone()

    async def generate_unique_master_code(self) -> str:
        while True:
            candidate = f"master{random.randint(1000, 9999)}"
            cur = await self.conn.execute("SELECT id FROM masters WHERE master_code = ?", (candidate,))
            if await cur.fetchone() is None:
                return candidate

    async def create_master(self, telegram_id: int, username: str | None, data: dict) -> int:
        now = datetime.now(timezone.utc).isoformat()
        code = await self.generate_unique_master_code()
        cur = await self.conn.execute(
            """
            INSERT INTO masters (
                telegram_id, master_code, username, first_name, last_name, professions,
                birth_date, work_start_month, work_start_year, work_experience_text,
                phone, work_address, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                code,
                username,
                data["first_name"],
                data.get("last_name"),
                json.dumps(data.get("professions", []), ensure_ascii=False),
                data["birth_date"],
                data["work_start_month"],
                data["work_start_year"],
                data["work_experience_text"],
                data["phone"],
                data["work_address"],
                now,
                now,
            ),
        )
        master_id = cur.lastrowid
        await self.conn.execute(
            """
            INSERT INTO booking_settings (
                master_id, time_step_minutes, first_booking_time, last_booking_time,
                booking_range_days, manual_duration_options, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (master_id, 30, "10:00", "19:00", 14, json.dumps(DEFAULT_MANUAL_DURATIONS), now),
        )
        await self.conn.commit()
        return master_id

    async def upsert_client_profile(self, telegram_id: int, username: str | None, data: dict) -> int:
        now = datetime.now(timezone.utc).isoformat()
        existing = await self.get_client_by_telegram_id(telegram_id)
        if existing:
            await self.conn.execute(
                """
                UPDATE clients
                SET username = ?, first_name = ?, last_name = ?, phone = ?, birth_date = ?,
                    updated_at = ?, is_registered = 1, is_active = 1
                WHERE telegram_id = ?
                """,
                (
                    username,
                    data["first_name"],
                    data.get("last_name"),
                    data.get("phone"),
                    data.get("birth_date"),
                    now,
                    telegram_id,
                ),
            )
            await self.conn.commit()
            return existing["id"]

        cur = await self.conn.execute(
            """
            INSERT INTO clients (
                telegram_id, username, first_name, last_name, phone, birth_date,
                created_by, is_registered, is_active, no_show_count, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'client', 1, 1, 0, ?, ?)
            """,
            (
                telegram_id,
                username,
                data["first_name"],
                data.get("last_name"),
                data.get("phone"),
                data.get("birth_date"),
                now,
                now,
            ),
        )
        await self.conn.commit()
        return cur.lastrowid

    async def deactivate_master_profile(self, telegram_id: int) -> None:
        master = await self.get_master_by_telegram_id(telegram_id)
        if not master:
            return
        mid = master["id"]
        await self.conn.execute("DELETE FROM masters WHERE id = ?", (mid,))
        await self.conn.commit()

    async def list_master_clients(self, master_id: int):
        cur = await self.conn.execute(
            """
            SELECT c.*
            FROM clients c
            JOIN client_masters cm ON cm.client_id = c.id
            WHERE cm.master_id = ? AND c.is_active = 1
            ORDER BY c.first_name, c.last_name, c.id
            """,
            (master_id,),
        )
        return await cur.fetchall()

    async def get_master_client(self, master_id: int, client_id: int):
        cur = await self.conn.execute(
            """
            SELECT c.*
            FROM clients c
            JOIN client_masters cm ON cm.client_id = c.id
            WHERE cm.master_id = ? AND c.id = ? AND c.is_active = 1
            """,
            (master_id, client_id),
        )
        return await cur.fetchone()

    async def create_manual_client_for_master(self, master_id: int, data: dict) -> int:
        now = datetime.now(timezone.utc).isoformat()
        cur = await self.conn.execute(
            """
            INSERT INTO clients (
                telegram_id, username, first_name, last_name, phone, birth_date,
                created_by, is_registered, is_active, no_show_count, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'master', 0, 1, 0, ?, ?)
            """,
            (
                None,
                None,
                data["first_name"],
                data["last_name"],
                data.get("phone"),
                data.get("birth_date"),
                now,
                now,
            ),
        )
        client_id = cur.lastrowid
        await self.conn.execute(
            """
            INSERT INTO client_masters (client_id, master_id, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (client_id, master_id, now, now),
        )
        await self.conn.commit()
        return client_id

    async def update_manual_client(self, client_id: int, data: dict) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        cur = await self.conn.execute(
            """
            UPDATE clients
            SET first_name = ?, last_name = ?, phone = ?, birth_date = ?, updated_at = ?
            WHERE id = ? AND created_by = 'master'
            """,
            (
                data["first_name"],
                data["last_name"],
                data.get("phone"),
                data.get("birth_date"),
                now,
                client_id,
            ),
        )
        await self.conn.commit()
        return cur.rowcount > 0

    async def delete_client_from_master(self, master_id: int, client_id: int) -> None:
        await self.conn.execute(
            """
            DELETE FROM appointments
            WHERE master_id = ?
              AND client_id = ?
              AND status = 'scheduled'
              AND appointment_date >= date('now')
            """,
            (master_id, client_id),
        )

        await self.conn.execute(
            "DELETE FROM client_masters WHERE master_id = ? AND client_id = ?",
            (master_id, client_id),
        )

        links_cur = await self.conn.execute(
            "SELECT COUNT(*) AS cnt FROM client_masters WHERE client_id = ?",
            (client_id,),
        )
        links_count = (await links_cur.fetchone())["cnt"]

        client_cur = await self.conn.execute("SELECT created_by FROM clients WHERE id = ?", (client_id,))
        client = await client_cur.fetchone()
        if client and links_count == 0 and client["created_by"] == "master":
            await self.conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))

        await self.conn.commit()
