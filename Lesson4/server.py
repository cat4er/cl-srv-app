from socket import *
import time
import pickle
import json

# config
port = 8008
sessions = 10
host = 'localhost'


def create_socket(port, host):
    sock = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP
    sock.bind((host, port))  # Присваивает порт
    sock.listen(sessions)  # Ограничивает кол-во сессий
    return sock


s = create_socket(port, host)
client_list = {}  # переделать на запись пользователей в БД
client = None


def main():
    global client
    global s
    if client is None:
        client = s.accept()[0]

    try:
        receive_data = json.loads(pickle.loads(client.recv(2048)))
        request(receive_data)
    except:
        client = None
        print('Ждем подключения')


def authenticate(user_data):
    global client_list  # не люблю так делать, переделаю когда будем писать в БД
    try:
        client_list.update(user_data)
        for k, v in user_data.items():
            return k, 200, f'Пользователь {v} вошел в чат'
    except:
        return k, 400, 'Ошибка запроса аутентификации'


def leave(user_data):
    global client_list
    global client
    try:
        for k, v in user_data.items():
            client_list.pop(k)
            yield k, 200, f'Пользователь {v} вышел из чата'
            client.close()
    except:
        return k, 400, f'Ошибка запроса выхода из чата'



def request(data):
    print(data)
    if 'action' in data.keys():
        action = data.get('action')
        if action == 'authenticate':
            responce(authenticate(data.get('user')))
        if action == 'leave':
            responce(leave(data.get('user')))
        if action == 'get_user_list':
            responce([None, 500, 'Сервис в разработке'])
        if action == 'send_message':
            responce([None, 500, 'Сервис в разработке'])
    else:
        print('Ошибка команды серверу')


def responce(data):
    global client
    answer = {data[0]:
        {
            "response": data[1],
            "alert": data[2]
        }
    }
    print(answer)
    client.send(pickle.dumps(json.dumps(answer)))


"""Перед запуском поменять environment = 'test'"""

environment = 'prod'
if environment == 'test':
    main()
elif environment == 'prod':
    while True:
        main()
