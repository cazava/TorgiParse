import asyncio
import datetime
import logging
import time

import urllib3
from aiogram import Dispatcher
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
import handlers

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"

logging.basicConfig(level=logging.ERROR, filename="bot_log.log", format=_log_format)

sheduler = AsyncIOScheduler(timezone='Europe/Moscow')

dp = Dispatcher()
bot = Bot(token=config.bot_token)
dp.include_routers(handlers.router)


async def main():
    sheduler.add_job(
        handlers.parse,
        trigger='interval',
        hours=2)
    sheduler.add_job(
        handlers.check_new_post,
        trigger='interval',
        hours=2,
        minutes=30,
        args=[handlers.bot])
    sheduler.start()
    await dp.start_polling(handlers.bot, skip_updates=False)


if __name__ == "__main__":

    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            logging.exception(datetime.datetime.now(), e)
            time.sleep(3)
            print(e)
