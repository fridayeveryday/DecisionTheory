import math
import psycopg2
import random
import matplotlib.pyplot as mpl
import numpy as np


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
        cls.__cursor.execute('SELECT * FROM fill_db(%s);', [data_str, ])
        cls.__connection.commit()

    def delete_contents_of_the_table(self):
        self.__cursor.execute("TRUNCATE TABLE \"Data\"")
        self.__connection.commit()

    # return "records" as objects of fetched data
    def get_data(self):
        self.__cursor.execute('SELECT * FROM "public"."Data"')
        records = self.__cursor.fetchall()
        return records


def generate_data(number, el_size):
    counter = 0
    res_str = ""
    while counter < number:
        res_str += str(random.randint(1, el_size)) + " "
        counter += 1
    return res_str.strip()


def check_belonging(data, l_border, r_border):
    if l_border <= data <= r_border:
        return True
    else:
        return False

    # def get_avarage(avarage, new_number):
    # avarage


def process_data(records, range_width, max_val):
    list_of_ranges = [[] for _ in range(max_val // range_width)]
    initial_left_range_border = 1
    if range_width == 1:
        initial_left_range_border = 0
    for row in records:
        left_range_border = initial_left_range_border
        range_num = 0
        while left_range_border < max_val:
            # while range_num < len(list_of_ranges):
            # if check_belonging(row[1], int(range_border), int(range_border + range_width)):
            if check_belonging(row, int(left_range_border), int(left_range_border + range_width)):
                # add elem if it belongs the range
                # list_of_ranges[range_num].append(row[1])

                list_of_ranges[left_range_border // range_width].append(row)
                break
            # range_num += 1
            left_range_border += range_width

    return list_of_ranges


def count_average(range_list):
    for rng_num, rng in enumerate(range_list):
        try:
            range_list[rng_num] = sum(rng) / len(rng)
        except ZeroDivisionError:
            print("was empty range")
    return range_list


def count_number_of_el_in_each_range(range_list):
    for rng_num, rng in enumerate(range_list):
        range_list[rng_num] = len(rng)
    return range_list


def find_probability_of_each_range(range_list, amount_of_elem):
    for value in range(len(range_list)):
        range_list[value] = range_list[value] / amount_of_elem
    return range_list


def main():
    # db_man = Db_manager.get_instance()
    # str = "120 125 159"
    # db_man.insert_data(str)
    # db_man.delete_contents_of_the_table()

    # width of each range
    range_width = 3
    # max value of each elements
    max_value = 10
    # amount rows for db, amount of numbers
    num_of_rows = 12
    # str = string with data splitting by space
    str = generate_data(num_of_rows, max_value).split(" ")
    # raw_res - list of data
    raw_res = [int(el) for el in str]
    a = 2

    # raw_res[0] = 0
    # raw_res = [ 1, 5, 4, 2, 3]

    num_of_rows = len(raw_res)
    # 2d list with devided into ranges
    if max_value // range_width <= 1:
        print("Your range width is too wide than your max value of each elements")
        return
    else:
        raw_res = process_data(raw_res, range_width, max_value)
    # copy of raw_res
    res_as_probability = raw_res[:]
    # counting the average value in each ranges
    res_as_average_in_each_range = count_average(res_as_probability)
    # counting numbers in each range
    res_as_probability = count_number_of_el_in_each_range(raw_res)

    print(res_as_average_in_each_range)
    print(res_as_probability)
    # calculating probability in each ranges
    res_as_probability = find_probability_of_each_range(res_as_probability, num_of_rows)
    # name of each range
    list_of_ranges = ["{}-{}".format(i * range_width + 1, (i + 1) * range_width) for i in range((max_value // range_width))]

    if max_value % range_width != 0:
        list_of_ranges[len(list_of_ranges) - 1] = "{}-{}".format(max_value - range_width, max_value)
    # mpl.bar(list_of_ranges, res_as_probability)
    rounding_accuracy = 2
    # rounding probability of each range
    probability_as_label = [round(el, rounding_accuracy) for el in res_as_probability]

    positions = np.arange(len(res_as_probability))
    figure = mpl.figure()
    axes = figure.gca()
    # width of each bar
    width = 0.99
    axes.bar(positions, res_as_probability, width, tick_label=list_of_ranges,
             align='center')
    y0, y1 = axes.get_ybound()  # размер графика по оси Y

    y_shift = 0.1 * (y1 - y0)  # дополнительное место под надписи

    for i, rect in enumerate(axes.patches):  # по всем нарисованным прямоугольникам
        height = rect.get_height()
        label = probability_as_label[i]
        x = rect.get_x() + rect.get_width() / 2  # посередине прямоугольника
        y = y0 + height + y_shift / 2  # над прямоугольником в середине доп. места
        axes.text(x, y, label, ha='center', va='center')  # выводим текст

    axes.set_ybound(y0, 1) #y1 + y_shift)
    axes.set_title("probability")
    mpl.show()


if __name__ == '__main__':
    # connection = psycopg2.connect(dbname='DT1', user='postgres',
    #                               password='admin', host='localhost')
    # cursor = connection.cursor()
    # data_str = "120 125 159"
    # cursor.execute('SELECT * FROM fill_db(%s);', [data_str,])
    # connection.commit()
    main()
