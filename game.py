from config import *
import re


def prepare_word(word: str) -> str:
    letters = list(word.lower())

    if LANG == 'ru':
        for idx in range(len(letters)):
            if not letters[idx].isalpha():  # убрать дефисы и прочие недоразумения
                return ""
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


def check_mask(mask):
    if len(mask) != WORD_LEN:
        return False
    for i in range(WORD_LEN):
        if not ['0', '1', '2'].count(mask[i]):
            return False
    return True


class Game:
    def __init__(self):
        self.__words = []
        self.__game = []
        self.__phase = 0
        self.__last_answer = ""

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
        self.__words.remove("")
        self.reset()
        return True

    def reset(self):
        self.__game = self.__words
        self.__phase = 0

    def make_turn(self, green, yellow, grey):
        # оставляем только слова по зелёной маске
        pattern = ['.'] * WORD_LEN
        for idx in range(len(pattern)):
            if green[idx] != '':
                pattern[idx] = green[idx].lower()

        r = re.compile("".join(pattern))
        self.__game = list(filter(r.match, self.__game))

        # из них убираем все с серыми буквами из неотгаданных!
        if len(grey):
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
        reply = []
        if message == '/start':
            self.reset()

        match self.__phase:
            case 0:  # спрашиваем слово
                reply.append("Какое слово отправил в Wordle?")
                self.__phase = 1
            case 1:  # спрашиваем положение
                if len(message) != 5:
                    reply.append("Пришли слово из 5 букв")
                else:
                    self.__last_answer = message
                    self.__phase = 2
                    reply.append("Что ответил Wordle? \nПришли число из 5 цифр 0, 1 или 2\n"
                                 "0 - буква серая, 1 - желтая, 2 - зеленая")
            case 2:
                if not check_mask(message):
                    reply.append("Неправильная маска, должно быть что-то типа 01102")
                else:
                    green = ['.'] * WORD_LEN
                    yellow = ['.'] * WORD_LEN
                    grey = []
                    for i in range(WORD_LEN):
                        match message[i]:
                            case '0':
                                grey.append(self.__last_answer[i])
                            case '1':
                                yellow[i] = self.__last_answer[i]
                            case '2':
                                green[i] = self.__last_answer[i]
                    self.make_turn(green, yellow, grey)
                    if len(self.__game):
                        reply.extend(self.__game)
                        reply.append("Какое слово отправил в Wordle? (Начать сначала: /start)")
                        self.__phase = 1
                    else:
                        reply.append("Кажется, я не знаю этого слова. (Начать сначала: /start)")
                        self.reset()
        return "".join(reply)


def test():
    games = {}

    while True:
        user = "id"
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
