from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

inline_btn_1 = InlineKeyboardButton('Все подходящие слова', callback_data='btn_all_good')
inline_btn_2 = InlineKeyboardButton('Без зелёных букв', callback_data='btn_new_letters')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2)