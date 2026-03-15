from __future__ import annotations

from datetime import date, datetime, time, timedelta

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from database.queries import Queries
from keyboards.common import SKIP_BACK_HOME_KB
from keyboards.confirm import (
    CONFIRM_DELETE_ALL_APPOINTMENTS_KB,
    CONFIRM_DELETE_ALL_WINDOWS_KB,
    CONFIRM_DELETE_CLIENT_KB,
)
from keyboards.master import (
    MASTER_APPOINTMENTS_KB,
    MASTER_BOOKING_ENTRY_KB,
    MASTER_CLIENTS_TOP_KB,
    MASTER_WINDOWS_KB,
)
from states.master_states import (
    MasterAppointmentsState,
    MasterClientCreateState,
    MasterClientDeleteState,
    MasterClientEditState,
    MasterClientsState,
    MasterWindowsState,
)

router = Router()

WEEKDAYS_RU = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
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


def _display_name(client) -> str:
    return f"{client['first_name'] or ''} {client['last_name'] or ''}".strip() or f"Клиент {client['id']}"


def _client_btn_text(client) -> str:
    return f"👤 {_display_name(client)} [#{client['id']}]"


def _parse_client_id(text: str) -> int | None:
    if "[#" not in text or not text.endswith("]"):
        return None
    try:
        return int(text.split("[#")[-1].rstrip("]"))
    except ValueError:
        return None


def _clients_keyboard(clients) -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text="✏️ Редактировать клиента"), KeyboardButton(text="🗑 Удалить клиента")]]
    for client in clients:
        rows.append([KeyboardButton(text=_client_btn_text(client))])
    rows.append([KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def _format_date_iso(date_iso: str) -> str:
    d = date.fromisoformat(date_iso)
    return f"{d.day} {MONTHS_RU[d.month]} {WEEKDAYS_RU[d.weekday()]}"


def _format_appointment_line(item) -> str:
    client_name = f"{item['client_first_name'] or ''} {item['client_last_name'] or ''}".strip() or "Клиент"
    service = item["service_name"] or "Без услуги"
    return f"{item['start_time']} — {client_name} ({service})"


def _parse_date_token(text: str) -> str | None:
    if "[d:" not in text or not text.endswith("]"):
        return None
    token = text.split("[d:")[-1].rstrip("]")
    try:
        date.fromisoformat(token)
        return token
    except ValueError:
        return None


def _parse_appointment_token(text: str) -> int | None:
    if "[a:" not in text or not text.endswith("]"):
        return None
    token = text.split("[a:")[-1].rstrip("]")
    try:
        return int(token)
    except ValueError:
        return None


def _parse_window_token(text: str) -> int | None:
    if "[w:" not in text or not text.endswith("]"):
        return None
    token = text.split("[w:")[-1].rstrip("]")
    try:
        return int(token)
    except ValueError:
        return None


def _add_minutes(hhmm: str, minutes: int) -> str:
    dt = datetime.combine(date.today(), time.fromisoformat(hhmm)) + timedelta(minutes=minutes)
    return dt.time().strftime("%H:%M")


def _time_slots(first: str, last: str, step: int):
    cur = datetime.combine(date.today(), time.fromisoformat(first))
    end = datetime.combine(date.today(), time.fromisoformat(last))
    out = []
    while cur <= end:
        out.append(cur.time().strftime("%H:%M"))
        cur += timedelta(minutes=step)
    return out


async def _master_or_error(message: Message, db):
    conn = await db.connect()
    q = Queries(conn)
    master = await q.get_master_by_telegram_id(message.from_user.id)
    if not master:
        await conn.close()
        await message.answer("Сначала выберите роль мастера через /start")
        return None, None, None
    return conn, q, master


# ----------------------
# 3.x Записать клиента (блок клиентов)
# ----------------------
@router.message(F.text == "✍️ Записать клиента")
async def master_booking(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Раздел ✍️ Записать клиента.\n\n"
        "Пока доступно управление клиентами:\n"
        "• 👥 Мои клиенты\n"
        "• ➕ Добавить клиента",
        reply_markup=MASTER_BOOKING_ENTRY_KB,
    )


@router.message(F.text == "👥 Мои клиенты")
async def master_clients(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    clients = await q.list_master_clients(master["id"])
    await conn.close()

    if not clients:
        await message.answer(
            "Список клиентов пока пуст. Добавьте клиента через ➕ Добавить клиента.",
            reply_markup=MASTER_BOOKING_ENTRY_KB,
        )
        return

    await state.set_state(MasterClientsState.viewing)
    await message.answer("Выберите клиента:", reply_markup=_clients_keyboard(clients))


@router.message(MasterClientsState.viewing, F.text == "✏️ Редактировать клиента")
async def start_edit_client(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    clients = await q.list_master_clients(master["id"])
    await conn.close()

    if not clients:
        await message.answer("У вас пока нет клиентов для редактирования.", reply_markup=MASTER_BOOKING_ENTRY_KB)
        return

    await state.set_state(MasterClientEditState.select_client)
    await message.answer("Выберите клиента для редактирования:", reply_markup=_clients_keyboard(clients))


@router.message(MasterClientsState.viewing, F.text == "🗑 Удалить клиента")
async def start_delete_client(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    clients = await q.list_master_clients(master["id"])
    await conn.close()

    if not clients:
        await message.answer("У вас пока нет клиентов для удаления.", reply_markup=MASTER_BOOKING_ENTRY_KB)
        return

    await state.set_state(MasterClientDeleteState.select_client)
    await message.answer("Выберите клиента для удаления:", reply_markup=_clients_keyboard(clients))


@router.message(MasterClientsState.viewing)
async def show_client_card(message: Message, db) -> None:
    client_id = _parse_client_id(message.text)
    if not client_id:
        return

    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    client = await q.get_master_client(master["id"], client_id)
    await conn.close()
    if not client:
        await message.answer("Клиент не найден.")
        return

    await message.answer(
        "👤 Клиент\n"
        f"{_display_name(client)}\n\n"
        f"📱 Телефон\n{client['phone'] or '—'}\n\n"
        f"🎂 Дата рождения\n{client['birth_date'] or '—'}",
        reply_markup=MASTER_CLIENTS_TOP_KB,
    )


@router.message(F.text == "➕ Добавить клиента")
async def add_client_start(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterClientCreateState.first_name)
    await message.answer("Введите имя клиента:", reply_markup=MASTER_BOOKING_ENTRY_KB)


@router.message(MasterClientCreateState.first_name)
async def add_client_first_name(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text.strip())
    await state.set_state(MasterClientCreateState.last_name)
    await message.answer("Введите фамилию клиента:")


@router.message(MasterClientCreateState.last_name)
async def add_client_last_name(message: Message, state: FSMContext) -> None:
    await state.update_data(last_name=message.text.strip())
    await state.set_state(MasterClientCreateState.phone)
    await message.answer("Введите номер телефона или нажмите ⏭ Пропустить", reply_markup=SKIP_BACK_HOME_KB)


@router.message(MasterClientCreateState.phone)
async def add_client_phone(message: Message, state: FSMContext) -> None:
    phone = None if message.text == "⏭ Пропустить" else message.text.strip()
    await state.update_data(phone=phone)
    await state.set_state(MasterClientCreateState.birth_date)
    await message.answer("Введите дату рождения (ДД.ММ) или нажмите ⏭ Пропустить", reply_markup=SKIP_BACK_HOME_KB)


@router.message(MasterClientCreateState.birth_date)
async def add_client_birth_date(message: Message, state: FSMContext, db) -> None:
    birth_date = None if message.text == "⏭ Пропустить" else message.text.strip()
    await state.update_data(birth_date=birth_date)
    data = await state.get_data()

    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    await q.create_manual_client_for_master(master["id"], data)
    await conn.close()

    await state.clear()
    await message.answer(
        "✅ Клиент добавлен.\n\n"
        "⚠️ Этому клиенту оповещения не придут. Чтобы они приходили, клиент должен зарегистрироваться со своего аккаунта Telegram.",
        reply_markup=MASTER_BOOKING_ENTRY_KB,
    )


@router.message(MasterClientEditState.select_client)
async def edit_select_client(message: Message, state: FSMContext, db) -> None:
    client_id = _parse_client_id(message.text)
    if not client_id:
        return

    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    client = await q.get_master_client(master["id"], client_id)
    await conn.close()
    if not client:
        await message.answer("Клиент не найден.")
        return

    if client["created_by"] != "master":
        await state.set_state(MasterClientsState.viewing)
        await message.answer(
            "Редактировать данные этого клиента может только сам клиент через своё меню.",
            reply_markup=MASTER_CLIENTS_TOP_KB,
        )
        return

    await state.update_data(edit_client_id=client_id)
    await state.set_state(MasterClientEditState.first_name)
    await message.answer("Введите новое имя клиента:")


@router.message(MasterClientEditState.first_name)
async def edit_client_first_name(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text.strip())
    await state.set_state(MasterClientEditState.last_name)
    await message.answer("Введите новую фамилию клиента:")


@router.message(MasterClientEditState.last_name)
async def edit_client_last_name(message: Message, state: FSMContext) -> None:
    await state.update_data(last_name=message.text.strip())
    await state.set_state(MasterClientEditState.phone)
    await message.answer("Введите новый номер телефона или нажмите ⏭ Пропустить", reply_markup=SKIP_BACK_HOME_KB)


@router.message(MasterClientEditState.phone)
async def edit_client_phone(message: Message, state: FSMContext) -> None:
    await state.update_data(phone=None if message.text == "⏭ Пропустить" else message.text.strip())
    await state.set_state(MasterClientEditState.birth_date)
    await message.answer("Введите новую дату рождения (ДД.ММ) или нажмите ⏭ Пропустить", reply_markup=SKIP_BACK_HOME_KB)


@router.message(MasterClientEditState.birth_date)
async def edit_client_birth(message: Message, state: FSMContext, db) -> None:
    birth_date = None if message.text == "⏭ Пропустить" else message.text.strip()
    data = await state.get_data()

    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    await q.update_manual_client(
        data["edit_client_id"],
        {
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "phone": data.get("phone"),
            "birth_date": birth_date,
        },
    )
    clients = await q.list_master_clients(master["id"])
    await conn.close()

    await state.set_state(MasterClientsState.viewing)
    await message.answer("✅ Данные клиента обновлены.", reply_markup=_clients_keyboard(clients))


@router.message(MasterClientDeleteState.select_client)
async def delete_select_client(message: Message, state: FSMContext, db) -> None:
    client_id = _parse_client_id(message.text)
    if not client_id:
        return

    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    client = await q.get_master_client(master["id"], client_id)
    await conn.close()
    if not client:
        await message.answer("Клиент не найден.")
        return

    await state.update_data(delete_client_id=client_id)
    await state.set_state(MasterClientDeleteState.confirm)
    await message.answer(
        "⚠️ Если вы удалите клиента, все его будущие записи тоже будут удалены.\n\n"
        "⚠️ Вы уверены, что хотите удалить клиента?",
        reply_markup=CONFIRM_DELETE_CLIENT_KB,
    )


@router.message(MasterClientDeleteState.confirm, F.text == "✅ Да, удалить")
async def confirm_delete_client(message: Message, state: FSMContext, db) -> None:
    data = await state.get_data()

    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    await q.delete_client_from_master(master["id"], data["delete_client_id"])
    clients = await q.list_master_clients(master["id"])
    await conn.close()

    await state.set_state(MasterClientsState.viewing)
    if clients:
        await message.answer("✅ Клиент удалён. Обновлённый список клиентов:", reply_markup=_clients_keyboard(clients))
    else:
        await state.clear()
        await message.answer("✅ Клиент удалён. Список клиентов теперь пуст.", reply_markup=MASTER_BOOKING_ENTRY_KB)


@router.message(MasterClientDeleteState.confirm, F.text == "◀️ Отмена")
async def cancel_delete_client(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    clients = await q.list_master_clients(master["id"])
    await conn.close()

    await state.set_state(MasterClientsState.viewing)
    await message.answer("Удаление отменено.", reply_markup=_clients_keyboard(clients) if clients else MASTER_BOOKING_ENTRY_KB)


# ----------------------
# 4.x Посмотреть записи
# ----------------------
@router.message(F.text == "📅 Посмотреть записи")
async def view_appointments(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    items = await q.list_future_appointments(master["id"])
    await conn.close()

    await state.set_state(MasterAppointmentsState.viewing)

    if not items:
        await message.answer("Пока нет будущих записей.", reply_markup=MASTER_APPOINTMENTS_KB)
        return

    chunks = []
    current_date = None
    current_lines = []
    for item in items:
        if item["appointment_date"] != current_date:
            if current_date is not None:
                chunks.append(f"✨ {_format_date_iso(current_date)}\n\n" + "\n\n".join(current_lines))
            current_date = item["appointment_date"]
            current_lines = [_format_appointment_line(item)]
        else:
            current_lines.append(_format_appointment_line(item))
    if current_date is not None:
        chunks.append(f"✨ {_format_date_iso(current_date)}\n\n" + "\n\n".join(current_lines))

    await message.answer("\n\n".join(chunks), reply_markup=MASTER_APPOINTMENTS_KB)


@router.message(MasterAppointmentsState.viewing, F.text == "🗑 Удалить запись")
async def delete_appointment_pick_date(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    dates = await q.list_appointment_dates_counts(master["id"])
    await conn.close()

    if not dates:
        await message.answer("Нет записей для удаления.", reply_markup=MASTER_APPOINTMENTS_KB)
        return

    rows = [[KeyboardButton(text=f"{_format_date_iso(i['appointment_date'])} ({i['cnt']} записи) [d:{i['appointment_date']}]")] for i in dates]
    rows.append([KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")])
    kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
    await state.set_state(MasterAppointmentsState.delete_pick_date)
    await message.answer("Выберите дату:", reply_markup=kb)


@router.message(MasterAppointmentsState.delete_pick_date)
async def delete_appointment_pick_item(message: Message, state: FSMContext, db) -> None:
    date_iso = _parse_date_token(message.text)
    if not date_iso:
        return

    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    items = await q.list_appointments_by_date(master["id"], date_iso)
    await conn.close()

    if not items:
        await message.answer("На этой дате нет записей.")
        return

    rows = [[KeyboardButton(text=f"{_format_appointment_line(i)} [a:{i['id']}]")] for i in items]
    rows.append([KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")])
    kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
    await state.set_state(MasterAppointmentsState.delete_pick_item)
    await message.answer(f"✨ {_format_date_iso(date_iso)}\n\nВыберите запись для удаления:", reply_markup=kb)


@router.message(MasterAppointmentsState.delete_pick_item)
async def delete_appointment_action(message: Message, state: FSMContext, db) -> None:
    appointment_id = _parse_appointment_token(message.text)
    if not appointment_id:
        return

    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    deleted = await q.delete_appointment(master["id"], appointment_id)
    await conn.close()

    if not deleted:
        await message.answer("Запись не найдена.")
        return

    client_tg = deleted["client_telegram_id"]
    if client_tg:
        try:
            await message.bot.send_message(client_tg, "📢 Ваша запись была удалена мастером.")
        except Exception:
            pass

    await state.set_state(MasterAppointmentsState.viewing)
    await message.answer("✅ Запись удалена.", reply_markup=MASTER_APPOINTMENTS_KB)


@router.message(MasterAppointmentsState.viewing, F.text == "🗑 Удалить все записи")
async def delete_all_appointments_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterAppointmentsState.delete_confirm_all)
    await message.answer(
        "⚠️ Вы уверены, что хотите удалить все записи?",
        reply_markup=CONFIRM_DELETE_ALL_APPOINTMENTS_KB,
    )


@router.message(MasterAppointmentsState.delete_confirm_all, F.text == "✅ Да, удалить все записи")
async def delete_all_appointments_action(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    deleted_count = await q.delete_all_future_appointments(master["id"])
    await conn.close()

    await state.set_state(MasterAppointmentsState.viewing)
    await message.answer(f"✅ Удалено записей: {deleted_count}", reply_markup=MASTER_APPOINTMENTS_KB)


@router.message(MasterAppointmentsState.delete_confirm_all, F.text == "◀️ Отмена")
async def delete_all_appointments_cancel(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterAppointmentsState.viewing)
    await message.answer("Удаление отменено.", reply_markup=MASTER_APPOINTMENTS_KB)


# ----------------------
# 5.x Свободные окна
# ----------------------
@router.message(F.text == "🕒 Свободные окна")
async def windows_menu(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    windows = await q.list_free_windows(master["id"])
    await conn.close()

    await state.set_state(MasterWindowsState.viewing)
    if not windows:
        await message.answer("Свободные окна пока не добавлены.", reply_markup=MASTER_WINDOWS_KB)
        return

    by_date: dict[str, list[str]] = {}
    for w in windows:
        by_date.setdefault(w["window_date"], []).append(w["start_time"])

    chunks = []
    for d in sorted(by_date.keys()):
        chunks.append(f"🕒 {_format_date_iso(d)}\n\n" + ", ".join(by_date[d]))
    await message.answer("\n\n".join(chunks), reply_markup=MASTER_WINDOWS_KB)


@router.message(MasterWindowsState.viewing, F.text == "➕ Добавить окно")
async def windows_add_pick_date(message: Message, state: FSMContext) -> None:
    today = date.today()
    rows = []
    for i in range(0, 31):
        d = today + timedelta(days=i)
        rows.append([KeyboardButton(text=f"{_format_date_iso(d.isoformat())} [d:{d.isoformat()}]")])
    rows.append([KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")])
    kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
    await state.set_state(MasterWindowsState.add_pick_date)
    await message.answer("Выберите дату для добавления окна:", reply_markup=kb)


@router.message(MasterWindowsState.add_pick_date)
async def windows_add_pick_time(message: Message, state: FSMContext, db) -> None:
    date_iso = _parse_date_token(message.text)
    if not date_iso:
        return

    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    settings = await q.get_booking_settings(master["id"])
    existing = await q.list_windows_by_date(master["id"], date_iso)
    await conn.close()

    step = settings["time_step_minutes"] if settings else 30
    first = settings["first_booking_time"] if settings else "10:00"
    last = settings["last_booking_time"] if settings else "19:00"
    slots = _time_slots(first, last, step)
    used = {w["start_time"] for w in existing}

    rows = [[KeyboardButton(text=t)] for t in slots if t not in used]
    if not rows:
        rows = [[KeyboardButton(text="(нет доступного времени)")]]
    rows.extend([[KeyboardButton(text="✅ Готово")], [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")]])
    kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

    await state.set_state(MasterWindowsState.add_pick_time)
    await state.update_data(window_date=date_iso)
    await message.answer(f"🕒 {_format_date_iso(date_iso)}\n\nВыберите время:", reply_markup=kb)


@router.message(MasterWindowsState.add_pick_time, F.text == "✅ Готово")
async def windows_add_done(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterWindowsState.add_pick_date)
    await message.answer("Готово. Выберите другую дату или вернитесь назад.")


@router.message(MasterWindowsState.add_pick_time)
async def windows_add_time_action(message: Message, state: FSMContext, db) -> None:
    if message.text in {"◀️ Назад", "🏠 Главное меню", "(нет доступного времени)"}:
        return
    try:
        time.fromisoformat(message.text)
    except ValueError:
        return

    data = await state.get_data()
    date_iso = data.get("window_date")
    if not date_iso:
        return

    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    settings = await q.get_booking_settings(master["id"])
    step = settings["time_step_minutes"] if settings else 30
    end_time = _add_minutes(message.text, step)
    await q.add_free_window(master["id"], date_iso, message.text, end_time)

    existing = await q.list_windows_by_date(master["id"], date_iso)
    await conn.close()

    slots = _time_slots(settings["first_booking_time"], settings["last_booking_time"], step) if settings else _time_slots("10:00", "19:00", 30)
    used = {w["start_time"] for w in existing}
    rows = [[KeyboardButton(text=t)] for t in slots if t not in used]
    if not rows:
        rows = [[KeyboardButton(text="(нет доступного времени)")]]
    rows.extend([[KeyboardButton(text="✅ Готово")], [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")]])
    kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

    await message.answer("✅ Окно добавлено", reply_markup=kb)


@router.message(MasterWindowsState.viewing, F.text == "🗑 Удалить окно")
async def windows_delete_pick_date(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    windows = await q.list_free_windows(master["id"])
    await conn.close()

    if not windows:
        await message.answer("Свободных окон для удаления нет.", reply_markup=MASTER_WINDOWS_KB)
        return

    by_date: dict[str, list[str]] = {}
    for w in windows:
        by_date.setdefault(w["window_date"], []).append(w["start_time"])

    rows = [[KeyboardButton(text=f"{_format_date_iso(d)} ({', '.join(times)}) [d:{d}]")] for d, times in by_date.items()]
    rows.extend([[KeyboardButton(text="✅ Готово")], [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")]])
    kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

    await state.set_state(MasterWindowsState.delete_pick_date)
    await message.answer("Выберите дату:", reply_markup=kb)


@router.message(MasterWindowsState.delete_pick_date, F.text == "✅ Готово")
async def windows_delete_date_done(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterWindowsState.viewing)
    await message.answer("Возврат в раздел свободных окон.", reply_markup=MASTER_WINDOWS_KB)


@router.message(MasterWindowsState.delete_pick_date)
async def windows_delete_pick_time(message: Message, state: FSMContext, db) -> None:
    date_iso = _parse_date_token(message.text)
    if not date_iso:
        return

    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    windows = await q.list_windows_by_date(master["id"], date_iso)
    await conn.close()

    if not windows:
        await message.answer("На этой дате окон нет.")
        return

    rows = [[KeyboardButton(text=f"{w['start_time']} [w:{w['id']}]")] for w in windows]
    rows.extend([[KeyboardButton(text="✅ Готово")], [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")]])
    kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

    await state.set_state(MasterWindowsState.delete_pick_time)
    await state.update_data(window_date=date_iso)
    await message.answer(f"🕒 {_format_date_iso(date_iso)}\n\nВыберите время для удаления:", reply_markup=kb)


@router.message(MasterWindowsState.delete_pick_time, F.text == "✅ Готово")
async def windows_delete_time_done(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    windows = await q.list_free_windows(master["id"])
    await conn.close()

    if not windows:
        await state.set_state(MasterWindowsState.viewing)
        await message.answer("Свободные окна закончились.", reply_markup=MASTER_WINDOWS_KB)
        return

    await state.set_state(MasterWindowsState.delete_pick_date)
    await message.answer("Выберите дату для продолжения удаления или нажмите ✅ Готово.")


@router.message(MasterWindowsState.delete_pick_time)
async def windows_delete_time_action(message: Message, state: FSMContext, db) -> None:
    window_id = _parse_window_token(message.text)
    if not window_id:
        return

    data = await state.get_data()
    date_iso = data.get("window_date")

    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    await q.delete_free_window(master["id"], window_id)
    windows = await q.list_windows_by_date(master["id"], date_iso)
    await conn.close()

    rows = [[KeyboardButton(text=f"{w['start_time']} [w:{w['id']}]")] for w in windows]
    if not rows:
        rows = [[KeyboardButton(text="(на этой дате окон больше нет)")]]
    rows.extend([[KeyboardButton(text="✅ Готово")], [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")]])
    kb = ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)

    await message.answer("❌ Окно удалено", reply_markup=kb)


@router.message(MasterWindowsState.viewing, F.text == "🗑 Удалить все окна")
async def windows_delete_all_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterWindowsState.delete_confirm_all)
    await message.answer(
        "⚠️ Вы уверены, что хотите удалить все свободные окна?",
        reply_markup=CONFIRM_DELETE_ALL_WINDOWS_KB,
    )


@router.message(MasterWindowsState.delete_confirm_all, F.text == "✅ Да, удалить все окна")
async def windows_delete_all_action(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    count = await q.delete_all_free_windows(master["id"])
    await conn.close()

    await state.set_state(MasterWindowsState.viewing)
    await message.answer(f"✅ Удалено окон: {count}", reply_markup=MASTER_WINDOWS_KB)


@router.message(MasterWindowsState.delete_confirm_all, F.text == "◀️ Отмена")
async def windows_delete_all_cancel(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterWindowsState.viewing)
    await message.answer("Удаление отменено.", reply_markup=MASTER_WINDOWS_KB)


# common back for booking sub-flows
@router.message(F.text == "◀️ Назад")
async def booking_back(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Возврат в раздел ✍️ Записать клиента.", reply_markup=MASTER_BOOKING_ENTRY_KB)


@router.message(F.text == "✍️ Записаться")
async def client_booking(message: Message) -> None:
    await message.answer("Раздел ✍️ Записаться: сначала выберите мастера или введите код мастера 🔑")
