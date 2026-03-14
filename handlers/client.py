from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.queries import Queries
from keyboards.reply import CLIENT_MAIN_KB
from states.client_states import ClientProfileState

router = Router()


@router.message(F.text == "👤 Клиент")
async def choose_client(message: Message, db) -> None:
    conn = await db.connect()
    q = Queries(conn)
    client = await q.get_client_by_telegram_id(message.from_user.id)
    await conn.close()

    if client:
        await message.answer("Главное меню клиента 👇", reply_markup=CLIENT_MAIN_KB)
        return

    await message.answer(
        "✨ Добро пожаловать в систему записи.\n\n"
        "Этот бот помогает:\n"
        "— быстро записаться к мастеру\n"
        "— получать напоминания о записи\n"
        "— вставать в лист ожидания"
    )
    await message.answer("Главное меню клиента 👇", reply_markup=CLIENT_MAIN_KB)


@router.message(F.text == "👤 Мой профиль")
async def my_profile(message: Message, db, state: FSMContext) -> None:
    conn = await db.connect()
    q = Queries(conn)
    client = await q.get_client_by_telegram_id(message.from_user.id)
    await conn.close()

    if client:
        from utils.formatters import format_client_profile

        await message.answer(
            format_client_profile(client)
            + "\n\nКнопки: ✏️ Редактировать профиль / 🗑 Удалить профиль"
        )
    else:
        await state.set_state(ClientProfileState.first_name)
        await message.answer(
            "⚠️ У вас ещё нет профиля. Создайте его, чтобы записываться к мастеру и получать уведомления.\n\n"
            "Введите имя:"
        )
