import logging
import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram import Bot, types

from config import *
from menu import *

from game import Game

TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)

# running games
games = {}
menu = {'start': StartMenu(), 'word': WordMenu(), 'mask': MaskMenu()}


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


async def _reply(msg, text):
    if len(text) > 4096:
        for x in range(0, len(text), 4096):
            await msg.answer(text[x:x + 4096])
    else:
        await msg.answer(text)


@dp.message_handler()
async def echo(message: types.Message):
    user = message.from_user.id
    if not games.get(user):
        games[user] = Game()
        init = games[user].prepare(DICT_FILE)
        if not init:
            await message.answer("Ошибка инициализации %1".format(DICT_FILE))
            return

    if message.text == '/start':
        games[user].reset()
        games[user].current_menu = 'start'

    new_menu, result = menu[games[user].current_menu].process(message.text)
    if not result.status:
        await _reply(message, result.text)
    elif games[user].current_menu == 'word':
        games[user].last_answer = result.text
    elif games[user].current_menu == 'mask':
        word = games[user].last_answer
        green = ['.'] * WORD_LEN
        yellow = ['.'] * WORD_LEN
        grey = []

        for i in range(WORD_LEN):
            match message.text[i]:
                case '0':
                    grey.append(word[i].lower())
                case '1':
                    yellow[i] = word[i].lower()
                case '2':
                    green[i] = word[i].lower()
        await _reply(message, games[user].make_turn(green, yellow, grey))

    games[user].current_menu = new_menu


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
