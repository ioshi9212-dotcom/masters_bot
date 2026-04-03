from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import load_settings
from database.db import Database
from database.queries import Queries
from handlers import setup_handlers


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    settings = load_settings()
    if not settings.bot_token:
        raise RuntimeError("Не задан BOT_TOKEN в переменных окружения")

    db = Database(str(settings.db_path))

    conn = await db.connect()
    try:
        q = Queries(conn)
        await q.init_schema()
    finally:
        await conn.close()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp["db"] = db
    setup_handlers(dp)

    logging.info("Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
