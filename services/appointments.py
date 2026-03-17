from __future__ import annotations

from datetime import datetime, timedelta


def has_time_overlap(existing_start: str, existing_end: str, new_start: str, new_end: str) -> bool:
    """Возвращает True, если интервалы времени пересекаются."""
    return new_start < existing_end and new_end > existing_start


def calculate_end_time(start_time: str, duration_minutes: int) -> str:
    start_dt = datetime.strptime(start_time, "%H:%M")
    return (start_dt + timedelta(minutes=duration_minutes)).strftime("%H:%M")


def is_slot_available(
    slot_start: str,
    duration_minutes: int,
    window_start: str,
    window_end: str,
    appointments: list,
) -> tuple[bool, str]:
    """
    Проверяет, что запись полностью помещается в окно и не пересекается с существующими записями.

    appointments: iterable словарей/Row с ключами start_time/end_time
    """
    slot_end = calculate_end_time(slot_start, duration_minutes)

    if slot_start < window_start or slot_end > window_end:
        return False, slot_end

    for ap in appointments:
        if has_time_overlap(ap["start_time"], ap["end_time"], slot_start, slot_end):
            return False, slot_end

    return True, slot_end
"""Бизнес-логика записей (каркас для дальнейшего расширения)."""
