import math
import psycopg2
import random

class Db_manager:
    # __ is private
    __instance = None
    __connection = None
    __cursor = None
    f = 0

    @staticmethod
    def get_instance():
        if Db_manager.__instance is None:
            Db_manager.__instance = Db_manager()
        return Db_manager.__instance

    @classmethod
    def get_connection_and_cursor(cls):
        connection = psycopg2.connect(dbname='DT1', user='postgres',
                                      password='admin', host='localhost')
        cursor = connection.cursor()
        return connection, cursor

    def __init__(self):
        Db_manager.f = 7
        Db_manager.__connection, Db_manager.__cursor = Db_manager.get_connection_and_cursor()

    @classmethod
    def insert_data(cls, data_str):
        g = 9
        h = g
        cls.__cursor.execute('SELECT * FROM fill_db(%s);', [data_str,])
        cls.__connection.commit()

    def delete_contents_of_the_table(self):
        self.__cursor.execute("TRUNCATE TABLE \"Data\"")
        self.__connection.commit()


def generate_data(number):
    counter = 0
    res_str = ""
    while counter < number:
        res_str += str(math.ceil(random.random()*100)) + " "
        counter += 1
    return res_str.strip()




def main():
    # db_man = Db_manager.get_instance()
    # str = "120 125 159"
    # db_man.insert_data(str)
    # db_man.delete_contents_of_the_table()
    num_of_rows = 5
    print(generate_data(num_of_rows))


if __name__ == '__main__':
    # connection = psycopg2.connect(dbname='DT1', user='postgres',
    #                               password='admin', host='localhost')
    # cursor = connection.cursor()
    # data_str = "120 125 159"
    # cursor.execute('SELECT * FROM fill_db(%s);', [data_str,])
    # connection.commit()
    main()
