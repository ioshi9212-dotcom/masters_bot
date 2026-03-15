from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

VISIT_CONFIRM_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Клиент пришёл", callback_data="visit:came")],
        [InlineKeyboardButton(text="⚠️ Не пришёл, но предупредил", callback_data="visit:warned")],
        [InlineKeyboardButton(text="❌ Не пришёл и не предупредил", callback_data="visit:no_show")],
    ]
)
