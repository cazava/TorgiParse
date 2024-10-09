import datetime
import logging

from aiogram import Bot, Dispatcher, types, F, Router, flags
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from pars import parser
from bd import lotsbd

router = Router()
bot = Bot(config.bot_token)


@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(text='Бот собирает лоты аренды недвижимого имущества в Санкт-Петербурге и постит их в канал')


async def parse():
    await parser.parse_gos()


async def post(bot: Bot, lot: tuple):
    address = lot[1]
    price = lot[3]
    date = lot[4]
    square = lot[5]
    ref = lot[7]
    formatted_price = f"{price:,.2f} руб.".replace(',', ' ').replace('.', ',')

    def get_map_url(latitude, longitude, api_map):
        url_map = f'''https://static-maps.yandex.ru/v1?ll={latitude},{longitude}&size=600,450&z=13&pt={latitude},{longitude}&apikey={api_map}'''
        return url_map

    map_url = get_map_url(lot[8], lot[9], config.api_map)

    text = f'''
{address}
*Начальная цена:* {formatted_price}
*Площадь:* {square} кв.м.
*Окончание подачи заявок:* {date}

'''

    # inline кнопка для ссылки
    kb_lot = InlineKeyboardBuilder()
    kb_lot.add(types.InlineKeyboardButton(
        text='Смотреть лот',
        url=ref
    ))

    try:
        await bot.send_photo(chat_id=config.channel_id, photo=map_url, caption=text, reply_markup=kb_lot.as_markup(),
                             parse_mode='Markdown')
        lotsbd.set_post(lot_id=lot[0])
    except Exception as e:
        logging.exception(datetime.datetime.now(), e)


async def check_new_post(bot):
    for lot in lotsbd.get_lots():
        if lot[10] == 0:
            try:
                await post(bot=bot, lot=lot)
            except Exception as e:
                logging.exception(datetime.datetime.now(), e)
                continue
