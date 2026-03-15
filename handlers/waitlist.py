from aiogram import F, Router
from aiogram.types import Message

from keyboards.master import MASTER_WAITLIST_KB

router = Router()


@router.message(F.text == "⏳ Лист ожидания")
async def waitlist_menu(message: Message) -> None:
    await message.answer(
        "⏳ Лист ожидания\n\n"
        "Доступно:\n"
        "• 📅 Ближайшие окна\n"
        "• 🗓 Определенная дата\n\n"
        "Когда клиент добавляется в лист ожидания, список обновляется у мастера.",
        reply_markup=MASTER_WAITLIST_KB,
    )


@router.message(F.text == "📅 Ближайшие окна")
async def nearest_windows_waitlist(message: Message) -> None:
    await message.answer(
        "📅 Ближайшие окна\n\n"
        "Клиент ждёт ближайшее освободившееся окно.\n"
        "Если окно появляется (новое или после отмены), клиенту приходит уведомление без кнопок."
    )


@router.message(F.text == "🗓 Определенная дата")
async def specific_dates_waitlist(message: Message) -> None:
    await message.answer(
        "🗓 Определенная дата\n\n"
        "Здесь будет выбор одной или нескольких дат на месяц вперёд и добавление в лист ожидания."
    )
