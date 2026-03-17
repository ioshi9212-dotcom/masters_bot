from aiogram import Dispatcher

from handlers.booking import router as booking_router
from handlers.client import router as client_router
from handlers.common import router as common_router
from handlers.master import router as master_router
from handlers.profile import router as profile_router
from handlers.waitlist import router as waitlist_router


def setup_handlers(dp: Dispatcher) -> None:
    dp.include_router(common_router)
    dp.include_router(master_router)
    dp.include_router(client_router)
    dp.include_router(profile_router)
    dp.include_router(booking_router)
    dp.include_router(waitlist_router)
