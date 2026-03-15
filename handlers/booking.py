from aiogram import F, Router
from aiogram.types import Message

router = Router()


@router.message(F.text == "✍️ Записать клиента")
async def master_booking(message: Message) -> None:
    await message.answer(
        "Раздел ✍️ Записать клиента: здесь будет календарь текущего и следующего месяца."
    )


@router.message(F.text == "✍️ Записаться")
async def client_booking(message: Message) -> None:
    await message.answer("Раздел ✍️ Записаться: сначала выберите мастера или введите код мастера 🔑")
