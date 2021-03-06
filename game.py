from config import *
from menu import *
import re


def prepare_word(word: str) -> str:
    letters = list(word.lower())

    if '\n' in letters:
        letters.remove('\n')

    if len(letters) != WORD_LEN:
        return str()

    for idx in range(len(letters)):
        if not letters[idx].isalpha():  # убрать дефисы и прочие недоразумения
            return str()
        if letters[idx] == 'ё':
            letters[idx] = 'е'

    return "".join(letters)


def exclude(word, grey, included):
    for ex in grey:
        if ex not in included:
            if ex in word:
                return False
        else:  # знаем сколько этих букв в слове
            if not (word.count(ex) == included.count(ex)):
                return False
    return True


def include(word, letters):
    _word = list(word)
    for idx in range(len(letters)):
        if letters[idx] in _word:
            _word.remove(letters[idx])
        else:
            return False
    return True


class Game:
    def __init__(self):
        self.__words = []
        self.__game = []
        self.last_answer = str()
        self.current_menu = str()

    def results(self):
        return self.__game

    def prepare(self, filename: str):
        try:
            with open(filename, 'r', encoding='utf8') as f:
                self.__words = f.readlines()
        except IOError as e:
            return False

        # убираем Ё и повторы
        self.__words = [prepare_word(w) for w in self.__words]
        self.__words = list(set(self.__words))
        if str() in self.__words:
            self.__words.remove(str())
        self.reset()
        return True

    def reset(self):
        self.__game = self.__words

    def make_turn(self, green, yellow, grey):
        # оставляем только слова по зелёной маске
        r = re.compile("".join(green))
        self.__game = list(filter(r.match, self.__game))

        # желтая маска и буквы в ней
        incl_letters = green
        incl_letters.extend(yellow)
        incl_letters = [ltr.lower() for ltr in incl_letters if ltr.isalpha()]  # если буквы парные, нужно искать обе

        # убираем все с серыми буквами, с учетом тех, что должны быть
        if len(grey):
            self.__game = list(filter(lambda e: exclude(e, "".join(grey).lower(), incl_letters), self.__game))

        # оставляем слова, содержащие все жёлтые буквы хоть раз
        self.__game = list(filter(lambda e: include(e, "".join(incl_letters)), self.__game))

        # если желтые буквы есть, убираем слова, где они стоят в точно неправильных местах
        for idx in range(len(yellow)):
            if yellow[idx] != '.':
                self.__game = [w for w in self.__game if w[idx] != yellow[idx]]

        return self.__game


def test():
    games = {}
    menu = {MenuId.START: Menu(MenuId.START, START_INFO), MenuId.WORD: WordMenu(), MenuId.MASK: MaskMenu()}

    user = "id1"

    if not games.get(user):
        games[user] = Game()
        init = games[user].prepare(DICT_FILE)
        if not init:
            print("Ошибка инициализации %1".format(DICT_FILE))
            return
        games[user].current_menu = MenuId.START

    while True:
        text = input()
        if isinstance(text, str):
            new_menu = games[user].current_menu

            if text == '/start':
                games[user].reset()
                games[user].current_menu = MenuId.START
                new_menu = MenuId.WORD

            result = menu[games[user].current_menu].process(text)
            if not result[0]:
                print(result[1])
            elif games[user].current_menu == MenuId.WORD:
                games[user].last_answer = result[1]
                new_menu = MenuId.MASK
            elif games[user].current_menu == MenuId.MASK:
                word = games[user].last_answer
                green = ['.'] * WORD_LEN
                yellow = ['.'] * WORD_LEN
                grey = []

                for i in range(WORD_LEN):
                    match text[i]:
                        case '0':
                            grey.append(word[i].lower())
                        case '1':
                            yellow[i] = word[i].lower()
                        case '2':
                            green[i] = word[i].lower()
                print(games[user].make_turn(green, yellow, grey))
                new_menu = MenuId.WORD

            games[user].current_menu = new_menu
            print(menu[games[user].current_menu].info)


if __name__ == '__main__':
    test()
