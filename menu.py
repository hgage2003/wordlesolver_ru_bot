from config import *


class Result:
    def __init__(self, status=False, text=str()):
        self.status = status
        self.text = text


class Menu:
    def __init__(self, menu_id: str, advance_id: str, info=str()):
        self.id = menu_id
        self.advance_id = advance_id
        self.info = info

    def process(self, text: str, result: Result) -> (str, Result):
        return self.id, (False, "Метод в process в классе Menu не должен вызываться")


class StartMenu(Menu):
    def __init__(self):
        super().__init__('start', 'word')
        self.info = "Новая игра: /start"

    def process(self, text: str) -> (str, Result):
        if text == '/start':
            return self.advance_id, Result(True, str())
        else:
            return self.id, Result(True, str())  # не нужно дополнительных сообщений


def check_word(word: str) -> (bool, str):
    if len(word) != WORD_LEN:
        return False, "Слово должно быть из пяти букв"
    for i in range(WORD_LEN):
        if not word[i].isalpha():
            return False, "В слове должны быть только буквы"
    return True, str()


class WordMenu(Menu):
    def __init__(self):
        super().__init__('word', 'mask')
        self.info = "Какое слово отправил в Wordle?"

    def process(self, text: str) -> (str, Result):
        check = check_word(text)
        if not check[0]:
            return self.id, Result(False, check[1])
        else:
            return self.advance_id, Result(True, text)


def check_mask(mask) -> (bool, str):
    if len(mask) != WORD_LEN:
        return False, "Маска должна быть из пяти цифр!"
    for i in range(WORD_LEN):
        if not ['0', '1', '2'].count(mask[i]):
            return False, "В маске можно использовать только 0, 1 или 2"
    return True, str()


class MaskMenu(Menu):
    def __init__(self):
        super().__init__('mask', 'word')
        self.info = "Что ответил Wordle? \nПришли число из 5 цифр 0, 1 или 2\n " \
                    "0 - буква серая, 1 - желтая, 2 - зеленая"

    def process(self, text: str) -> (str, Result):
        check = check_mask(text)
        if not check[0]:
            return self.id, Result(False, check[1])
        else:
            return self.advance_id, Result(True, text)
