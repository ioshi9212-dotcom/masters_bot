from __future__ import annotations

from datetime import date

MONTHS_RU = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}



def calculate_experience_text(month: int, year: int) -> str:
    today = date.today()
    months = (today.year - year) * 12 + (today.month - month)
    if months < 0:
        return "Стаж: меньше месяца"
    years = months // 12
    rem_months = months % 12
    return f"В сфере с {MONTHS_RU[month]} {year}. Стаж: {years} г. {rem_months} мес."
