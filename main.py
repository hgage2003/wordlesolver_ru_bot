import logging
import os
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook
from aiogram import Bot, types
import keyboards as kb

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
menu = {MenuId.START: Menu(MenuId.START, START_INFO), MenuId.WORD: WordMenu(), MenuId.MASK: MaskMenu()}


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


async def _reply(msg, text: str):
    while len(text) > 4096:
        x = text[:4096].rfind('\n')
        if x < 0:
            x = text[:4096].rfind(' ')
            if x < 0:
                await msg.answer('Ошибка, текст не разбивается на сообщения')
                return
        await msg.answer(text[:x])
        text = text[x:]
    if len(text) > 0:
        await msg.answer(text)


@dp.callback_query_handler()
async def process_buttons(callback_query: types.CallbackQuery):
    button = callback_query.data
    user = callback_query.from_user.id

    if button == 'btn_all_good':
        words = games[user].results()
        text = '\n'.join(words)
        await _reply(text)


@dp.message_handler()
async def echo(message: types.Message):
    user = message.from_user.id
    if not games.get(user):
        games[user] = Game()
        games[user].current_menu = MenuId.START
        init = games[user].prepare(DICT_FILE)
        if not init:
            await message.answer("Ошибка инициализации %1".format(DICT_FILE))
            return

    new_menu = games[user].current_menu

    if message.text == '/start':
        games[user].reset()
        games[user].current_menu = MenuId.START
        new_menu = MenuId.WORD

    result = menu[games[user].current_menu].process(message.text)
    if not result[0]:
        await _reply(message, result[1])
    elif games[user].current_menu == MenuId.WORD:
        games[user].last_answer = result[1]
        new_menu = MenuId.MASK
    elif games[user].current_menu == MenuId.MASK:
        if message.text == '22222':
            await _reply(message, "Ура! Поздравляю!")
            new_menu = MenuId.START
        else:
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
            words = games[user].make_turn(green, yellow, grey)
            if not len(words):
                await message.answer("Кажется, я не знаю такого слова...")
                new_menu = MenuId.START
            elif len(words) <= 10:
                await message.answer('\n'.join(words))
            else:
                text = '\n'.join(words[:10])
                await message.answer(text, reply_markup=kb.inline_kb1)
        new_menu = MenuId.WORD

    games[user].current_menu = new_menu
    await _reply(message, menu[games[user].current_menu].info)


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
