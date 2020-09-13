import re
import string
from enum import Enum

import psycopg2 as psycopg2

listOfCommonWords = []
db_manager = None
file = None


class spam_degrees(Enum):
    not_spam = 1,
    neutral = 0,
    spam = -1


class oneWord:
    word = ""
    spam = 0
    not_spam = 0

    def __init__(self, word, spam, not_spam):
        self.word = word
        self.spam = spam
        self.not_spam = not_spam


class Db_manager:
    # __ is private
    __instance = None
    __connection = None
    __cursor = None

    @staticmethod
    def get_instance():
        if Db_manager.__instance is None:
            Db_manager.__instance = Db_manager()
        return Db_manager.__instance

    def get_connection_and_cursor(cls):

        connection = psycopg2.connect(dbname='DT3', user='postgres',
                                      password='admin', host='localhost')
        cursor = connection.cursor()
        return connection, cursor

    def __init__(self):
        Db_manager.__connection, Db_manager.__cursor = Db_manager.get_connection_and_cursor(self)

    def update_spam(cls, oneWord):
        word = oneWord.word
        number = cls.__cursor.execute('SELECT spam  FROM data WHERE word = %s', (word,))
        number = cls.__cursor.fetchall()
        number = number[0][0]
        number = 0 if not number else number
        number += 1
        cls.__cursor.execute("Update data SET spam=%s WHERE word = %s", (number, word))
        cls.__connection.commit()

    def update_none_spam(cls, oneWord):
        word = oneWord.word
        number = cls.__cursor.execute('SELECT non_spam  FROM data WHERE word = %s', (word,))
        number = cls.__cursor.fetchall()
        number = number[0][0]
        number = 0 if not number else number
        number += 1
        cls.__cursor.execute('Update data SET non_spam=%s WHERE word = %s', (number, word))
        cls.__connection.commit()

    def insert_data(self, oneWord):
        word = oneWord.word
        isSpam = bool(oneWord.spam)
        data = self.__cursor.execute("""SELECT * FROM data WHERE word = %s""", (word,))
        data = self.__cursor.fetchall()
        if data:
            if isSpam:
                self.update_spam(oneWord)
            else:
                self.update_none_spam(oneWord)
        else:
            if isSpam:
                self.__cursor.execute('INSERT INTO data (word, spam, non_spam) VALUES (%s, %s, %s)', (word, 1, 0))
                self.__connection.commit()
            else:
                self.__cursor.execute('INSERT INTO data (word, spam, non_spam) VALUES (%s, %s, %s)', (word, 0, 1))
                self.__connection.commit()

    def delete_contents_of_the_table(self):
        self.__cursor.execute("TRUNCATE TABLE \"data\"")
        self.__connection.commit()

    # return "records" as objects of fetched data
    def get_data_by_word(self, word):
        self.__cursor.execute('SELECT * FROM "public"."data" where word = %s', (word,))
        records = self.__cursor.fetchall()
        return records

    def set_probability(self, value, word):
        self.__cursor.execute('Update "public"."data" set spam_probability = %s WHERE word = %s', (value, word))


def ask_choice(question, agreement_txt):
    print(question)
    if input() == agreement_txt:
        return True
    else:
        return False


def prepareLine(line):
    line = line.translate(str.maketrans('', '', string.punctuation))
    line = re.sub("[–!\"»«,.?-]", "", line)
    line = line.lower()
    return line


def treatOneLine(line, isSpam):
    line = prepareLine(line)
    words = line.split()
    del words[0]
    for word in words:
        if word in listOfCommonWords:
            continue
        else:
            if isSpam:
                w = oneWord(word, 1, 0)
            else:
                w = oneWord(word, 0, 1)
            db_manager.insert_data(w)


def treat_messages():
    global file
    for line in file:
        if line[0] == "1":
            treatOneLine(line, True)
        else:
            treatOneLine(line, False)


def compute_message_is_spam_probability(message):
    message = prepareLine(message)
    words = message.split()
    probability = 0
    s = 1
    g = 1
    for word in words:
        probability_of_the_word_being_spam = compute_probability_of_one_word(word)
        s *= probability_of_the_word_being_spam
        g *= 1 - probability_of_the_word_being_spam
    return s / (g + s)


def compute_probability_of_one_word(word):
    if word in listOfCommonWords:
        return 0.5
    raw_result = db_manager.get_data_by_word(word)
    count_is_spam = raw_result[0][2]
    count_is_non_spam = raw_result[0][3]
    total = count_is_spam + count_is_non_spam
    probability = count_is_spam / total
    if probability == 1.0 or probability == 0.0:
        return 0.5
    return probability


def main():
    global file, listOfCommonWords, db_manager
    file = open("C:\Temp\DT3.txt", "r")
    listOfCommonWords = file.readline().lower().split()
    print(listOfCommonWords)
    db_manager = None
    try:
        db_manager = Db_manager.get_instance()
    except BaseException:
        print("No database")
    db_manager.delete_contents_of_the_table()
    treat_messages()
    print("Enter a message: \n")
    treating_message = "Дорогой друг! Пришли мне деньги!"
    # treating_message = input()
    print("Enter a spam level (0-1)")
    spam_level = 0.5
    # spam_level = input()
    probability = compute_message_is_spam_probability(treating_message)
    if probability > spam_level:
        print("Your message is a spam.")
    else:
        print("Your message is not a spam.")
    print(probability)


if __name__ == '__main__':
    main()
