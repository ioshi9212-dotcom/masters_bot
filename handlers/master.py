from __future__ import annotations

import json

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from database.queries import Queries
from keyboards.common import PROFESSION_DONE_KB, YES_SKIP_KB
from keyboards.confirm import MASTER_CONFIRM_DELETE_SERVICE_KB, MASTER_DELETE_CONFIRM_KB
from keyboards.master import (
    MASTER_CABINET_KB,
    MASTER_EXISTS_KB,
    MASTER_MAIN_KB,
    MASTER_PROFILE_EDIT_KB,
    MASTER_PROFILE_VIEW_KB,
    MASTER_SERVICES_LIST_KB,
    MASTER_SERVICES_KB,
    MASTER_SETTINGS_KB,
    MASTER_STATS_PERIOD_KB,
)
from states.master_states import (
    MasterCabinetState,
    MasterDeleteProfileState,
    MasterRegistrationState,
    ServiceCreateState,
    ServiceEditPriceState,
)
from utils.dates import calculate_experience_text
from utils.formatters import format_master_profile

router = Router()


def _service_btn(service) -> str:
    return f"{service['name']} [s:{service['id']}]"


def _parse_service_id(text: str) -> int | None:
    if "[s:" not in text or not text.endswith("]"):
        return None
    try:
        return int(text.split("[s:")[-1].rstrip("]"))
    except ValueError:
        return None


def _services_pick_keyboard(services) -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text=_service_btn(s))] for s in services]
    rows.append([KeyboardButton(text="◀️ Назад"), KeyboardButton(text="🏠 Главное меню")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


async def _master_ctx(message: Message, db):
    conn = await db.connect()
    q = Queries(conn)
    master = await q.get_master_by_telegram_id(message.from_user.id)
    if not master:
        await conn.close()
        await message.answer("Сначала выберите роль мастера через /start")
        return None, None, None
    return conn, q, master


def _format_master_full_profile(master) -> str:
    professions = ", ".join(json.loads(master["professions"])) if master["professions"] else "—"
    return (
        "👤 Профиль мастера\n\n"
        f"Имя: {master['first_name']}\n"
        f"Фамилия: {master['last_name'] or '—'}\n"
        f"Профессии: {professions}\n"
        f"Дата рождения: {master['birth_date'] or '—'}\n"
        f"Начало работы: {master['work_start_month'] or '—'}.{master['work_start_year'] or '—'}\n"
        f"Стаж: {master['work_experience_text'] or '—'}\n"
        f"Телефон: {master['phone'] or '—'}\n"
        f"Адрес: {master['work_address'] or '—'}"
    )


@router.message(F.text == "👩‍🎨 Мастер")
async def choose_master(message: Message, state: FSMContext, db) -> None:
    # Сбрасываем незавершённые FSM-сценарии перед выбором роли.
    await state.clear()

    conn = await db.connect()
    q = Queries(conn)
    master = await q.get_master_by_telegram_id(message.from_user.id)
    await conn.close()

    if master:
        await message.answer(
            "✨ Добро пожаловать в систему записи.\n\n"
            "Этот бот помогает мастеру:\n"
            "— вести запись клиентов\n"
            "— автоматически напоминать о записях\n"
            "— хранить базу клиентов\n"
            "— видеть статистику работы"
        )
        await message.answer(
            "✅ Вы зарегистрированы как мастер.\n\n"
            "Вы хотите оставить этот профиль или удалить его и создать новый?",
            reply_markup=MASTER_EXISTS_KB,
        )
        return

    await message.answer(
        "✨ Добро пожаловать в систему записи.\n\n"
        "Этот бот помогает мастеру:\n"
        "— вести запись клиентов\n"
        "— автоматически напоминать о записях\n"
        "— хранить базу клиентов\n"
        "— видеть статистику работы"
    )
    await state.set_state(MasterRegistrationState.first_name)
    await message.answer("Введите ваше имя:")


@router.message(F.text == "✅ Оставить профиль")
async def keep_master_profile(message: Message) -> None:
    await message.answer(
        "Главное меню мастера открыто 👇\n\n"
        "✍️ Записать клиента — добавить запись вручную.\n"
        "📅 Посмотреть записи — список будущих записей.\n"
        "🕒 Свободные окна — управлять окнами для онлайн-записи.\n"
        "⏳ Лист ожидания — клиенты, которые ждут окно.\n"
        "👤 Кабинет мастера — профиль, услуги, настройки, статистика.\n"
        "👤 Меню клиента — перейти в клиентское меню и проверить сценарий записи.",
        reply_markup=MASTER_MAIN_KB
    )


@router.message(F.text == "🗑 Удалить и создать новый")
async def delete_master_profile(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterDeleteProfileState.confirm)
    await message.answer(
        "⚠️ Если вы удалите профиль мастера, будут полностью удалены все ваши данные:\n\n"
        "• профиль мастера\n"
        "• услуги\n"
        "• записи\n"
        "• клиенты\n"
        "• свободные окна\n"
        "• лист ожидания\n"
        "• статистика\n"
        "• настройки",
        reply_markup=MASTER_DELETE_CONFIRM_KB,
    )


@router.message(MasterDeleteProfileState.confirm, F.text == "✅ Да, удалить")
async def confirm_delete_master_profile(message: Message, state: FSMContext, db) -> None:
    conn = await db.connect()
    q = Queries(conn)
    await q.deactivate_master_profile(message.from_user.id)
    await conn.close()

    await state.clear()
    await state.set_state(MasterRegistrationState.first_name)
    await message.answer("Старый профиль удалён. Введите имя для нового профиля мастера:")


@router.message(MasterDeleteProfileState.confirm, F.text == "◀️ Отмена")
async def cancel_delete_master_profile(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Удаление отменено.\n\n"
        "✅ Вы зарегистрированы как мастер.\n\n"
        "Вы хотите оставить этот профиль или удалить его и создать новый?",
        reply_markup=MASTER_EXISTS_KB,
    )


@router.message(MasterRegistrationState.first_name)
async def m_first_name(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text.strip())
    await state.set_state(MasterRegistrationState.last_name)
    await message.answer("Введите фамилию или нажмите ⏭ Пропустить", reply_markup=YES_SKIP_KB)


@router.message(MasterRegistrationState.last_name)
async def m_last_name(message: Message, state: FSMContext) -> None:
    last_name = None if message.text == "⏭ Пропустить" else message.text.strip()
    await state.update_data(last_name=last_name)
    await state.set_state(MasterRegistrationState.birth_date)
    await message.answer("Введите дату рождения в формате ДД.ММ")


@router.message(MasterRegistrationState.profession)
async def m_profession(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    professions = data.get("professions", [])

    text = message.text.strip()
    if text == "✅ Готово":
        if not professions:
            await message.answer("Добавьте хотя бы одну профессию.")
            return
        await state.set_state(MasterRegistrationState.work_start)
        await message.answer(
            "Введите месяц и год начала работы в формате ММ.ГГГГ.\n"
            "Если укажете этот пункт, клиенты будут видеть начало вашего стажа.\n"
            "Или нажмите ⏭ Пропустить.",
            reply_markup=YES_SKIP_KB,
        )
        return

    professions.append(text)
    await state.update_data(professions=professions)
    await message.answer("Профессия добавлена. Добавьте ещё или нажмите ✅ Готово", reply_markup=PROFESSION_DONE_KB)


@router.message(MasterRegistrationState.birth_date)
async def m_birth_date(message: Message, state: FSMContext) -> None:
    await state.update_data(birth_date=message.text.strip(), professions=[])
    await state.set_state(MasterRegistrationState.profession)
    await message.answer("Введите профессию (например, Мастер маникюра):", reply_markup=PROFESSION_DONE_KB)


@router.message(MasterRegistrationState.work_start)
async def m_work_start(message: Message, state: FSMContext) -> None:
    if message.text == "⏭ Пропустить":
        await state.update_data(
            work_start_month=None,
            work_start_year=None,
            work_experience_text=None,
        )
        await state.set_state(MasterRegistrationState.phone)
        await message.answer(
            "Введите номер телефона (обязательно).\n"
            "Этот номер будет виден клиентам для связи."
        )
        return

    try:
        month_str, year_str = message.text.strip().split(".")
        month, year = int(month_str), int(year_str)
        if month < 1 or month > 12:
            raise ValueError
    except ValueError:
        await message.answer("Неверный формат. Пример: 05.2021")
        return

    await state.update_data(
        work_start_month=month,
        work_start_year=year,
        work_experience_text=calculate_experience_text(month, year),
    )
    await state.set_state(MasterRegistrationState.phone)
    await message.answer(
        "Введите номер телефона (обязательно).\n"
        "Этот номер будет виден клиентам для связи."
    )


@router.message(MasterRegistrationState.phone)
async def m_phone(message: Message, state: FSMContext) -> None:
    await state.update_data(phone=message.text.strip())
    await state.set_state(MasterRegistrationState.address)
    await message.answer(
        "📍 Введите адрес работы.\n\n"
        "Укажите:\n— адрес\n— номер кабинета\n— этаж\n— или любую дополнительную информацию, как вас найти."
    )


@router.message(MasterRegistrationState.address)
async def m_address(message: Message, state: FSMContext, db) -> None:
    await state.update_data(work_address=message.text.strip())
    data = await state.get_data()

    conn = await db.connect()
    q = Queries(conn)
    await q.create_master(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        data=data,
    )
    master = await q.get_master_by_telegram_id(message.from_user.id)
    await conn.close()

    await state.clear()
    await message.answer(
        "✨ Добро пожаловать в систему записи. Профиль мастера сохранён.\n\n"
        f"{format_master_profile(master)}",
        reply_markup=MASTER_MAIN_KB,
    )




@router.message(F.text == "👤 Меню клиента")
async def switch_to_client_mode(message: Message, state: FSMContext, db) -> None:
    from keyboards.client import CLIENT_MASTER_MODE_KB

    await state.clear()
    await message.answer(
        "Меню клиента открыто 👇\n\n"
        "Здесь вы можете проверить клиентский сценарий записи и вернуться кнопкой «🔁 Вернуться в режим мастера».",
        reply_markup=CLIENT_MASTER_MODE_KB,
    )

@router.message(F.text == "👤 Кабинет мастера")
async def master_cabinet(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterCabinetState.menu)
    await message.answer(
        "👤 Кабинет мастера\n\n"
        "💰 Прайс — посмотреть услуги и изменить стоимость.\n"
        "🛠 Услуги — добавить, посмотреть, удалить услугу и изменить стоимость.\n"
        "👤 Профиль мастера — ваши данные и редактирование.\n"
        "⚙️ Настройки записи — шаг, время и ограничения записи.\n"
        "📊 Статистика — показатели за период.",
        reply_markup=MASTER_CABINET_KB,
    )


@router.message(MasterCabinetState.menu, F.text == "💰 Прайс")
async def cabinet_price(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    services = await q.list_master_services(master["id"], active_only=True)
    await conn.close()

    if not services:
        await message.answer("Список услуг пуст. Сначала добавьте услуги в разделе ✂️ Услуги.")
        return

    lines = [
        f"• {s['name']}\nДлительность: {s['duration_minutes']} мин\nСтоимость: {s['price']}\nОписание: {s['description'] or '—'}"
        for s in services
    ]
    await state.set_state(MasterCabinetState.price_edit_pick_service)
    await message.answer(
        "💰 Прайс\n\n" + "\n\n".join(lines) + "\n\nВыберите услугу для изменения стоимости:",
        reply_markup=_services_pick_keyboard(services),
    )


@router.message(MasterCabinetState.price_edit_pick_service)
async def cabinet_price_pick(message: Message, state: FSMContext, db) -> None:
    sid = _parse_service_id(message.text)
    if not sid:
        return
    await state.update_data(price_service_id=sid)
    await state.set_state(MasterCabinetState.price_edit_enter_value)
    await message.answer("Введите новую стоимость:")


@router.message(MasterCabinetState.price_edit_enter_value)
async def cabinet_price_update(message: Message, state: FSMContext, db) -> None:
    try:
        price = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите стоимость числом.")
        return

    data = await state.get_data()
    sid = data.get("price_service_id")
    if not sid:
        return

    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await q.update_service_price(master["id"], sid, price)
    services = await q.list_master_services(master["id"], active_only=True)
    await conn.close()

    await state.set_state(MasterCabinetState.price_edit_pick_service)
    await message.answer("✅ Стоимость обновлена.", reply_markup=_services_pick_keyboard(services) if services else MASTER_CABINET_KB)


@router.message(MasterCabinetState.menu, F.text.in_({"🛠 Услуги", "✂️ Услуги"}))
async def cabinet_services_menu(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await conn.close()
    await state.set_state(MasterCabinetState.services_menu)
    await message.answer("🛠 Меню услуг\n\nВыберите нужное действие:", reply_markup=MASTER_SERVICES_KB)


@router.message(MasterCabinetState.services_menu, F.text == "➕ Добавить услугу")
async def service_add_start(message: Message, state: FSMContext) -> None:
    await state.set_state(ServiceCreateState.name)
    await message.answer("Введите название услуги:")


@router.message(ServiceCreateState.name)
async def service_add_name(message: Message, state: FSMContext) -> None:
    await state.update_data(service_name=message.text.strip())
    await state.set_state(ServiceCreateState.description)
    await message.answer("Введите описание услуги:")


@router.message(ServiceCreateState.description)
async def service_add_desc(message: Message, state: FSMContext) -> None:
    await state.update_data(service_description=message.text.strip())
    await state.set_state(ServiceCreateState.duration)
    await message.answer(
        "Введите длительность услуги в минутах. Например: 30, 60, 90, 120\n"
        "Эта длительность влияет на доступные окна для онлайн-записи клиентов: "
        "показываются только те окна, куда услуга полностью помещается."
    )


@router.message(ServiceCreateState.duration)
async def service_add_duration(message: Message, state: FSMContext) -> None:
    try:
        duration = int(message.text)
        if duration <= 0:
            raise ValueError
    except ValueError:
        await message.answer(
            "Введите длительность услуги в минутах. Например: 30, 60, 90, 120\n"
            "Эта длительность влияет на доступные окна для онлайн-записи клиентов."
        )
        return
    await state.update_data(service_duration=duration)
    await state.set_state(ServiceCreateState.price)
    await message.answer("Введите стоимость услуги числом. Например: 1500")


@router.message(ServiceCreateState.price)
async def service_add_price(message: Message, state: FSMContext, db) -> None:
    try:
        price = float(message.text.replace(",", "."))
        if price < 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите стоимость услуги числом. Например: 1500")
        return

    data = await state.get_data()
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await q.create_service(master["id"], data["service_name"], data["service_description"], data["service_duration"], price)
    await conn.close()

    services = await q.list_master_services(master["id"], active_only=True)
    await state.set_state(MasterCabinetState.services_menu)
    if services:
        lines = [
            f"{idx}. {s['name']}\n⏱ {s['duration_minutes']} мин\n💰 {s['price']} ₽\n📝 {s['description'] or '—'}"
            for idx, s in enumerate(services, start=1)
        ]
        await message.answer("✅ Услуга добавлена.\n\n🛠 Ваши услуги\n\n" + "\n\n".join(lines), reply_markup=MASTER_SERVICES_LIST_KB)
    else:
        await message.answer("✅ Услуга добавлена.", reply_markup=MASTER_SERVICES_KB)


@router.message(MasterCabinetState.services_menu, F.text == "📋 Мои услуги")
async def service_list(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    services = await q.list_master_services(master["id"], active_only=True)
    await conn.close()

    await state.set_state(MasterCabinetState.services_menu)
    if not services:
        await message.answer("⚠️ У вас пока нет услуг.", reply_markup=MASTER_SERVICES_KB)
        return

    lines = [
        f"{idx}. {s['name']}\n⏱ {s['duration_minutes']} мин\n💰 {s['price']} ₽\n📝 {s['description'] or '—'}"
        for idx, s in enumerate(services, start=1)
    ]
    await message.answer("🛠 Ваши услуги\n\n" + "\n\n".join(lines), reply_markup=MASTER_SERVICES_LIST_KB)


@router.message(MasterCabinetState.services_menu, F.text == "✏️ Редактировать стоимость")
async def service_price_pick(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    services = await q.list_master_services(master["id"], active_only=True)
    await conn.close()

    if not services:
        await message.answer("⚠️ У вас пока нет услуг.", reply_markup=MASTER_SERVICES_KB)
        return

    await state.set_state(ServiceEditPriceState.pick_service)
    await message.answer("Выберите услугу:", reply_markup=_services_pick_keyboard(services))


@router.message(ServiceEditPriceState.pick_service)
async def service_price_pick_service(message: Message, state: FSMContext) -> None:
    sid = _parse_service_id(message.text)
    if not sid:
        return
    await state.update_data(price_service_id=sid)
    await state.set_state(ServiceEditPriceState.new_price)
    await message.answer("Введите новую стоимость:")


@router.message(ServiceEditPriceState.new_price)
async def service_price_update(message: Message, state: FSMContext, db) -> None:
    try:
        price = float(message.text.replace(",", "."))
        if price < 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите новую стоимость:")
        return

    data = await state.get_data()
    sid = data.get("price_service_id")
    if not sid:
        return

    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await q.update_service_price(master["id"], sid, price)
    await conn.close()

    await state.set_state(MasterCabinetState.services_menu)
    await message.answer("✅ Стоимость услуги обновлена.", reply_markup=MASTER_SERVICES_KB)


@router.message(MasterCabinetState.services_menu, F.text == "🗑 Удалить услугу")
async def service_delete_pick(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    services = await q.list_master_services(master["id"], active_only=False)
    await conn.close()
    if not services:
        await message.answer("Нет услуг для удаления.")
        return

    await state.set_state(MasterCabinetState.service_delete_pick)
    await message.answer("Выберите услугу:", reply_markup=_services_pick_keyboard(services))


@router.message(MasterCabinetState.service_delete_pick)
async def service_delete_confirm_prompt(message: Message, state: FSMContext) -> None:
    sid = _parse_service_id(message.text)
    if not sid:
        return
    await state.update_data(delete_service_id=sid)
    await state.set_state(MasterCabinetState.service_delete_confirm)
    await message.answer("⚠️ Вы уверены, что хотите удалить услугу?", reply_markup=MASTER_CONFIRM_DELETE_SERVICE_KB)


@router.message(MasterCabinetState.service_delete_confirm, F.text == "✅ Да, удалить")
async def service_delete_confirm(message: Message, state: FSMContext, db) -> None:
    data = await state.get_data()
    sid = data.get("delete_service_id")
    if not sid:
        return

    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    action = await q.delete_or_deactivate_service(master["id"], sid)
    await conn.close()

    await state.set_state(MasterCabinetState.services_menu)
    if action == "deactivated":
        await message.answer(
            "ℹ️ По этой услуге есть записи. Услуга скрыта для новых записей и останется в старых до их завершения.",
            reply_markup=MASTER_SERVICES_KB,
        )
    else:
        await message.answer("✅ Услуга удалена.", reply_markup=MASTER_SERVICES_KB)


@router.message(MasterCabinetState.service_delete_confirm, F.text == "❌ Отмена")
async def service_delete_cancel(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterCabinetState.services_menu)
    await message.answer("Удаление отменено.", reply_markup=MASTER_SERVICES_KB)


@router.message(MasterCabinetState.menu, F.text == "👤 Профиль мастера")
async def profile_view(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await conn.close()
    await state.set_state(MasterCabinetState.profile_edit_menu)
    await message.answer(_format_master_full_profile(master), reply_markup=MASTER_PROFILE_VIEW_KB)


@router.message(MasterCabinetState.profile_edit_menu, F.text == "✏️ Редактировать профиль")
async def profile_edit_menu(message: Message) -> None:
    await message.answer("Выберите поле для редактирования:", reply_markup=MASTER_PROFILE_EDIT_KB)


@router.message(MasterCabinetState.profile_edit_menu, F.text == "👤 Имя")
async def profile_edit_name_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterCabinetState.profile_edit_name)
    await message.answer("Введите новое имя:")


@router.message(MasterCabinetState.profile_edit_name)
async def profile_edit_name_save(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await q.update_master_field(master["id"], "first_name", message.text.strip())
    updated = await q.get_master_by_telegram_id(message.from_user.id)
    await conn.close()
    await state.set_state(MasterCabinetState.profile_edit_menu)
    await message.answer(_format_master_full_profile(updated), reply_markup=MASTER_PROFILE_VIEW_KB)


@router.message(MasterCabinetState.profile_edit_menu, F.text == "👤 Фамилия")
async def profile_edit_last_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterCabinetState.profile_edit_last_name)
    await message.answer("Введите новую фамилию или ⏭ Пропустить", reply_markup=YES_SKIP_KB)


@router.message(MasterCabinetState.profile_edit_last_name)
async def profile_edit_last_save(message: Message, state: FSMContext, db) -> None:
    value = None if message.text == "⏭ Пропустить" else message.text.strip()
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await q.update_master_field(master["id"], "last_name", value)
    updated = await q.get_master_by_telegram_id(message.from_user.id)
    await conn.close()
    await state.set_state(MasterCabinetState.profile_edit_menu)
    await message.answer(_format_master_full_profile(updated), reply_markup=MASTER_PROFILE_VIEW_KB)


@router.message(MasterCabinetState.profile_edit_menu, F.text == "📱 Телефон")
async def profile_edit_phone_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterCabinetState.profile_edit_phone)
    await message.answer("Введите новый телефон:")


@router.message(MasterCabinetState.profile_edit_phone)
async def profile_edit_phone_save(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await q.update_master_field(master["id"], "phone", message.text.strip())
    updated = await q.get_master_by_telegram_id(message.from_user.id)
    await conn.close()
    await state.set_state(MasterCabinetState.profile_edit_menu)
    await message.answer(_format_master_full_profile(updated), reply_markup=MASTER_PROFILE_VIEW_KB)


@router.message(MasterCabinetState.profile_edit_menu, F.text == "🎂 Дата рождения")
async def profile_edit_birth_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterCabinetState.profile_edit_birth_date)
    await message.answer("Введите дату рождения ДД.ММ:")


@router.message(MasterCabinetState.profile_edit_birth_date)
async def profile_edit_birth_save(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await q.update_master_field(master["id"], "birth_date", message.text.strip())
    updated = await q.get_master_by_telegram_id(message.from_user.id)
    await conn.close()
    await state.set_state(MasterCabinetState.profile_edit_menu)
    await message.answer(_format_master_full_profile(updated), reply_markup=MASTER_PROFILE_VIEW_KB)


@router.message(MasterCabinetState.profile_edit_menu, F.text == "📅 Начало работы в сфере")
async def profile_edit_work_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterCabinetState.profile_edit_work_start)
    await message.answer("Введите ММ.ГГГГ, например 05.2021:")


@router.message(MasterCabinetState.profile_edit_work_start)
async def profile_edit_work_save(message: Message, state: FSMContext, db) -> None:
    try:
        month, year = map(int, message.text.split("."))
    except ValueError:
        await message.answer("Неверный формат. Пример: 05.2021")
        return

    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await q.update_master_field(master["id"], "work_start_month", month)
    await q.update_master_field(master["id"], "work_start_year", year)
    await q.update_master_field(master["id"], "work_experience_text", calculate_experience_text(month, year))
    updated = await q.get_master_by_telegram_id(message.from_user.id)
    await conn.close()
    await state.set_state(MasterCabinetState.profile_edit_menu)
    await message.answer(_format_master_full_profile(updated), reply_markup=MASTER_PROFILE_VIEW_KB)


@router.message(MasterCabinetState.profile_edit_menu, F.text == "📍 Адрес работы")
async def profile_edit_address_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterCabinetState.profile_edit_address)
    await message.answer("Введите новый адрес:")


@router.message(MasterCabinetState.profile_edit_address)
async def profile_edit_address_save(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await q.update_master_field(master["id"], "work_address", message.text.strip())
    updated = await q.get_master_by_telegram_id(message.from_user.id)
    await conn.close()
    await state.set_state(MasterCabinetState.profile_edit_menu)
    await message.answer(_format_master_full_profile(updated), reply_markup=MASTER_PROFILE_VIEW_KB)


@router.message(MasterCabinetState.profile_edit_menu, F.text == "💼 Профессии")
async def profile_edit_prof_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterCabinetState.profile_edit_professions)
    await state.update_data(new_professions=[])
    await message.answer("Введите профессии по одной. Для завершения нажмите ✅ Готово", reply_markup=PROFESSION_DONE_KB)


@router.message(MasterCabinetState.profile_edit_professions)
async def profile_edit_prof_save(message: Message, state: FSMContext, db) -> None:
    data = await state.get_data()
    profs = data.get("new_professions", [])

    if message.text == "✅ Готово":
        if not profs:
            await message.answer("Добавьте хотя бы одну профессию.")
            return
        conn, q, master = await _master_ctx(message, db)
        if not master:
            return
        await q.update_master_field(master["id"], "professions", json.dumps(profs, ensure_ascii=False))
        updated = await q.get_master_by_telegram_id(message.from_user.id)
        await conn.close()
        await state.set_state(MasterCabinetState.profile_edit_menu)
        await message.answer(_format_master_full_profile(updated), reply_markup=MASTER_PROFILE_VIEW_KB)
        return

    profs.append(message.text.strip())
    await state.update_data(new_professions=profs)
    await message.answer("Профессия добавлена. Добавьте ещё или нажмите ✅ Готово", reply_markup=PROFESSION_DONE_KB)


@router.message(MasterCabinetState.menu, F.text == "⚙️ Настройки записи")
async def settings_menu(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    s = await q.get_booking_settings(master["id"])
    await conn.close()

    await state.set_state(MasterCabinetState.settings_menu)
    await message.answer(
        "⚙️ Настройки записи\n\n"
        f"Шаг времени: {s['time_step_minutes']}\n"
        f"Начало первой записи: {s['first_booking_time']}\n"
        f"Конец последней записи: {s['last_booking_time']}\n"
        f"Записи вперед: {s['booking_range_days']} дней\n"
        f"Длительности мастера: {s['manual_duration_options']}\n"
        f"Ограничение клиентов: {s['client_booking_limit_type'] or '—'}",
        reply_markup=MASTER_SETTINGS_KB,
    )


@router.message(MasterCabinetState.settings_menu, F.text == "⏱ Шаг времени")
async def settings_step_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterCabinetState.settings_step)
    await message.answer("Введите 60, 30 или 15")


@router.message(MasterCabinetState.settings_step)
async def settings_step_save(message: Message, state: FSMContext, db) -> None:
    try:
        value = int(message.text)
        if value not in {15, 30, 60}:
            raise ValueError
    except ValueError:
        await message.answer("Введите 60, 30 или 15")
        return
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await q.update_booking_settings(master["id"], "time_step_minutes", value)
    await conn.close()
    await state.set_state(MasterCabinetState.settings_menu)
    await message.answer("✅ Шаг времени обновлён", reply_markup=MASTER_SETTINGS_KB)


@router.message(MasterCabinetState.settings_menu, F.text == "🌅 Начало первой записи")
async def settings_first_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterCabinetState.settings_first_time)
    await message.answer("Введите время в формате HH:MM")


@router.message(MasterCabinetState.settings_first_time)
async def settings_first_save(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await q.update_booking_settings(master["id"], "first_booking_time", message.text.strip())
    await conn.close()
    await state.set_state(MasterCabinetState.settings_menu)
    await message.answer("✅ Обновлено", reply_markup=MASTER_SETTINGS_KB)


@router.message(MasterCabinetState.settings_menu, F.text == "🌙 Конец последней записи")
async def settings_last_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterCabinetState.settings_last_time)
    await message.answer("Введите время в формате HH:MM")


@router.message(MasterCabinetState.settings_last_time)
async def settings_last_save(message: Message, state: FSMContext, db) -> None:
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await q.update_booking_settings(master["id"], "last_booking_time", message.text.strip())
    await conn.close()
    await state.set_state(MasterCabinetState.settings_menu)
    await message.answer("✅ Обновлено", reply_markup=MASTER_SETTINGS_KB)


@router.message(MasterCabinetState.settings_menu, F.text == "📆 Записи вперед")
async def settings_range_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterCabinetState.settings_range)
    await message.answer("Введите 7, 14 или 30")


@router.message(MasterCabinetState.settings_range)
async def settings_range_save(message: Message, state: FSMContext, db) -> None:
    try:
        value = int(message.text)
        if value not in {7, 14, 30}:
            raise ValueError
    except ValueError:
        await message.answer("Введите 7, 14 или 30")
        return
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await q.update_booking_settings(master["id"], "booking_range_days", value)
    await conn.close()
    await state.set_state(MasterCabinetState.settings_menu)
    await message.answer("✅ Обновлено", reply_markup=MASTER_SETTINGS_KB)


@router.message(MasterCabinetState.settings_menu, F.text == "⌛ Длительность записи мастером")
async def settings_duration_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterCabinetState.settings_duration)
    await message.answer(
        "⌛ Длительность записи мастером\n\n"
        "Эта настройка — список длительностей, из которого мастер выбирает время записи при ручном добавлении клиента.\n"
        "Она не влияет на онлайн-запись клиента: там используется длительность из услуги.\n\n"
        "Введите длительности через запятую (в минутах), например 30,60,90"
    )


@router.message(MasterCabinetState.settings_duration)
async def settings_duration_save(message: Message, state: FSMContext, db) -> None:
    try:
        values = [int(v.strip()) for v in message.text.split(",") if v.strip()]
        if not values:
            raise ValueError
    except ValueError:
        await message.answer("Неверный формат")
        return
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await q.update_booking_settings(master["id"], "manual_duration_options", json.dumps(values))
    await conn.close()
    await state.set_state(MasterCabinetState.settings_menu)
    await message.answer("✅ Обновлено", reply_markup=MASTER_SETTINGS_KB)


@router.message(MasterCabinetState.settings_menu, F.text == "⛔ Ограничение записи для клиентов")
async def settings_limit_prompt(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterCabinetState.settings_limit)
    await message.answer("Введите: 5h / no_today / 1d / 2d")


@router.message(MasterCabinetState.settings_limit)
async def settings_limit_save(message: Message, state: FSMContext, db) -> None:
    token = message.text.strip().lower()
    options = {"5h": ("hours_before", 5), "no_today": ("no_today", 1), "1d": ("days_before", 1), "2d": ("days_before", 2)}
    if token not in options:
        await message.answer("Введите один из вариантов: 5h / no_today / 1d / 2d")
        return
    limit_type, limit_value = options[token]
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    await q.update_booking_settings(master["id"], "client_booking_limit_type", limit_type)
    await q.update_booking_settings(master["id"], "client_booking_limit_value", limit_value)
    await conn.close()
    await state.set_state(MasterCabinetState.settings_menu)
    await message.answer("✅ Обновлено", reply_markup=MASTER_SETTINGS_KB)


@router.message(MasterCabinetState.menu, F.text == "📊 Статистика")
async def stats_menu(message: Message, state: FSMContext) -> None:
    await state.set_state(MasterCabinetState.stats_period)
    await message.answer("📊 Выберите период:", reply_markup=MASTER_STATS_PERIOD_KB)


@router.message(MasterCabinetState.stats_period, F.text.in_({"Неделя", "Месяц", "Год"}))
async def stats_show(message: Message, db) -> None:
    days = {"Неделя": 7, "Месяц": 30, "Год": 365}[message.text]
    conn, q, master = await _master_ctx(message, db)
    if not master:
        return
    s = await q.stats_summary(master["id"], days)
    await conn.close()

    await message.answer(
        f"📊 Статистика за период: {message.text}\n\n"
        f"💰 Доход: {s['income']}\n"
        f"📅 Количество записей: {s['appointments']}\n"
        f"🆕 Новые клиенты: {s['new_clients']}\n"
        f"⏱ Рабочие часы: {round((s['worked_minutes'] or 0) / 60, 1)}\n"
        f"❌ Отмены клиентом: {s['cancelled_by_client']}\n"
        f"❌ Отмены мастером: {s['cancelled_by_master']}\n"
        f"🚫 Неявки: {s['no_show']}\n"
        f"😴 Спящие клиенты: {s['sleeping']}",
        reply_markup=MASTER_STATS_PERIOD_KB,
    )


@router.message(MasterCabinetState, F.text == "🏠 Главное меню")
async def cabinet_home(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    if current and current.startswith("MasterCabinetState"):
        await state.clear()
        await message.answer("Главное меню мастера 👇", reply_markup=MASTER_MAIN_KB)


@router.message(MasterCabinetState, F.text == "◀️ Назад")
async def cabinet_back(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    if current and current.startswith("MasterCabinetState"):
        if current == MasterCabinetState.menu.state:
            await state.clear()
            await message.answer("Главное меню мастера 👇", reply_markup=MASTER_MAIN_KB)
        elif current == MasterCabinetState.stats_period.state:
            await state.set_state(MasterCabinetState.menu)
            await message.answer("👤 Кабинет мастера", reply_markup=MASTER_CABINET_KB)
        elif current in {
            MasterCabinetState.settings_step.state,
            MasterCabinetState.settings_first_time.state,
            MasterCabinetState.settings_last_time.state,
            MasterCabinetState.settings_range.state,
            MasterCabinetState.settings_duration.state,
            MasterCabinetState.settings_limit.state,
        }:
            await state.set_state(MasterCabinetState.settings_menu)
            await message.answer("⚙️ Настройки записи", reply_markup=MASTER_SETTINGS_KB)
        elif current in {
            MasterCabinetState.profile_edit_name.state,
            MasterCabinetState.profile_edit_last_name.state,
            MasterCabinetState.profile_edit_phone.state,
            MasterCabinetState.profile_edit_birth_date.state,
            MasterCabinetState.profile_edit_work_start.state,
            MasterCabinetState.profile_edit_address.state,
            MasterCabinetState.profile_edit_professions.state,
        }:
            await state.set_state(MasterCabinetState.profile_edit_menu)
            await message.answer("👤 Профиль мастера", reply_markup=MASTER_PROFILE_VIEW_KB)
        elif current in {
            MasterCabinetState.service_add_name.state,
            MasterCabinetState.service_add_description.state,
            MasterCabinetState.service_add_duration.state,
            MasterCabinetState.service_add_price.state,
            MasterCabinetState.service_delete_pick.state,
            MasterCabinetState.service_delete_confirm.state,
            ServiceCreateState.name.state,
            ServiceCreateState.description.state,
            ServiceCreateState.duration.state,
            ServiceCreateState.price.state,
            ServiceEditPriceState.pick_service.state,
            ServiceEditPriceState.new_price.state,
        }:
            await state.set_state(MasterCabinetState.services_menu)
            await message.answer("🛠 Меню услуг", reply_markup=MASTER_SERVICES_KB)
        else:
            await state.set_state(MasterCabinetState.menu)
            await message.answer("👤 Кабинет мастера", reply_markup=MASTER_CABINET_KB)
