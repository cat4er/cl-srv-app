# 1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных
# из файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV. Для этого:
# Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и
# считывание данных. В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь значения
# параметров «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения каждого параметра
# поместить в соответствующий список. Должно получиться четыре списка — например, os_prod_list, os_name_list,
# os_code_list, os_type_list. В этой же функции создать главный список для хранения данных отчета — например,
# main_data — и поместить в него названия столбцов отчета в виде списка: «Изготовитель системы», «Название ОС»,
# «Код продукта», «Тип системы». Значения для этих столбцов также оформить в виде списка и поместить в файл
# main_data (также для каждого файла);
# Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение
# данных через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл;
# Проверить работу программы через вызов функции write_to_csv().

import csv
import re

files = ['info_1.txt', 'info_2.txt', 'info_3.txt']


def get_data(arg):
    os_prod_list, os_name_list, os_code_list, os_type_list = [], [], [], []
    for file in arg:
        with open(f'{file}', encoding='cp1251') as f_n:
            for row in f_n:  # если не делать 4 разных списка, то уже здесь можно формировать список
                if re.findall(r'Изготовитель системы', row):
                    os_prod_list.append(re.sub(r'^\s+|\n|\r|\s+$', '', re.findall(r'Изготовитель системы:(\s.*)', row)[0]))
                if re.findall(r'Название ОС', row):
                    os_name_list.append(re.sub(r'^\s+|\n|\r|\s+$', '', re.findall(r'Название ОС:(\s.*)', row)[0]))
                if re.findall(r'Код продукта', row):
                    os_code_list.append(re.sub(r'^\s+|\n|\r|\s+$', '', re.findall(r'Код продукта:(\s.*)', row)[0]))
                if re.findall(r'Тип системы', row):
                    os_type_list.append(re.sub(r'^\s+|\n|\r|\s+$', '', re.findall(r'Тип системы:(\s.*)', row)[0]))
    main_data = [['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']]
    for i in range(0, len(main_data[0]) - 1):   # цикл по длине хидера
        row = [
            f'{os_prod_list[i]}',
            f'{os_name_list[i]}',
            f'{os_code_list[i]}',
            f'{os_type_list[i]}'
        ]   # делаем строку по столбцу из хидера
        main_data.append(row)
    return main_data


def write_to_csv(data):
    new_file = open('dataset.csv', 'w')
    f_n_writer = csv.writer(new_file)
    for row in data:
        f_n_writer.writerow(row)


write_to_csv(get_data(files))