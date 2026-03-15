from aiogram import F, Router
from aiogram.types import Message

router = Router()


@router.message(F.text == "⏳ Лист ожидания")
async def waitlist_menu(message: Message) -> None:
    await message.answer(
        "⏳ Лист ожидания\n\n"
        "Доступно:\n"
        "• 📅 Ближайшие окна\n"
        "• 🗓 Определенная дата"
    )
