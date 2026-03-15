from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.queries import Queries
from keyboards.reply import MASTER_EXISTS_KB, MASTER_MAIN_KB, YES_SKIP_KB
from states.master_states import MasterRegistrationState
from utils.dates import calculate_experience_text
from utils.formatters import format_master_profile

router = Router()


@router.message(F.text == "👩‍🎨 Мастер")
async def choose_master(message: Message, state: FSMContext, db) -> None:
    conn = await db.connect()
    q = Queries(conn)
    master = await q.get_master_by_telegram_id(message.from_user.id)
    await conn.close()

    if master:
        await message.answer(
            "✅ Вы зарегистрированы как мастер.\n\n"
            "Вы хотите оставить этот профиль или удалить его и создать новый?",
            reply_markup=MASTER_EXISTS_KB,
        )
        return

    await state.set_state(MasterRegistrationState.first_name)
    await message.answer("✨ Добро пожаловать в систему записи.\n\nВведите ваше имя:")


@router.message(F.text == "✅ Оставить профиль")
async def keep_master_profile(message: Message) -> None:
    await message.answer("Главное меню мастера открыто 👇", reply_markup=MASTER_MAIN_KB)


@router.message(F.text == "🗑 Удалить и создать новый")
async def delete_master_profile(message: Message, state: FSMContext, db) -> None:
    conn = await db.connect()
    q = Queries(conn)
    await q.deactivate_master_profile(message.from_user.id)
    await conn.close()

    await state.set_state(MasterRegistrationState.first_name)
    await message.answer("Старый профиль удалён. Введите имя для нового профиля мастера:")


@router.message(MasterRegistrationState.first_name)
async def m_first_name(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text.strip())
    await state.set_state(MasterRegistrationState.last_name)
    await message.answer("Введите фамилию или нажмите ⏭ Пропустить", reply_markup=YES_SKIP_KB)


@router.message(MasterRegistrationState.last_name)
async def m_last_name(message: Message, state: FSMContext) -> None:
    last_name = None if message.text == "⏭ Пропустить" else message.text.strip()
    await state.update_data(last_name=last_name, professions=[])
    await state.set_state(MasterRegistrationState.profession)
    await message.answer("Введите профессию (например, Мастер маникюра):")


@router.message(MasterRegistrationState.profession)
async def m_profession(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    professions = data.get("professions", [])

    text = message.text.strip()
    if text == "✅ Готово":
        if not professions:
            await message.answer("Добавьте хотя бы одну профессию.")
            return
        await state.set_state(MasterRegistrationState.birth_date)
        await message.answer("Введите дату рождения в формате ДД.ММ")
        return

    professions.append(text)
    await state.update_data(professions=professions)
    await message.answer("Профессия добавлена. Добавьте ещё или нажмите ✅ Готово")


@router.message(MasterRegistrationState.birth_date)
async def m_birth_date(message: Message, state: FSMContext) -> None:
    await state.update_data(birth_date=message.text.strip())
    await state.set_state(MasterRegistrationState.work_start)
    await message.answer("Введите месяц и год начала работы в формате ММ.ГГГГ")


@router.message(MasterRegistrationState.work_start)
async def m_work_start(message: Message, state: FSMContext) -> None:
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
    await message.answer("Введите номер телефона (обязательно):")


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
