from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message

from keyboards.common import START_ROLE_KB

router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message) -> None:
    await message.answer(
        "Здравствуйте 👋\n\nВы мастер или клиент?",
        reply_markup=START_ROLE_KB,
    )


@router.message(StateFilter(None), F.text == "🏠 Главное меню")
async def to_main_menu(message: Message) -> None:
    await message.answer("Выберите роль через /start")
