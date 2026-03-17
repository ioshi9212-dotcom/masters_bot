from __future__ import annotations

from datetime import date
import json

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from database.queries import Queries
from keyboards.client import (
    CLIENT_EDIT_PROFILE_KB,
    CLIENT_MAIN_KB,
    CLIENT_MASTER_MODE_KB,
    CLIENT_NO_PROFILE_KB,
    CLIENT_PROFILE_KB,
    CLIENT_WRITE_MASTER_KB,
)
from keyboards.confirm import CLIENT_DELETE_PROFILE_CONFIRM_KB
from keyboards.master import MASTER_MAIN_KB
from states.client_states import ClientBookingState, ClientMastersState, ClientProfileState
from utils.formatters import format_client_profile

router = Router()


async def _client_ctx(message: Message, db):
    conn = await db.connect()
    q = Queries(conn)
    client = await q.get_client_by_telegram_id(message.from_user.id)
    return conn, q, client


async def _is_master_user(message: Message, db) -> bool:
    conn = await db.connect()
    q = Queries(conn)
    master = await q.get_master_by_telegram_id(message.from_user.id)
    await conn.close()
    return bool(master)


async def _client_menu_for_user(message: Message, db):
    return CLIENT_MASTER_MODE_KB if await _is_master_user(message, db) else CLIENT_MAIN_KB


def _master_row(master) -> str:
    professions = "Мастер"
    try:
        profs = json.loads(master["professions"] or "[]")
        if profs:
            professions = profs[0]
    except Exception:
        pass
    return f"👩‍🎨 {master['first_name']} — {professions} [m:{master['id']}]"


def _parse_token(text: str, prefix: str) -> int | None:
    token = f"[{prefix}:"
    if token not in text or not text.endswith("]"):
        return None
    try:
        return int(text.split(token)[-1].rstrip("]"))
    except ValueError:
        return None


def _parse_date_token(text: str) -> str | None:
    if "[d:" not in text or not text.endswith("]"):
        return None
    token = text.split("[d:")[-1].rstrip("]")
    try:
        date.fromisoformat(token)
        return token
    except ValueError:
        return None


def _masters_keyboard(masters) -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text=_master_row(m))] for m in masters]
    rows.append([KeyboardButton(text="🔑 Ввести код мастера")])
    rows.append([KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def _services_keyboard(services) -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text=f"💅 {s['name']} [s:{s['id']}]")] for s in services]
    rows.append([KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


@router.message(F.text == "👤 Клиент")
async def choose_client(message: Message, db) -> None:
    conn, q, client = await _client_ctx(message, db)
    await conn.close()

    if client:
        await message.answer(
            "Главное меню клиента 👇\n\n"
            "👤 Мой профиль — ваши данные для записи.\n"
            "✍️ Записаться — выбрать мастера и время.\n"
            "🕒 Посмотреть свободные окна — увидеть ближайшие окна.\n"
            "💅 Какой маникюр сделать? — идеи и вдохновение.\n"
            "👩‍🎨 Мои мастера — контакты, адрес и прайс.\n"
            "⏳ Лист ожидания — ждать уведомление об окне.",
            reply_markup=await _client_menu_for_user(message, db),
        )
        return

    await message.answer(
        "✨ Добро пожаловать в систему записи.\n\n"
        "Этот бот помогает:\n"
        "— быстро записаться к мастеру\n"
        "— получать напоминания о записи\n"
        "— не искать адрес и время записи\n"
        "— вставать в лист ожидания на свободное окно\n\n"
        "Основные разделы:\n\n"
        "👤 Мой профиль — ваши данные для записи.\n\n"
        "✍️ Записаться — запись на услугу.\n\n"
        "🕒 Свободные окна — ближайшие свободные окна мастера.\n\n"
        "👩‍🎨 Мои мастера — информация о мастере, адрес и прайс.\n\n"
        "⏳ Лист ожидания — уведомление, если появится свободное окно."
    )
    await message.answer(
        "Главное меню клиента 👇\n\n"
        "👤 Мой профиль — ваши данные для записи.\n"
        "✍️ Записаться — выбрать мастера и время.\n"
        "🕒 Посмотреть свободные окна — увидеть ближайшие окна.\n"
        "💅 Какой маникюр сделать? — идеи и вдохновение.\n"
        "👩‍🎨 Мои мастера — контакты, адрес и прайс.\n"
        "⏳ Лист ожидания — ждать уведомление об окне.",
        reply_markup=await _client_menu_for_user(message, db),
    )


@router.message(F.text == "🔁 Вернуться в режим мастера")
async def back_to_master_mode(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("Вы вернулись в режим мастера 👇", reply_markup=MASTER_MAIN_KB)


@router.message(F.text == "👤 Мой профиль")
async def my_profile(message: Message, db, state: FSMContext) -> None:
    conn, q, client = await _client_ctx(message, db)
    await conn.close()

    if client:
        await state.set_state(ClientProfileState.edit_pick_field)
        await message.answer(format_client_profile(client), reply_markup=CLIENT_PROFILE_KB)
    else:
        await state.clear()
        await message.answer(
            "⚠️ У вас ещё нет профиля. Создайте его, чтобы записываться к мастеру и получать уведомления.",
            reply_markup=CLIENT_NO_PROFILE_KB,
        )


@router.message(F.text == "➕ Создать профиль")
async def create_profile_start(message: Message, state: FSMContext) -> None:
    await state.set_state(ClientProfileState.create_first_name)
    await message.answer("Введите имя:")


@router.message(ClientProfileState.create_first_name)
async def create_profile_first_name(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text.strip())
    await state.set_state(ClientProfileState.create_last_name)
    await message.answer("Введите фамилию:")


@router.message(ClientProfileState.create_last_name)
async def create_profile_last_name(message: Message, state: FSMContext) -> None:
    await state.update_data(last_name=message.text.strip())
    await state.set_state(ClientProfileState.create_phone)
    await message.answer("Введите номер телефона:")


@router.message(ClientProfileState.create_phone)
async def create_profile_phone(message: Message, state: FSMContext) -> None:
    await state.update_data(phone=message.text.strip())
    await state.set_state(ClientProfileState.create_birth_date)
    await message.answer("Введите дату рождения (ДД.ММ):")


@router.message(ClientProfileState.create_birth_date)
async def create_profile_birth_date(message: Message, state: FSMContext, db) -> None:
    await state.update_data(birth_date=message.text.strip())
    data = await state.get_data()

    conn = await db.connect()
    q = Queries(conn)
    await q.upsert_client_profile(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        data={
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "phone": data["phone"],
            "birth_date": data["birth_date"],
        },
    )
    client = await q.get_client_by_telegram_id(message.from_user.id)
    await conn.close()

    await state.set_state(ClientProfileState.edit_pick_field)
    await message.answer("✅ Профиль создан.")
    await message.answer(format_client_profile(client), reply_markup=CLIENT_PROFILE_KB)


@router.message(F.text == "✏️ Редактировать профиль")
async def edit_profile_menu(message: Message, state: FSMContext) -> None:
    await state.set_state(ClientProfileState.edit_pick_field)
    await message.answer("Выберите поле для редактирования:", reply_markup=CLIENT_EDIT_PROFILE_KB)


@router.message(F.text == "🗑 Удалить профиль")
async def delete_profile_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(ClientProfileState.delete_confirm)
    await message.answer(
        "⚠️ Если вы удалите профиль, все ваши будущие записи к мастеру будут удалены.",
        reply_markup=CLIENT_DELETE_PROFILE_CONFIRM_KB,
    )


@router.message(ClientProfileState.delete_confirm, F.text == "✅ Удалить профиль")
async def delete_profile_confirm(message: Message, state: FSMContext, db) -> None:
    conn = await db.connect()
    q = Queries(conn)
    masters_to_notify = await q.delete_client_profile_with_future_appointments(message.from_user.id)
    await conn.close()

    for tg_id in masters_to_notify:
        try:
            await message.bot.send_message(
                tg_id,
                "📢 Клиент удалил свой профиль. Его будущие записи были автоматически удалены.",
            )
        except Exception:
            pass

    await state.clear()
    await message.answer(
        "📢 Ваш профиль удалён. Все ваши будущие записи к мастеру были отменены.",
        reply_markup=CLIENT_NO_PROFILE_KB,
    )


@router.message(ClientProfileState.delete_confirm, F.text == "◀️ Отмена")
async def delete_profile_cancel(message: Message, state: FSMContext, db) -> None:
    await state.clear()
    await message.answer("Удаление профиля отменено.", reply_markup=await _client_menu_for_user(message, db))


@router.message(ClientProfileState.edit_pick_field, F.text == "👤 Имя")
async def edit_name_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(ClientProfileState.edit_first_name)
    await message.answer("Введите новое имя:")


@router.message(ClientProfileState.edit_pick_field, F.text == "👤 Фамилия")
async def edit_last_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(ClientProfileState.edit_last_name)
    await message.answer("Введите новую фамилию:")


@router.message(ClientProfileState.edit_pick_field, F.text == "📱 Телефон")
async def edit_phone_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(ClientProfileState.edit_phone)
    await message.answer("Введите новый телефон:")


@router.message(ClientProfileState.edit_pick_field, F.text == "🎂 Дата рождения")
async def edit_birth_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(ClientProfileState.edit_birth_date)
    await message.answer("Введите новую дату рождения (ДД.ММ):")


async def _save_client_field(message: Message, db, field: str, value, state: FSMContext):
    conn, q, client = await _client_ctx(message, db)
    if not client:
        await conn.close()
        await state.clear()
        await message.answer("Сначала создайте профиль.", reply_markup=CLIENT_NO_PROFILE_KB)
        return

    data = {
        "first_name": client["first_name"],
        "last_name": client["last_name"],
        "phone": client["phone"],
        "birth_date": client["birth_date"],
    }
    data[field] = value
    await q.upsert_client_profile(message.from_user.id, message.from_user.username, data)
    updated = await q.get_client_by_telegram_id(message.from_user.id)
    await conn.close()

    await state.set_state(ClientProfileState.edit_pick_field)
    await message.answer(format_client_profile(updated), reply_markup=CLIENT_PROFILE_KB)


@router.message(ClientProfileState.edit_first_name)
async def edit_name_save(message: Message, state: FSMContext, db) -> None:
    await _save_client_field(message, db, "first_name", message.text.strip(), state)


@router.message(ClientProfileState.edit_last_name)
async def edit_last_save(message: Message, state: FSMContext, db) -> None:
    await _save_client_field(message, db, "last_name", message.text.strip(), state)


@router.message(ClientProfileState.edit_phone)
async def edit_phone_save(message: Message, state: FSMContext, db) -> None:
    await _save_client_field(message, db, "phone", message.text.strip(), state)


@router.message(ClientProfileState.edit_birth_date)
async def edit_birth_save(message: Message, state: FSMContext, db) -> None:
    await _save_client_field(message, db, "birth_date", message.text.strip(), state)


@router.message(F.text == "✍️ Записаться")
async def client_booking_start(message: Message, state: FSMContext, db) -> None:
    conn, q, client = await _client_ctx(message, db)
    if not client:
        await conn.close()
        await message.answer("Сначала создайте профиль в разделе 👤 Мой профиль.", reply_markup=CLIENT_NO_PROFILE_KB)
        return

    masters = await q.list_client_masters(client["id"])
    await conn.close()

    await state.set_state(ClientBookingState.pick_master)
    if not masters:
        await message.answer(
            "⚠️ У вас пока нет мастеров. Введите код мастера.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="🔑 Ввести код мастера")],
                    [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")],
                ],
                resize_keyboard=True,
            ),
        )
        return

    await message.answer("Выберите мастера:", reply_markup=_masters_keyboard(masters))


@router.message(ClientBookingState.pick_master, F.text == "🔑 Ввести код мастера")
async def enter_master_code_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(ClientBookingState.enter_master_code)
    await message.answer("Введите код мастера, например master5560:")


@router.message(ClientBookingState.enter_master_code)
async def enter_master_code_save(message: Message, state: FSMContext, db) -> None:
    code = message.text.strip()
    conn, q, client = await _client_ctx(message, db)
    if not client:
        await conn.close()
        await message.answer("Сначала создайте профиль.")
        return

    master = await q.get_master_by_code(code)
    if not master:
        await conn.close()
        await message.answer("⚠️ Мастер с таким кодом не найден.")
        return

    linked = await q.link_client_to_master(client["id"], master["id"])
    masters = await q.list_client_masters(client["id"])
    await conn.close()

    await state.set_state(ClientBookingState.pick_master)
    if not linked:
        await message.answer(
            f"ℹ️ Этот мастер уже есть в вашем списке.\n\n👩‍🎨 {master['first_name']}",
            reply_markup=_masters_keyboard(masters),
        )
    else:
        await message.answer("✅ Мастер добавлен в ваш список.", reply_markup=_masters_keyboard(masters))


@router.message(ClientBookingState.pick_master)
async def pick_master(message: Message, state: FSMContext, db) -> None:
    master_id = _parse_token(message.text, "m")
    if not master_id:
        return

    conn = await db.connect()
    q = Queries(conn)
    services = await q.list_master_active_services(master_id)
    await conn.close()

    if not services:
        await message.answer("⚠️ У мастера пока нет доступных услуг.")
        return

    await state.update_data(book_master_id=master_id)
    await state.set_state(ClientBookingState.pick_service)
    await message.answer("Выберите услугу:", reply_markup=_services_keyboard(services))


@router.message(ClientBookingState.pick_service)
async def pick_service(message: Message, state: FSMContext, db) -> None:
    service_id = _parse_token(message.text, "s")
    if not service_id:
        return

    data = await state.get_data()
    master_id = data.get("book_master_id")
    if not master_id:
        return

    conn = await db.connect()
    q = Queries(conn)
    windows = await q.list_available_windows_for_service(master_id, service_id)
    await conn.close()

    if not windows:
        await message.answer(
            "⚠️ Сейчас нет свободных окон для выбранной услуги.\n\n"
            "Кнопки: ⏳ Лист ожидания / ✉️ Написать мастеру",
        )
        return

    by_date = {}
    for w in windows:
        by_date.setdefault(w["window_date"], []).append((w["id"], w["start_time"]))

    rows = []
    for d, times in by_date.items():
        t = ", ".join(i[1] for i in times)
        rows.append([KeyboardButton(text=f"{d} ({t}) [d:{d}]")])
    rows.append([KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")])

    await state.update_data(book_service_id=service_id)
    await state.set_state(ClientBookingState.pick_date)
    await message.answer("Выберите дату:", reply_markup=ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True))


@router.message(ClientBookingState.pick_date)
async def pick_date(message: Message, state: FSMContext, db) -> None:
    date_iso = _parse_date_token(message.text)
    if not date_iso:
        return

    data = await state.get_data()
    master_id = data.get("book_master_id")
    service_id = data.get("book_service_id")
    if not master_id or not service_id:
        return

    conn = await db.connect()
    q = Queries(conn)
    windows = await q.list_available_windows_for_service(master_id, service_id)
    await conn.close()

    rows = []
    for w in windows:
        if w["window_date"] == date_iso:
            rows.append([KeyboardButton(text=f"{w['start_time']} [w:{w['id']}]")])
    rows.append([KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")])

    await state.set_state(ClientBookingState.pick_time)
    await message.answer("Выберите время:", reply_markup=ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True))


@router.message(ClientBookingState.pick_time)
async def pick_time(message: Message, state: FSMContext, db) -> None:
    window_id = _parse_token(message.text, "w")
    if not window_id:
        return

    data = await state.get_data()
    master_id = data.get("book_master_id")
    service_id = data.get("book_service_id")

    conn, q, client = await _client_ctx(message, db)
    if not client:
        await conn.close()
        return

    ap = await q.create_client_appointment_from_window(master_id, client["id"], service_id, window_id)
    await conn.close()

    if not ap:
        await message.answer("⚠️ Не удалось создать запись. Возможно, окно уже занято.")
        return

    await state.clear()
    await message.answer(
        "✨ Ваша запись добавлена\n\n"
        f"📅 {ap['appointment_date']}\n"
        f"🕒 {ap['start_time']}\n"
        f"💅 {ap['service_name'] or 'Услуга'}",
        reply_markup=await _client_menu_for_user(message, db),
    )

    if ap["master_telegram_id"]:
        try:
            await message.bot.send_message(
                ap["master_telegram_id"],
                f"📢 Новый клиент записался: {ap['appointment_date']} {ap['start_time']}",
            )
        except Exception:
            pass


@router.message(F.text == "👩‍🎨 Мои мастера")
async def my_masters(message: Message, state: FSMContext, db) -> None:
    conn, q, client = await _client_ctx(message, db)
    if not client:
        await conn.close()
        await message.answer("Сначала создайте профиль.", reply_markup=CLIENT_NO_PROFILE_KB)
        return

    masters = await q.list_client_masters(client["id"])
    await conn.close()
    if not masters:
        await message.answer("У вас пока нет мастеров.")
        return

    await state.set_state(ClientMastersState.pick_master)
    await message.answer("Выберите мастера:", reply_markup=_masters_keyboard(masters))


@router.message(ClientMastersState.pick_master)
async def my_masters_pick(message: Message, state: FSMContext, db) -> None:
    master_id = _parse_token(message.text, "m")
    if not master_id:
        if message.text == "✉️ Написать мастеру":
            data = await state.get_data()
            username = data.get("selected_master_username")
            phone = data.get("selected_master_phone")
            if username:
                await message.answer(f"Откройте чат: https://t.me/{username}")
            else:
                await message.answer(
                    "⚠️ У мастера не указан Telegram username. Свяжитесь с мастером по номеру телефона."
                    + (f"\n{phone}" if phone else "")
                )
            return
        return

    conn = await db.connect()
    q = Queries(conn)
    service_list = await q.list_master_active_services(master_id)
    cur = await q.conn.execute("SELECT * FROM masters WHERE id = ?", (master_id,))
    master = await cur.fetchone()
    await conn.close()
    if not master:
        return

    price_lines = [f"• {s['name']} — {s['price']}" for s in service_list] or ["—"]
    await state.update_data(
        selected_master_username=master["username"],
        selected_master_phone=master["phone"],
    )
    await message.answer(
        "👩‍🎨 Мастер\n"
        f"{master['first_name']} {master['last_name'] or ''}\n\n"
        f"📍 Адрес\n{master['work_address'] or '—'}\n\n"
        f"📱 Телефон\n{master['phone'] or '—'}\n\n"
        "💰 Прайс\n" + "\n".join(price_lines),
        reply_markup=CLIENT_WRITE_MASTER_KB,
    )


@router.message(F.text == "🕒 Посмотреть свободные окна")
async def see_free_windows(message: Message, db) -> None:
    conn, q, client = await _client_ctx(message, db)
    if not client:
        await conn.close()
        await message.answer("Сначала создайте профиль.")
        return

    masters = await q.list_client_masters(client["id"])
    if not masters:
        await conn.close()
        await message.answer("⚠️ Извините, свободных окон пока нет.")
        return

    chunks = []
    for m in masters:
        windows = await q.list_free_windows(m["id"])
        if not windows:
            continue
        by_date = {}
        for w in windows:
            by_date.setdefault(w["window_date"], []).append(w["start_time"])
        for d, times in by_date.items():
            chunks.append(f"👩‍🎨 {m['first_name']}\n🕒 {d}: {', '.join(times)}")
    await conn.close()

    if not chunks:
        await message.answer("⚠️ Извините, свободных окон пока нет.\n\nКнопки: ⏳ Лист ожидания / ✉️ Написать мастеру")
    else:
        await message.answer("\n\n".join(chunks))


@router.message(F.text == "💅 Какой маникюр сделать?")
async def manicure_ideas(message: Message) -> None:
    await message.answer(
        "💅 Здесь будут идеи маникюра и подбор по сезону/стилю.\n"
        "Пока раздел в базовой версии — скоро расширим примерами."
    )


@router.message(F.text == "⏳ Лист ожидания")
async def client_waitlist_info(message: Message) -> None:
    await message.answer(
        "⏳ Лист ожидания\n\n"
        "📅 Ближайшие окна — уведомление на первое освободившееся время.\n"
        "🗓 Определенная дата — уведомление по выбранным датам."
    )


@router.message(F.text == "◀️ Назад")
async def client_back(message: Message, state: FSMContext, db) -> None:
    current = await state.get_state()
    if current and current.startswith("Client"):
        await state.clear()
        await message.answer("Главное меню клиента 👇", reply_markup=await _client_menu_for_user(message, db))
