import asyncio
import logging
import sys

from aiogram import Dispatcher
from aiogram.types import BotCommandScopeAllPrivateChats
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from middlewares.db import DataBaseSession
from handlers.user_private import user_private_router
from handlers.admin_panel import admin_route
from assets.bot_cmd_list import private
from database.engine import create_db, drop_db, session_maker

from bot_creator import bot

# Ограничение запросов для разгрузки скрипта
ALLOWED_UPDATES = ["message", "edited_message", "callback_query"]

dp = Dispatcher()

dp.include_routers(user_private_router,
                   admin_route)


async def on_startup():
    run_param = False
    if run_param:
        await drop_db()
    await create_db()


async def on_shutdown():
    print('--- !!! --- BASTED --- !!! ---')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


logging.basicConfig(level=logging.INFO, stream=sys.stdout)
asyncio.run(main())
