from socket import *
import time
import json
from threading import Thread
import ast
import secrets
from Crypto.Cipher import AES
from base64 import b64encode, b64decode
import select
from log.server_log_config import logger
from functools import wraps
import inspect
from dis import code_info

sessions = 10
salt = 'SlTKeYOpHygTYkP3'
client_list = {}  # клиенты и их атрибуты
groups = {}  # группы клиентов


def log(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if args or kwargs:
            logger.info(
                f'Функция  {func.__name__} вызвана из функции {inspect.stack()[1][3]} с аргументами {args or kwargs}')
            return func(*args, **kwargs)
        if not args and kwargs:
            logger.info(f'Функция  {func.__name__} вызвана из функции {inspect.stack()[1][3]} без аргументов')
            return func

    return decorated


class ServerVerifier(type):
    def __new__(mcs, class_name, parents, attributes):
        for key, value in attributes.items():
            try:
                if 'socket' in code_info(value):
                    print(f'Найден сокет в функции {key}')
                    if 'SOCK_STREAM' in code_info(value):
                        print('Задан тип соединения TCP')
                    else:
                        print('TCP соединение не задано')
                    if 'connect' not in code_info(value):
                        print('Отсутствует метод connect')
                        print("---------------------")
                    else:
                        print('Метод connect задан')
                        print("---------------------")
                else:
                    print(f'Сокет не задан в функции {key}')
                    print("---------------------")
            except:
                print(f'{key} атрибут не подлежит разбору')
        print("--------------------------------------------------")
        return type.__new__(mcs, class_name, parents, attributes)


class Port:
    def __init__(self):
        self._port = None
        self.default = 7777

    def __get__(self, instance, instance_type):
        return self._port

    def __set__(self, instance, port):
        try:
            if not (0 < port <= 65535):
                port = self.default
        except ValueError:
            print(f'Порт для соединения должен быть в диапазоне от 1 до 65535, задан поумолчанию {self.default}')
        finally:
            self._port = port


class Chat(Thread, metaclass=ServerVerifier):
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

    def response(self, data):
        """Метод отправки унифицированного ответа"""
        answer = {data[0]:
            {
                "response": data[1],
                'time': f'{time.time()}',
                "alert": data[2]
            }
        }
        self.client.send(json.dumps(answer).encode())

    def request(self):
        """Метод получения запроса"""
        data = json.loads(self.client.recv(2048).decode())
        return data

    def leave(self):
        """Метод выхода из чата(закрывает сокет, удаляет клиентскую запись, убивает экземпляр класса и поток)"""
        try:
            client_list.pop(self.guid)
            self.response([self.guid, 200, f'Пользователь {self.user_name} вышел из чата'])
            time.sleep(1)
            self.client.close()
            del self
        except:
            self.response([self.guid, 400, 'Ошибка запроса выхода из чата'])

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
                    self.response(self.get_user_list())
                elif action == 'send_message':
                    self.send_message(data)
                elif action == 'rec_message':
                    self.rec_message(data)
                elif action == 'show_group':
                    self.response(self.show_group())
                elif action == 'open_group':
                    self.response(self.open_group(None, data))
                elif action == 'create_group':
                    self.response(self.create_group(data))
                elif action == 'exit_of_group':
                    self.response(self.exit_of_group())
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
        to_client.send(json.dumps(data).encode())

    @staticmethod
    def rec_message(data):
        """Метод получает ответ от пользваотеля на сообщение и направляет его отправителю, как подтверждение.
        Выполняет роль маршрутизатора"""
        to_client = (client_list.get(int(data.get('to_guid')))).get('socket')
        data.update({'action': 'send_message'})
        print(data)
        to_client.send(json.dumps(data).encode())

    def show_group(self):
        """Метод отображения доступных групп"""
        group_list = {}
        for i, v in groups.items():
            group_list.update({i: v.get('group_name')})
        return self.guid, 200, group_list

    def open_group(self, group_id=None, data=None):
        """Метод открытия существующей группы"""
        if group_id is not None:
            if client_list.get(self.guid).get('group') is None:
                client_list.get(self.guid).update({'group': group_id})
                self.group_id = group_id
            else:
                return self.guid, 400, f'Пользователь уже участвует в гурппе {client_list.get(self.guid).get("group")}'
        if data is not None:
            if client_list.get(self.guid).get('group') is None:
                group_id = data.get('group_id')
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
                if self.open_group(gr_id, None):
                    return self.open_group(gr_id, None)
                break
            else:
                gr_id += 1
        return self.guid, 200, f'Группа {groups.get(gr_id).get("group_name")} готова для общения'

    @log
    def exit_of_group(self):
        """Метод выхода из группы"""
        group_id = client_list.get(self.guid).get('group')
        client_list.get(self.guid).update({'group': None})
        return self.guid, 200, f'Вы вышли из группы {group_id}'

    # def check_token():
    """Проверят выданный клиенту токен в каждом реквесте перед обработкой"""
    #     pass


class Main(metaclass=ServerVerifier):
    port = Port()

    def __init__(self, cl_list, sess, slt):
        self.sessions = sess
        self.salt = slt
        self.client_list = cl_list  # клиенты и их атрибуты

    def run(self):
        self.main()
        print('Проверки прошлиб запускаем сервер')

    def check_user(self):
        """Проверяет доступен ли клиент на сервере, и если нет, то закрывает сокет,
        удаляет клиентскую запись, экземплятр класса и поток"""
        while True:
            if self.client_list:
                for guid, v in self.client_list.items():
                    token = v.get('token')
                    client = v.get('socket')
                    ping = {
                        'action': 'ping',
                        'time': f'{time.time()}',
                        guid: token}
                    client.send(json.dumps(ping))
                    try:
                        ready = select.select([client], [], [], 5)
                        if ready[0]:
                            response = json.loads(client.recv(2048).decode())
                            if response.get('response') == 200 and response.get('action') == 'ping':
                                time.sleep(10)
                    except:
                        client.close()
                        self.client_list.pop(guid)
                        time.sleep(10)

    def tokenization(self, data):
        """Создание уникального токена, буду использовать для проверки сообщений нужному клиенту"""
        if 'action' in data.keys():
            action = data.get('action')
            if action == 'registration':
                key = secrets.token_bytes(32)
                ecb_token = AES.new(key, AES.MODE_CFB, self.salt).encrypt(data.get('user'))  # соль не меняется
                edata = b64encode(ecb_token)

                return edata, key

    @staticmethod
    def create_thread(guid, token, key, client, user_name):
        """Создание отдельно потока с экземпляром класса: 1 клиент = 1 поток"""
        name = "Chat_%s" % guid
        thread = Chat(name, token, key, client, guid, user_name)
        thread.daemon = True
        thread.start()

    def registration(self, client, data):
        """Запись в словарь основных данных по классу: id, token, socket, имя пользователя"""
        user_name = dict(ast.literal_eval(data.get('user'))).get('name_in_chat')

        token, key = self.tokenization(data)

        guid = 1
        while guid <= self.sessions:
            if guid not in self.client_list.keys():
                new_user = {
                    guid: {'user_name': f'{user_name}',
                           'socket': client,
                           'token': token,
                           'pub_key': key,
                           'group': None,
                           }
                }
                self.client_list.update(new_user)
                break
            else:
                guid += 1

        client.send(json.dumps({guid:
            {
                "response": 200,
                'time': f'{time.time()}',
                "alert": f'{guid, user_name} подключен'
            }
        }).encode())
        print(f'{guid, user_name} подключен')

        self.create_thread(guid, token, key, client, user_name)

    def main(self, testing=False):
        """Задача функции: открыть сессию, зарегистрировать пользователя"""
        s = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP
        s.bind(('localhost', self.port))  # Присваивает порт
        s.listen(self.sessions)  # Ограничивает кол-во сессий
        client = None
        if testing:
            if client is None:
                client = s.accept()[0]

            receive_data = json.loads(client.recv(2048).decode())
            self.registration(client, receive_data)
            p = Thread(target=self.check_user)
            p.daemon = True
            p.start()
        else:
            while True:
                if client is None:
                    client = s.accept()[0]

                receive_data = json.loads(client.recv(2048).decode())
                self.registration(client, receive_data)
                client = None


if __name__ == "__main__":
    serv = Main(client_list, sessions, salt)
    serv.port = -8007
    print(serv.port)
    serv.run()

