
import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


bot = Bot(token=os.getenv('BOT_TOKEN'),
          default=DefaultBotProperties(
              parse_mode=ParseMode.HTML
          )
          )