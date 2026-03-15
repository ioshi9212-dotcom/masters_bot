from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone

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

    async def get_booking_settings(self, master_id: int):
        cur = await self.conn.execute("SELECT * FROM booking_settings WHERE master_id = ?", (master_id,))
        return await cur.fetchone()

    async def list_future_appointments(self, master_id: int):
        cur = await self.conn.execute(
            """
            SELECT a.*, c.first_name AS client_first_name, c.last_name AS client_last_name,
                   c.telegram_id AS client_telegram_id, s.name AS service_name
            FROM appointments a
            LEFT JOIN clients c ON c.id = a.client_id
            LEFT JOIN services s ON s.id = a.service_id
            WHERE a.master_id = ?
              AND a.status = 'scheduled'
              AND a.appointment_date >= date('now')
            ORDER BY a.appointment_date, a.start_time
            """,
            (master_id,),
        )
        return await cur.fetchall()

    async def list_appointment_dates_counts(self, master_id: int):
        cur = await self.conn.execute(
            """
            SELECT appointment_date, COUNT(*) AS cnt
            FROM appointments
            WHERE master_id = ?
              AND status = 'scheduled'
              AND appointment_date >= date('now')
            GROUP BY appointment_date
            ORDER BY appointment_date
            """,
            (master_id,),
        )
        return await cur.fetchall()

    async def list_appointments_by_date(self, master_id: int, date_iso: str):
        cur = await self.conn.execute(
            """
            SELECT a.*, c.first_name AS client_first_name, c.last_name AS client_last_name,
                   c.telegram_id AS client_telegram_id, s.name AS service_name
            FROM appointments a
            LEFT JOIN clients c ON c.id = a.client_id
            LEFT JOIN services s ON s.id = a.service_id
            WHERE a.master_id = ?
              AND a.status = 'scheduled'
              AND a.appointment_date = ?
            ORDER BY a.start_time
            """,
            (master_id, date_iso),
        )
        return await cur.fetchall()

    async def get_appointment_by_id(self, master_id: int, appointment_id: int):
        cur = await self.conn.execute(
            """
            SELECT a.*, c.telegram_id AS client_telegram_id
            FROM appointments a
            LEFT JOIN clients c ON c.id = a.client_id
            WHERE a.master_id = ? AND a.id = ?
            """,
            (master_id, appointment_id),
        )
        return await cur.fetchone()

    async def restore_free_window_from_appointment(self, appointment) -> None:
        exists_cur = await self.conn.execute(
            """
            SELECT id FROM free_windows
            WHERE master_id = ? AND window_date = ? AND start_time = ? AND is_active = 1
            """,
            (appointment["master_id"], appointment["appointment_date"], appointment["start_time"]),
        )
        exists = await exists_cur.fetchone()
        if exists:
            return
        now = datetime.now(timezone.utc).isoformat()
        await self.conn.execute(
            """
            INSERT INTO free_windows (master_id, window_date, start_time, end_time, is_active, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (
                appointment["master_id"],
                appointment["appointment_date"],
                appointment["start_time"],
                appointment["end_time"],
                now,
            ),
        )

    async def delete_appointment(self, master_id: int, appointment_id: int):
        appointment = await self.get_appointment_by_id(master_id, appointment_id)
        if not appointment:
            return None
        await self.conn.execute("DELETE FROM appointments WHERE id = ? AND master_id = ?", (appointment_id, master_id))
        await self.restore_free_window_from_appointment(appointment)
        await self.conn.commit()
        return appointment

    async def delete_all_future_appointments(self, master_id: int) -> int:
        items = await self.list_future_appointments(master_id)
        for item in items:
            await self.restore_free_window_from_appointment(item)
        cur = await self.conn.execute(
            """
            DELETE FROM appointments
            WHERE master_id = ?
              AND status = 'scheduled'
              AND appointment_date >= date('now')
            """,
            (master_id,),
        )
        await self.conn.commit()
        return cur.rowcount

    async def list_free_windows(self, master_id: int):
        cur = await self.conn.execute(
            """
            SELECT * FROM free_windows
            WHERE master_id = ? AND is_active = 1 AND window_date >= date('now')
            ORDER BY window_date, start_time
            """,
            (master_id,),
        )
        return await cur.fetchall()

    async def list_windows_by_date(self, master_id: int, date_iso: str):
        cur = await self.conn.execute(
            """
            SELECT * FROM free_windows
            WHERE master_id = ? AND is_active = 1 AND window_date = ?
            ORDER BY start_time
            """,
            (master_id, date_iso),
        )
        return await cur.fetchall()

    async def add_free_window(self, master_id: int, date_iso: str, start_time: str, end_time: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        exists_cur = await self.conn.execute(
            """
            SELECT id FROM free_windows
            WHERE master_id = ? AND window_date = ? AND start_time = ? AND is_active = 1
            """,
            (master_id, date_iso, start_time),
        )
        if await exists_cur.fetchone():
            return
        await self.conn.execute(
            """
            INSERT INTO free_windows (master_id, window_date, start_time, end_time, is_active, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (master_id, date_iso, start_time, end_time, now),
        )
        await self.conn.commit()

    async def delete_free_window(self, master_id: int, window_id: int) -> None:
        await self.conn.execute("DELETE FROM free_windows WHERE id = ? AND master_id = ?", (window_id, master_id))
        await self.conn.commit()

    async def delete_all_free_windows(self, master_id: int) -> int:
        cur = await self.conn.execute("DELETE FROM free_windows WHERE master_id = ? AND is_active = 1", (master_id,))
        await self.conn.commit()
        return cur.rowcount


    async def list_master_services(self, master_id: int, active_only: bool = False):
        sql = "SELECT * FROM services WHERE master_id = ?"
        params = [master_id]
        if active_only:
            sql += " AND is_active = 1"
        sql += " ORDER BY created_at DESC, id DESC"
        cur = await self.conn.execute(sql, tuple(params))
        return await cur.fetchall()

    async def create_service(self, master_id: int, name: str, description: str, duration_minutes: int, price: float) -> int:
        now = datetime.now(timezone.utc).isoformat()
        cur = await self.conn.execute(
            """
            INSERT INTO services (master_id, name, description, duration_minutes, price, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (master_id, name, description, duration_minutes, price, now, now),
        )
        await self.conn.commit()
        return cur.lastrowid

    async def get_service_by_id(self, master_id: int, service_id: int):
        cur = await self.conn.execute(
            "SELECT * FROM services WHERE id = ? AND master_id = ?",
            (service_id, master_id),
        )
        return await cur.fetchone()

    async def update_service_price(self, master_id: int, service_id: int, price: float) -> None:
        now = datetime.now(timezone.utc).isoformat()
        await self.conn.execute(
            "UPDATE services SET price = ?, updated_at = ? WHERE id = ? AND master_id = ?",
            (price, now, service_id, master_id),
        )
        await self.conn.commit()

    async def service_has_scheduled_appointments(self, master_id: int, service_id: int) -> bool:
        cur = await self.conn.execute(
            """
            SELECT 1
            FROM appointments
            WHERE master_id = ? AND service_id = ? AND status = 'scheduled'
            LIMIT 1
            """,
            (master_id, service_id),
        )
        return await cur.fetchone() is not None

    async def delete_or_deactivate_service(self, master_id: int, service_id: int) -> str:
        has_future = await self.service_has_scheduled_appointments(master_id, service_id)
        if has_future:
            now = datetime.now(timezone.utc).isoformat()
            await self.conn.execute(
                "UPDATE services SET is_active = 0, updated_at = ? WHERE id = ? AND master_id = ?",
                (now, service_id, master_id),
            )
            await self.conn.commit()
            return "deactivated"
        await self.conn.execute("DELETE FROM services WHERE id = ? AND master_id = ?", (service_id, master_id))
        await self.conn.commit()
        return "deleted"

    async def update_master_field(self, master_id: int, field: str, value) -> None:
        allowed = {
            "first_name",
            "last_name",
            "phone",
            "birth_date",
            "work_start_month",
            "work_start_year",
            "work_experience_text",
            "work_address",
            "professions",
        }
        if field not in allowed:
            raise ValueError("Недопустимое поле")
        now = datetime.now(timezone.utc).isoformat()
        await self.conn.execute(
            f"UPDATE masters SET {field} = ?, updated_at = ? WHERE id = ?",
            (value, now, master_id),
        )
        await self.conn.commit()

    async def update_booking_settings(self, master_id: int, field: str, value) -> None:
        allowed = {
            "time_step_minutes",
            "first_booking_time",
            "last_booking_time",
            "booking_range_days",
            "manual_duration_options",
            "client_booking_limit_type",
            "client_booking_limit_value",
        }
        if field not in allowed:
            raise ValueError("Недопустимое поле")
        now = datetime.now(timezone.utc).isoformat()
        await self.conn.execute(
            f"UPDATE booking_settings SET {field} = ?, updated_at = ? WHERE master_id = ?",
            (value, now, master_id),
        )
        await self.conn.commit()

    async def stats_summary(self, master_id: int, days: int) -> dict:
        cur = await self.conn.execute(
            """
            SELECT
                COALESCE(SUM(income_amount), 0) AS income,
                COALESCE(SUM(appointments_count), 0) AS appointments,
                COALESCE(SUM(worked_minutes), 0) AS worked_minutes,
                COALESCE(SUM(cancelled_by_client_count), 0) AS cancelled_by_client,
                COALESCE(SUM(cancelled_by_master_count), 0) AS cancelled_by_master,
                COALESCE(SUM(no_show_count), 0) AS no_show,
                COALESCE(MAX(sleeping_clients_count), 0) AS sleeping
            FROM daily_stats
            WHERE master_id = ? AND stats_date >= date('now', ?)
            """,
            (master_id, f"-{days} day"),
        )
        row = await cur.fetchone()

        new_clients_cur = await self.conn.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM clients c
            JOIN client_masters cm ON cm.client_id = c.id
            WHERE cm.master_id = ?
              AND c.created_at >= datetime('now', ?)
            """,
            (master_id, f"-{days} day"),
        )
        new_clients = (await new_clients_cur.fetchone())["cnt"]

        return {
            "income": row["income"],
            "appointments": row["appointments"],
            "worked_minutes": row["worked_minutes"],
            "cancelled_by_client": row["cancelled_by_client"],
            "cancelled_by_master": row["cancelled_by_master"],
            "no_show": row["no_show"],
            "sleeping": row["sleeping"],
            "new_clients": new_clients,
        }


    async def ensure_client_from_telegram(self, telegram_id: int, username: str | None) -> int | None:
        client = await self.get_client_by_telegram_id(telegram_id)
        return client["id"] if client else None

    async def get_master_by_code(self, master_code: str):
        cur = await self.conn.execute(
            "SELECT * FROM masters WHERE master_code = ? AND is_active = 1",
            (master_code,),
        )
        return await cur.fetchone()

    async def is_client_linked_to_master(self, client_id: int, master_id: int) -> bool:
        cur = await self.conn.execute(
            "SELECT 1 FROM client_masters WHERE client_id = ? AND master_id = ?",
            (client_id, master_id),
        )
        return await cur.fetchone() is not None

    async def link_client_to_master(self, client_id: int, master_id: int) -> bool:
        if await self.is_client_linked_to_master(client_id, master_id):
            return False
        now = datetime.now(timezone.utc).isoformat()
        await self.conn.execute(
            "INSERT INTO client_masters (client_id, master_id, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (client_id, master_id, now, now),
        )
        await self.conn.commit()
        return True

    async def list_client_masters(self, client_id: int):
        cur = await self.conn.execute(
            """
            SELECT m.*
            FROM masters m
            JOIN client_masters cm ON cm.master_id = m.id
            WHERE cm.client_id = ? AND m.is_active = 1
            ORDER BY m.first_name, m.last_name, m.id
            """,
            (client_id,),
        )
        return await cur.fetchall()

    async def list_master_active_services(self, master_id: int):
        return await self.list_master_services(master_id, active_only=True)

    async def list_available_windows_for_service(self, master_id: int, service_id: int):
        service = await self.get_service_by_id(master_id, service_id)
        if not service:
            return []
        duration = service["duration_minutes"]

        settings = await self.get_booking_settings(master_id)
        booking_range_days = settings["booking_range_days"] if settings else 14

        cur = await self.conn.execute(
            """
            SELECT fw.*
            FROM free_windows fw
            WHERE fw.master_id = ?
              AND fw.is_active = 1
              AND fw.window_date >= date('now')
              AND fw.window_date <= date('now', ?)
              AND (
                (strftime('%s', '2000-01-01 ' || fw.end_time) - strftime('%s', '2000-01-01 ' || fw.start_time)) / 60
              ) >= ?
            ORDER BY fw.window_date, fw.start_time
            """,
            (master_id, f"+{booking_range_days} day", duration),
        )
        return await cur.fetchall()

    async def get_free_window_for_master(self, master_id: int, window_id: int):
        cur = await self.conn.execute(
            "SELECT * FROM free_windows WHERE id = ? AND master_id = ? AND is_active = 1",
            (window_id, master_id),
        )
        return await cur.fetchone()

    async def create_client_appointment_from_window(self, master_id: int, client_id: int, service_id: int, window_id: int):
        service = await self.get_service_by_id(master_id, service_id)
        window = await self.get_free_window_for_master(master_id, window_id)
        if not service or not window:
            return None

        duration = service["duration_minutes"]
        start = datetime.strptime(window["start_time"], "%H:%M")
        end = start + timedelta(minutes=duration)
        end_time = end.strftime("%H:%M")

        # check overlaps
        overlap_cur = await self.conn.execute(
            """
            SELECT 1
            FROM appointments
            WHERE master_id = ?
              AND appointment_date = ?
              AND status = 'scheduled'
              AND NOT (end_time <= ? OR start_time >= ?)
            LIMIT 1
            """,
            (master_id, window["window_date"], window["start_time"], end_time),
        )
        if await overlap_cur.fetchone():
            return None

        now = datetime.now(timezone.utc).isoformat()
        cur = await self.conn.execute(
            """
            INSERT INTO appointments (
                master_id, client_id, service_id, appointment_date, start_time, end_time,
                duration_minutes, price_amount, status, created_by, is_confirmed_by_client,
                cancelled_by, no_show_status, included_in_stats, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'scheduled', 'client', 0, NULL, 'pending', 0, ?, ?)
            """,
            (
                master_id,
                client_id,
                service_id,
                window["window_date"],
                window["start_time"],
                end_time,
                duration,
                service["price"],
                now,
                now,
            ),
        )
        appointment_id = cur.lastrowid

        await self.conn.execute("DELETE FROM free_windows WHERE id = ?", (window_id,))
        await self.conn.commit()

        out_cur = await self.conn.execute(
            """
            SELECT a.*, s.name AS service_name, m.telegram_id AS master_telegram_id
            FROM appointments a
            LEFT JOIN services s ON s.id = a.service_id
            LEFT JOIN masters m ON m.id = a.master_id
            WHERE a.id = ?
            """,
            (appointment_id,),
        )
        return await out_cur.fetchone()

    async def get_client_with_id(self, client_id: int):
        cur = await self.conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        return await cur.fetchone()

    async def delete_client_profile_with_future_appointments(self, telegram_id: int):
        client = await self.get_client_by_telegram_id(telegram_id)
        if not client:
            return []
        client_id = client["id"]

        masters_cur = await self.conn.execute(
            """
            SELECT DISTINCT m.telegram_id AS tg_id
            FROM appointments a
            JOIN masters m ON m.id = a.master_id
            WHERE a.client_id = ?
              AND a.status = 'scheduled'
              AND a.appointment_date >= date('now')
            """,
            (client_id,),
        )
        masters_to_notify = [r["tg_id"] for r in await masters_cur.fetchall() if r["tg_id"]]

        future_cur = await self.conn.execute(
            """
            SELECT *
            FROM appointments
            WHERE client_id = ?
              AND status = 'scheduled'
              AND appointment_date >= date('now')
            """,
            (client_id,),
        )
        for ap in await future_cur.fetchall():
            await self.restore_free_window_from_appointment(ap)

        await self.conn.execute(
            """
            DELETE FROM appointments
            WHERE client_id = ?
              AND status = 'scheduled'
              AND appointment_date >= date('now')
            """,
            (client_id,),
        )
        await self.conn.execute("DELETE FROM client_masters WHERE client_id = ?", (client_id,))
        await self.conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        await self.conn.commit()
        return masters_to_notify
