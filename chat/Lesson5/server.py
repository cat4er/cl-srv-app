from socket import *
import time
import pickle
import json
from log.server_log_config import logger

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
        logger.info(f'Получен запрос {receive_data}')
        request(receive_data)
    except:
        client = None
        logger.info('Сервер ждет новых подключений от пользоватлей')
        # print('Ждем подключения')


def authenticate(user_data):
    global client_list  # не люблю так делать, переделаю когда будем писать в БД
    try:
        client_list.update(user_data)
        for k, v in user_data.items():
            logger.info(f'{k}, Пользователь {v} вошел в чат')
            return k, 200, f'Пользователь {v} вошел в чат'
    except:
        logger.error(f'{k}, Ошибка запроса аутентификации')
        return k, 400, 'Ошибка запроса аутентификации'


def leave(user_data):
    global client_list
    global client
    try:
        for k, v in user_data.items():
            client_list.pop(k)
            logger.info(f'{k}, Пользователь {v} вышел из чата')
            yield k, 200, f'Пользователь {v} вышел из чата'
            client.close()
    except:
        logger.error(f'{k}, Ошибка запроса выхода из чата')
        return k, 400, f'Ошибка запроса выхода из чата'


def request(data):
    print(data)
    if 'action' in data.keys():
        action = data.get('action')
        if action == 'authenticate':
            egg = data.get('user')
            logger.info(f'Запуск функции authenticate с запросом {egg}')
            responce(authenticate(egg))
        if action == 'leave':
            egg = data.get('user')
            logger.info(f'Запуск функции leave с запросом {egg}')
            responce(leave(data.get('user')))
        if action == 'get_user_list':
            responce([None, 500, 'Сервис в разработке'])
        if action == 'send_message':
            responce([None, 500, 'Сервис в разработке'])
    else:
        logger.error(f'Ошибка команды серверу: {data}')
        # print('Ошибка команды серверу')


def responce(data):
    global client
    answer = {data[0]:
        {
            "response": data[1],
            "alert": data[2]
        }
    }
    logger.info(f'Отправка ответа на запрос: {answer}')
    client.send(pickle.dumps(json.dumps(answer)))


"""Перед запуском поменять environment = 'test'"""

environment = 'prod'
if environment == 'test':
    logger.warning(f'Сервер запущен в тестовом режиме')
    main()
elif environment == 'prod':
    logger.warning(f'Сервер запущен в продакшен режиме')
    while True:
        main()
