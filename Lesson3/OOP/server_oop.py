from socket import *
import time
import pickle
import json
from threading import Thread
import ast
import secrets
from Crypto.Cipher import AES
from base64 import b64encode, b64decode

port = 8006
sessions = 10
client_list = {}  # переделать на запись пользователей в БД


class Chat(Thread):
    """Задача класса отпочковаться, получить сессию сокета и слушать ее до закрытия"""

    def __init__(self, name, token, key, client, guid, user_name):
        """Инициализация потока и атрибутов"""
        super().__init__()
        self.client = client
        self.key = key
        self.user_name = user_name
        self.name = name
        self.token = token
        self.guid = guid

    def run(self):
        """Запуск потока"""
        print(f'Запуск потока для {self.name, self.token,}')
        self.main()

    def responce(self, data):
        """Метод отправки унифицированного ответа"""
        answer = {data[0]:
            {
                "response": data[1],
                'time': f'{time.time()}',
                "alert": data[2]
            }
        }
        self.client.send(pickle.dumps(json.dumps(answer)))

    def request(self):
        """Метод получения запроса"""
        data = json.loads(pickle.loads(self.client.recv(2048)))
        return data

    def leave(self):
        try:
            client_list.pop(f'{self.guid}')
            self.responce([self.guid, 200, f'Пользователь {self.user_name} вышел из чата'])
            time.sleep(1)
            self.client.close()
            del self
        except:
            self.responce([self.guid, 400, 'Ошибка запроса выхода из чата'])

    def __del__(self):
        print('Сессия разорвана')
        pass

    def main(self):
        """Транслирует запросы по другим методам"""
        while True:
            data = self.request()
            if 'action' in data.keys():
                action = data.get('action')
                if action == 'registration':
                    pass
                elif action == 'leave':
                    self.leave()
                    exit()
                elif action == 'get_user_list':
                    self.responce(self.get_user_list())
                elif action == 'send_message':
                    self.send_message(data)
                elif action == 'rec_message':
                    self.send_message(data)
            else:
                print('Такой команды в классе нет')

    def get_user_list(self):
        """Метод возвращает список доступных пользователей чата"""
        online_list = {}
        for g, v in client_list.items():
            online_list.update({g: v.get('user_name')})
        return self.guid, 200, online_list

    @staticmethod
    def send_message(data):
        """Метод получает сообшение от пользваотеля и направляет его другому пользователю"""
        to_client = (client_list.get(int(data.get('to_guid')))).get('socket')
        data.update({'action': 'rec_message'})
        print(data)
        to_client.send(pickle.dumps(json.dumps(data)))

    @staticmethod
    def rec_message(data):
        """Метод получает ответ от пользваотеля на сообщение и направляет его отправителю, как подтверждение"""
        to_client = (client_list.get(int(data.get('to_guid')))).get('socket')
        data.update({'action': 'send_message'})
        print(data)
        to_client.send(pickle.dumps(json.dumps(data)))


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


def tokenization(data):
    """Создание уникального токена"""
    if 'action' in data.keys():
        action = data.get('action')
        if action == 'registration':
            key = secrets.token_bytes(32)
            ecb_token = AES.new(key, AES.MODE_CFB, 'SlTKeYOpHygTYkP3').encrypt(data.get('user'))  # соль не меняется
            edata = b64encode(ecb_token)

            return edata, key


def registration(client, data):
    global client_list
    """Запись в словарь основных данных по классу: id, token, socket, имя пользователя"""
    user_name = dict(ast.literal_eval(data.get('user'))).get('name_in_chat')

    token, key = tokenization(data)

    guid = 1
    while guid <= sessions:
        if guid not in client_list.keys():
            new_user = {
                guid: {'user_name': f'{user_name}',
                       'socket': client,
                       'token': f'{token}',
                       'pub_key': f'{key}',
                       }
            }
            client_list.update(new_user)
            break
        else:
            guid += 1

    client.send(pickle.dumps(json.dumps({guid:
        {
            "response": 200,
            'time': f'{time.time()}',
            "alert": f'{guid, user_name} подключен'
        }
    })))
    print(f'{guid, user_name} подключен')

    create_thread(guid, token, key, client, user_name)


def create_thread(guid, token, key, client, user_name):
    """Создание отдельно потока с экземпляром класса: 1 клиент = 1 поток"""
    name = "Chat_%s" % guid
    thread = Chat(name, token, key, client, guid, user_name)
    thread.daemon = True
    thread.start()


def main(testing=False):
    """Задача функции: открыть сессию, зарегистрировать пользователя"""
    s = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP
    s.bind(('localhost', port))  # Присваивает порт
    s.listen(sessions)  # Ограничивает кол-во сессий
    client = None
    if testing:
        if client is None:
            client = s.accept()[0]

        receive_data = json.loads(pickle.loads(client.recv(2048)))
        registration(client, receive_data)
    else:
        while True:
            if client is None:
                client = s.accept()[0]

            receive_data = json.loads(pickle.loads(client.recv(2048)))
            registration(client, receive_data)
            client = None


if __name__ == "__main__":
    main()
