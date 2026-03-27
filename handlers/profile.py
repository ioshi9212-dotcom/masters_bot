from aiogram import Router

router = Router()
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.queries import Queries
from keyboards.reply import CLIENT_MAIN_KB
from states.client_states import ClientProfileState
from utils.formatters import format_client_profile

router = Router()


@router.message(ClientProfileState.create_first_name)
async def c_first_name(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text.strip())
    await state.set_state(ClientProfileState.create_last_name)
    await message.answer("Введите фамилию:")


@router.message(ClientProfileState.create_last_name)
async def c_last_name(message: Message, state: FSMContext) -> None:
    await state.update_data(last_name=message.text.strip())
    await state.set_state(ClientProfileState.create_phone)
    await message.answer("Введите номер телефона:")


@router.message(ClientProfileState.create_phone)
async def c_phone(message: Message, state: FSMContext) -> None:
    await state.update_data(phone=message.text.strip())
    await state.set_state(ClientProfileState.create_birth_date)
    await message.answer("Введите дату рождения (ДД.ММ):")


@router.message(ClientProfileState.create_birth_date)
async def c_birth_date(message: Message, state: FSMContext, db) -> None:
    await state.update_data(birth_date=message.text.strip())
    data = await state.get_data()

    conn = await db.connect()
    q = Queries(conn)
    await q.upsert_client_profile(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        data=data,
    )
    client = await q.get_client_by_telegram_id(message.from_user.id)
    await conn.close()

    await state.clear()
    await message.answer("✅ Профиль клиента сохранён.")
    await message.answer(format_client_profile(client), reply_markup=CLIENT_MAIN_KB)
