from socket import *
import time
import pickle
import json
from threading import Thread
import ast
from Crypto.Cipher import AES


class Chat(Thread):
    """Задача класса отпочковаться, получить сессию сокета и слушать ее до закрытия"""
    def __init__(self, hash, client, user_name):
        """Инициализация потока и атрибутов"""
        Thread.__init__(self)
        self.client = client
        self.request = request
        self.user_name = user_name
        self.hash = hash
        main()

    def run(self):
        """Запуск потока"""
        print(f'Запуск потока для {self.hash}')

    @staticmethod
    def main():
        """Транслирует запросы по другим методам"""
        while True:
            request = json.loads(pickle.loads(client.recv(2048)))
            if 'action' in request.keys():
                action = data.get('action')
                if action == 'registration':
                    pass
                elif action == 'leave':
                    responce(leave(data.get('user')))
                elif action == 'get_user_list':
                    responce([None, 500, 'Сервис в разработке'])
                elif action == 'send_message':
                    responce([None, 500, 'Сервис в разработке'])
            else:
                print('Такой команды в классе нет')


    # def check_user(self):
    #     ping = {
    #         'action': 'ping',
    #         'time': f'{time.time()}',
    #         'user': {
    #             f'{hash_usr_data}': f'{name_in_chat}'
    #         }
    #     }
    #     for k, v in client_list.items():
    #         v[0].send(pickle.dumps(json.dumps(ping)))
    #         time.sleep(60)
    #         try:
    #             responce = json.loads(pickle.loads(v[0].recv(2048)))
    #         except:
    #             v[0].close()
    #             client_list.pop(k)


    def leave(self, user_data):
        try:
            for k, v in user_data.items():
                client_list.pop(k)
                return k, 200, f'Пользователь {v} вышел из чата'
            client.close()
        except:
            return k, 400, f'Ошибка запроса выхода из чата'
            client.close()
            del self

    def __del__(self):
        print('Сессия разорвана')
        pass


    def responce(self, data):
        """Метод отправки унифицированного ответа"""
        answer = {data[0]:
            {
                "response": data[1],
                "alert": data[2]
            }
        }
        client.send(pickle.dumps(json.dumps(answer)))



port = 8007
sessions = 10


s = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP
s.bind(('localhost', port))  # Присваивает порт
s.listen(sessions)  # Ограничивает кол-во сессий
client_list = {}  # переделать на запись пользователей в БД
client = None

while True:
    """Задача функции: открыть сессию, зарегистрировать пользователя"""
    if client is None:
        client = s.accept()[0]

    def tokenization(data):
        """Создание уникального токена"""
        if 'action' in data.keys():
            action = data.get('action')
            if action == 'registration':
                user_name = dict(ast.literal_eval(data.get('user'))).get('name_in_chat')
                token = hashlib.sha256(pickle.dumps(data.get('user'))).hexdigest()  # тут при желании можно еще посолить
            return token, user_name


    def registration(data):
        """Создание отдельно потока с экземпляром класса: 1 клиент = 1 поток,
        и запись в словарь основных данных по классу: id, token, socket, имя пользователя
        """


    eval(compile(f'{hash} = Chat({hash, client, user_name })'))
    eval(compile(f'{hash}.start()'))
    # try:
    receive_data = json.loads(pickle.loads(client.recv(2048)))
    registration(client, receive_data)
    client.send(pickle.dumps(f'{user_name, hash} подключен'))
    client = None
    print(f'{user_name, hash} подключен')
    # except:
    #     print('Ждем подключения')
