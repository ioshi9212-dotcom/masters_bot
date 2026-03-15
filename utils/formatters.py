from __future__ import annotations

import json


def format_master_profile(master) -> str:
    professions = ", ".join(json.loads(master["professions"])) if master["professions"] else "—"
    return (
        "👤 Профиль мастера\n\n"
        f"Имя: {master['first_name']}\n"
        f"Фамилия: {master['last_name'] or '—'}\n"
        f"Профессии: {professions}\n"
        f"Дата рождения: {master['birth_date'] or '—'}\n"
        f"Телефон: {master['phone']}\n"
        f"Адрес: {master['work_address']}\n"
        f"Код мастера: {master['master_code']}"
    )


def format_client_profile(client) -> str:
    return (
        "👤 Ваш профиль\n\n"
        f"Имя: {client['first_name'] or '—'}\n"
        f"Фамилия: {client['last_name'] or '—'}\n"
        f"Телефон: {client['phone'] or '—'}\n"
        f"Дата рождения: {client['birth_date'] or '—'}"
    )
