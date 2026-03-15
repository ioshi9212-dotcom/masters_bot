from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from database.queries import Queries
from keyboards.reply import (
    CONFIRM_DELETE_CLIENT_KB,
    MASTER_BOOKING_ENTRY_KB,
    MASTER_CLIENTS_TOP_KB,
    SKIP_BACK_HOME_KB,
)
from states.master_states import MasterClientCreateState, MasterClientDeleteState, MasterClientEditState, MasterClientsState

router = Router()


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
    rows = [
        [KeyboardButton(text="✏️ Редактировать клиента"), KeyboardButton(text="🗑 Удалить клиента")],
    ]
    for client in clients:
        rows.append([KeyboardButton(text=_client_btn_text(client))])
    rows.append([KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


async def _master_or_error(message: Message, db):
    conn = await db.connect()
    q = Queries(conn)
    master = await q.get_master_by_telegram_id(message.from_user.id)
    if not master:
        await conn.close()
        await message.answer("Сначала выберите роль мастера через /start")
        return None, None, None
    return conn, q, master


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
    client_id = data["edit_client_id"]

    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    await q.update_manual_client(
        client_id,
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
    client_id = data["delete_client_id"]

    conn, q, master = await _master_or_error(message, db)
    if not master:
        return
    await q.delete_client_from_master(master["id"], client_id)
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



@router.message(F.text == "✍️ Записаться")
async def client_booking(message: Message) -> None:
    await message.answer("Раздел ✍️ Записаться: сначала выберите мастера или введите код мастера 🔑")
