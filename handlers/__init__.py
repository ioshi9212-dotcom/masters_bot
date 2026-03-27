from aiogram import Dispatcher

from handlers import booking, client, common, master, profile, waitlist


def setup_handlers(dp: Dispatcher) -> None:
    dp.include_router(common.router)
    dp.include_router(master.router)
    dp.include_router(client.router)
    dp.include_router(profile.router)
    dp.include_router(booking.router)
    dp.include_router(waitlist.router)
