# 6. Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет»,
# «декоратор». Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести
# его содержимое.


import os

exam = ['сетевое программирование', 'сокет', 'декоратор']

txt = open('text.txt', 'w')
for string in exam:
    txt.write(string + '\n')
txt.close()

txt = open('text.txt', 'r')
print(txt)
txt.close()

txt = open('text.txt', encoding='utf-8')
print(txt)
for string in txt:
    print(string)

os.remove('text.txt')


# для частоты эксперимента я через Sublime поменял кодировку на cp-1251 но файл все равно отображается, как utf-8 и
# при чтении выдает ошибку
# <_io.TextIOWrapper name='text.txt' mode='r' encoding='UTF-8'>
# <_io.TextIOWrapper name='text.txt' mode='r' encoding='utf-8'>
# сетевое программирование
#
# сокет
#
# декоратор
