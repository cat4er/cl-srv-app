# ### 2. Задание на закрепление знаний по модулю json.
# Есть файл orders в формате JSON с информацией о заказах. Написать скрипт, автоматизирующий его заполнение данными.
# Для этого:
# Создать функцию write_order_to_json(), в которую передается 5 параметров — товар (item), количество (quantity),
# цена (price), покупатель (buyer), дата (date). Функция должна предусматривать запись данных в виде словаря
# в файл orders.json. При записи данных указать величину отступа в 4 пробельных символа;
# Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра.

import json


i = 'Macbook Pro m1 16Gb 1TB'
q = 1
p = 199990
b = 'Victor Pavlyuk'
d = '17.12.2021'


def write_order_to_json(item, quantity, price, buyer, date):
    with open('orders.json') as f_n:  # будем вставлять данные только в раздел orders, а не пересоздавать файл заново
        f_n_content = f_n.read()
        obj = json.loads(f_n_content)
        obj.update({'orders': [
            {'item': item},
            {'quantity': quantity},
            {'price': price},
            {'buyer': buyer},
            {'date': date}
        ]})  # для теста добавил в файл разделы buyer, lead
        with open('orders.json', 'w') as f_d:
            json.dump(obj, f_d, indent=4)


write_order_to_json(i, q, p, b, d)