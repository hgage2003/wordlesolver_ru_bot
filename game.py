from config import *
import re


def prepare_word(word: str) -> str:
    letters = list(word.lower())

    if LANG == 'ru':
        for idx in range(len(letters)):
            if letters[idx] == 'ё':
                letters[idx] = 'е'

    return "".join(letters)


def exclude(word, letters, green):
    for idx in range(len(word)):
        if word[idx] in letters and green[idx] == '.':  # только в неотгаданных
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

    def results(self):
        return self.__game

    def prepare(self, filename: str):
        try:
            with open(filename, 'r', encoding='utf8') as f:
                self.__words = f.readlines()
        except IOError as e:
            return False

        # убираем Ё и повторы
        self.__words = [prepare_word(w) for w in self.__words if len(w) == WORD_LEN + 1]
        self.__words = list(set(self.__words))
        self.reset()
        return True

    def reset(self):
        self.__game = self.__words

    def make_turn(self, green, yellow, grey):
        # оставляем только слова по зелёной маске
        pattern = ['.'] * WORD_LEN
        for idx in range(len(pattern)):
            if green[idx] != '':
                pattern[idx] = green[idx].lower()

        r = re.compile("".join(pattern))
        self.__game = list(filter(r.match, self.__game))

        # из них убираем все с серыми буквами из неотгаданных!
        self.__game = list(filter(lambda e: exclude(e, "".join(grey).lower(), pattern), self.__game))

        # желтая маска и буквы в ней
        pattern = ['.'] * WORD_LEN
        incl_letters = [ltr.lower() for ltr in green if ltr.isalpha()]  # если буквы парные, нужно искать обе
        for idx in range(len(pattern)):
            if yellow[idx].isalpha():
                pattern[idx] = yellow[idx].lower()
                incl_letters.append(pattern[idx])

        # оставляем слова, содержащие все жёлтые буквы хоть раз
        self.__game = list(filter(lambda e: include(e, "".join(incl_letters)), self.__game))

        # если желтые буквы есть, убираем слова, где они стоят в точно неправильных местах
        for idx in range(len(pattern)):
            if pattern[idx] != '.':
                self.__game = [w for w in self.__game if w[idx] != pattern[idx]]

    def play(self, message):
        return "Let's a Go!"


def test():
    games = {}

    while True:
        user = "message.from_user.id"
        text = input("Play: ")
        if not games.get(user):
            games[user] = Game()
            init = games[user].prepare(DICT_FILE)
            if not init:
                print("Ошибка инициализации %1".format(DICT_FILE))
                return
        print(games[user].play(text))


if __name__ == '__main__':
    test()
