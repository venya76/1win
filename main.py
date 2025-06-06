
import asyncio
import logging

from aiogram import Dispatcher, Bot

from config import BOT_TOKEN
from handlers.client import router as client_router
from handlers.admin import router as admin_router
from database.db import DataBase


logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=f'[BOT] '
               f'{u"%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s"}')
    logger.info("Starting bot...")

    dp = Dispatcher()
    bot = Bot(BOT_TOKEN)
    dp.include_routers(client_router, admin_router)

    dp.startup.register(DataBase.on_startup)
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())


