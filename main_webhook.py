import logging

from create_bot import *
from handlers import registration, exit, other
from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook

# Чтобы запустить бота этим main'ом запусти ngrok либо потом догвооримся и

# webhook settings
WEBHOOK_HOST = 'https://2eae-188-170-86-184.eu.ngrok.io' #поменяй тут ссылку из ngrok
WEBHOOK_PATH = ''
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = 'localhost'  # здесь так и оставь пока с localhost'ом будем
WEBAPP_PORT = 3000 #пиши сюда порт который ты указывал

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage = MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

registration.register_handlers(dp)
exit.register_handlers(dp)
other.register_handlers(dp)

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    # insert code here to run it after start

async def on_shutdown(dp):
    logging.warning('Shutting down..')
    await bot.delete_webhook()

    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning('Bye!')


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )