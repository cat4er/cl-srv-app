from socket import *
import time
import pickle
import json
from threading import Thread
import ast
import secrets
from Crypto.Cipher import AES
from base64 import b64encode, b64decode

port = 8007
sessions = 10
salt = 'SlTKeYOpHygTYkP3'
client_list = {}  # клиенты и их атрибуты
groups = {}  # группы


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
        self.group_id = None

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
        """Метод выхода из чата(закрывает сокет, удаляет клиентскую запись, убивает экземпляр класса и поток)"""
        try:
            client_list.pop(self.guid)
            self.responce([self.guid, 200, f'Пользователь {self.user_name} вышел из чата'])
            time.sleep(1)
            self.client.close()
            del self
        except:
            self.responce([self.guid, 400, 'Ошибка запроса выхода из чата'])

    def __del__(self):
        """нотификация о закрытии сессии"""
        print('Сессия разорвана')
        pass

    def main(self):
        """Транслирует запросы по другим методам"""
        while True:
            data = self.request()
            if 'action' in data.keys():
                action = data.get('action')
                if action == 'registration':
                    print('Что-то пользователь химичит')
                elif action == 'leave':
                    self.leave()
                    exit()
                elif action == 'get_user_list':
                    self.responce(self.get_user_list())
                elif action == 'send_message':
                    self.send_message(data)
                elif action == 'rec_message':
                    self.send_message(data)
                elif action == 'show_group':
                    self.responce(self.show_group())
                elif action == 'open_group':
                    self.responce(self.open_group())
                elif action == 'create_group':
                    self.responce(self.create_group(data))
                elif action == 'exit_of_group':
                    self.responce(self.exit_of_group())
            else:
                print('Такой команды в списке доступных')

    def get_user_list(self):
        """Метод возвращает список доступных пользователей чата"""
        online_list = {}
        for g, v in client_list.items():
            online_list.update({g: {'user_name': v.get('user_name'), 'group': v.get('group')}})
        return self.guid, 200, online_list

    @staticmethod
    def send_message(data):
        """Метод получает сообшение от пользваотеля и направляет его другому пользователю.
        Выполняет роль маршрутизатора"""
        to_client = (client_list.get(int(data.get('to_guid')))).get('socket')
        data.update({'action': 'rec_message'})
        print(data)
        to_client.send(pickle.dumps(json.dumps(data)))

    @staticmethod
    def rec_message(data):
        """Метод получает ответ от пользваотеля на сообщение и направляет его отправителю, как подтверждение.
        Выполняет роль маршрутизатора"""
        to_client = (client_list.get(int(data.get('to_guid')))).get('socket')
        data.update({'action': 'send_message'})
        print(data)
        to_client.send(pickle.dumps(json.dumps(data)))

    def show_group(self):
        """Метод отображения доступных групп"""
        group_list = {}
        for i, v in groups.items():
            group_list.update({i: v.get('group_name')})
        return self.guid, 200, group_list

    def open_group(self, group_id=None, data=None):
        """Метод открытия существующей группы"""
        if group_id:
            if client_list.get(self.guid).get('group') is None:
                client_list.get(self.guid).update({'group': group_id})
                self.group_id = group_id
            else:
                return self.guid, 400, f'Пользователь уже участвует в гурппе {client_list.get(self.guid).get("group")}'
        if data:
            if client_list.get(self.guid).get('group') is None:
                group_id = data.get("group_id")
                client_list.get(self.guid).update({'group': group_id})
                self.group_id = group_id
                return self.guid, 200, f'Группа {groups.get(group_id).get("group_name")} открыта для общения'

    def create_group(self, data):
        """Метод создания группы"""
        gr_id = 1
        while True:
            if gr_id not in groups.keys():
                group_name = data.get("user_group")
                new_group = {
                    gr_id: {'group_name': group_name,
                            'owner_id': self.guid,
                            'owner_name': self.user_name,
                            }
                }
                groups.update(new_group)
                if self.open_group(gr_id):
                    return self.open_group(gr_id)
                break
            else:
                gr_id += 1
        return self.guid, 200, f'Группа {groups.get(gr_id).get("group_name")} готова для общения'

    def exit_of_group(self):
        """Метод выхода из группы"""
        group_id = client_list.get(self.guid).get('group')
        client_list.get(self.guid).update({'group': None})
        return self.guid, 200, f'Вы вышли из группы {group_id}'

    # def check_token():
    """Проверят выданный клиенту токен в каждом реквесте перед обработкой"""
    #     pass


# def check_user(self):
"""Проверяет доступен ли клиент на сервере, и если нет, то закрывает сокет, 
удаляет клиентскую запись, экземплятр класса и поток"""


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
    """Создание уникального токена, буду использовать для проверки сооьщений нужному клиенту"""
    if 'action' in data.keys():
        action = data.get('action')
        if action == 'registration':
            key = secrets.token_bytes(32)
            ecb_token = AES.new(key, AES.MODE_CFB, salt).encrypt(data.get('user'))  # соль не меняется
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
                       'group': None,
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
