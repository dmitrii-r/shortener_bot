import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers import (
    add_event_handlers,
    get_event_handlers,
    other_handlers,
    shortener_handlers,
    user_handlers,
)
from keyboards.keyboards import set_main_menu
from utils.db_utils import create_table

load_dotenv()

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s "
        "[%(asctime)s] - %(name)s - %(message)s",
    )

    logger.info("Запуск бота.")

    bot: Bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp: Dispatcher = Dispatcher()

    await set_main_menu(bot)
    await create_table()

    dp.include_router(user_handlers.router)
    dp.include_router(add_event_handlers.router)
    dp.include_router(get_event_handlers.router)
    # dp.include_router(shortener_handlers.router)
    dp.include_router(other_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
