from config import *
from enum import Enum

START_INFO = "Новая игра: /start"


class MenuId(Enum):
    START = 'start'
    WORD = 'word'
    MASK = 'MASK'


class Menu:
    def __init__(self, menu_id: MenuId, info=str()):
        self.id = menu_id
        self.info = info

    def process(self, text: str) -> (bool, str):
        return True, text


def check_word(word: str) -> (bool, str):
    if len(word) != WORD_LEN:
        return False, "Слово должно быть из пяти букв"
    for i in range(WORD_LEN):
        if not word[i].isalpha():
            return False, "В слове должны быть только буквы"
    return True, str()


class WordMenu(Menu):
    def __init__(self):
        super().__init__(MenuId.WORD)
        self.info = "Какое слово отправил в Wordle?"

    def process(self, text: str) -> (bool, str):
        check = check_word(text)
        if not check[0]:
            return False, check[1]
        else:
            return True, text


def check_mask(mask) -> (bool, str):
    if len(mask) != WORD_LEN:
        return False, "Маска должна быть из пяти цифр!"
    for i in range(WORD_LEN):
        if not ['0', '1', '2'].count(mask[i]):
            return False, "В маске можно использовать только 0, 1 или 2"
    return True, str()


class MaskMenu(Menu):
    def __init__(self):
        super().__init__(MenuId.MASK)
        self.info = "Что ответил Wordle? \nПришли число из 5 цифр 0, 1 или 2\n " \
                    "0 - буква серая, 1 - желтая, 2 - зеленая"

    def process(self, text: str) -> (bool, str):
        check = check_mask(text)
        if not check[0]:
            return False, check[1]
        else:
            return True, text
