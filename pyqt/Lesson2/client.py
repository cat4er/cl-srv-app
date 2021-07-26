from socket import *
from threading import Thread
import platform
import json
import time
from queue import PriorityQueue
from log.client_log_config import logger
from functools import wraps
import inspect
from dis import code_info

# config
port = 7777


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


class ClientVerifier(type):
    def __new__(mcs, class_name, parents, attributes):
        if "socket.socket" in str(attributes):
            print(f'Найден атрибут сокета в классе {class_name}')
        else:
            print(f'Атрибут сокета в классе {class_name} не найден')
        for key, value in attributes.items():
            try:
                if 'socket' in code_info(value):
                    print(f'Найден сокет в функции {key}')
                    if 'SOCK_STREAM' in code_info(value):
                        print('Задан тип соединения TCP')
                    else:
                        print('TCP соединение не задано')
                    if 'accept' and 'listen' not in code_info(value):
                        print('Отсутствуют методы accept и listen')
                        print("---------------------")
                    else:
                        print('Методы accept и listen заданы')
                        print("---------------------")
                else:
                    print(f'Сокет не задан в функции {key}')
                    print("---------------------")
            except:
                print(f'{key} атрибут не подлежит разбору')
        print("--------------------------------------------------")
        return type.__new__(mcs, class_name, parents, attributes)


class Client(metaclass=ClientVerifier):

    @log
    def send(self, msg):
        self.sock.send(json.dumps(msg).encode())

    @log
    def load_print(self):
        data = json.loads(self.sock.recv(2048).decode())
        # print('Сообщение от сервера: ', data)
        return data

    @log
    def registration(self):
        # создание псевдоуникального токена
        sys_info = platform.uname()
        usr_data = {'system': f'{sys_info[0]}',
                    'node': f'{sys_info[1]}',
                    'release': f'{sys_info[2]}',
                    'version': f'{sys_info[3]}',
                    'machine': f'{sys_info[4]}',
                    'processor': f'{sys_info[5]}',
                    'name_in_chat': f'{self.name_in_chat}'
                    }

        reg_msg = {
            'action': 'registration',
            'time': f'{time.time()}',
            'user_name': f'{self.name_in_chat}',
            'user': f'{usr_data}'
        }

        self.send(reg_msg)
        reg_data = self.load_print()
        for k, v in reg_data.items():
            if v.get('response') == 200:
                guid = k
                return guid, usr_data
            else:
                print('Ошибка регистарции')

    @log
    def send_message(self, group=None):

        def create_message(*args):
            send_message_msg = {
                'action': 'send_message',
                'time': f'{time.time()}',
                'from_user_name': f'{self.name_in_chat}',
                'from_guid': f'{self.guid}',
                'to_user_name': f'{to_user_name}',
                'to_guid': f'{to_guid}',
                'message': f'{message}',
            }
            return send_message_msg

        if group is None:
            to_guid = int(input('Введите кому пишем: '))
            message = 'Личное:' + input('Введите ваше ссобщение: ')
            smsg = self.get_list()
            to_user_name = smsg.get(f'{to_guid}').get('user_name')
            self.send(create_message(to_user_name, to_guid, message))

        elif group != 'All' and group is not None:
            message = 'Групповое:' + input('Введите ваше ссобщение: ')
            smsg = self.get_list()
            for to_guid, v in smsg.items():
                if str(v.get('group')) == self.usr_group:
                    to_user_name = v.get('user_name')
                    self.send(create_message(to_user_name, to_guid, message))

        elif group == 'All':
            message = 'Публичное:' + input('Введите ваше ссобщение: ')
            smsg = self.get_list()
            for to_guid, user_data in smsg.items():
                to_user_name = user_data.get('user_name')
                self.send(create_message(to_user_name, to_guid, message))

    def rec_message(self):
        while True:
            self.input_queue.put(self.load_print())
            req = self.input_queue.queue[0].get('action')
            if req == 'rec_message':
                msg = self.input_queue.get()
                if msg.get('response') == 200:
                    pass
                elif 'response' not in msg:
                    print(f'У Вас новое сообщение от {msg.get("from_user_name")}:\n'
                          f'{msg.get("message")}')
                    resp_msg = {
                        'response': 200,
                        'action': 'send_message',
                        'time': f'{time.time()}',
                        'from_user_name': f'{self.name_in_chat}',
                        'from_guid': f'{self.guid}',
                        'to_user_name': f'{msg.get("from_user_name")}',
                        'to_guid': f'{msg.get("from_guid")}',
                        'alert': 'Сообщение доставлено'
                    }
                    self.send(resp_msg)
            elif req == 'ping':
                self.input_queue.get()
                resp_msg = {
                    'response': 200,
                    'action': 'ping',
                    'time': f'{time.time()}',
                    'guid': f'{self.guid}',
                    'alert': 'я тут'
                }
                self.send(resp_msg)
            else:
                pass

    @log
    def get_list(self, group=None):
        get_list_msg = {
            'action': 'get_user_list',
            'time': f'{time.time()}',
            'user_name': f'{self.name_in_chat}',
            'group': group,
            'user': f'{self.usr_data}',
        }
        self.send(get_list_msg)
        msg = self.input_queue.get()
        data = msg.get(f'{self.guid}').get('alert')
        print(data)
        return data

    @log
    def leave(self):
        leave_msg = {
            'action': 'leave',
            'time': f'{time.time()}',
            'user': {
                'user_name': f'{self.name_in_chat}',
                'user': f'{self.usr_data}'
            }
        }
        self.send(leave_msg)
        msg = self.input_queue.get()
        data = msg.get(f'{self.guid}').get('alert')
        print(data)
        exit()

    @log
    def show_group(self):
        get_gr_list_msg = {
            'action': 'show_group',
            'time': f'{time.time()}',
            'user_name': f'{self.name_in_chat}',
            'user': f'{self.usr_data}'
        }
        self.send(get_gr_list_msg)
        msg = self.input_queue.get()
        data = msg.get(f'{self.guid}').get('alert')
        print(data)
        return data

    @log
    def open_group(self):
        self.show_group()
        group_id = int(input('Введите номер группы:  '))
        open_msg = {
            'action': 'open_group',
            'time': f'{time.time()}',
            'user_name': f'{self.name_in_chat}',
            'group_id': group_id,
            'user': f'{self.usr_data}'
        }
        self.send(open_msg)
        msg = self.input_queue.get()
        data = msg.get(f'{self.guid}')
        if data.get('response') == 200:
            self.usr_group = f'{group_id}'
        print(data.get('alert'))

    @log
    def create_group(self):
        group_name = input('Введите название группы:  ')
        create_group_msg = {
            'action': 'create_group',
            'time': f'{time.time()}',
            'user_group': group_name,
            'user_name': f'{self.name_in_chat}',
            'user': f'{self.usr_data}'
        }
        self.send(create_group_msg)
        msg = self.input_queue.get()
        data = msg.get(f'{self.guid}')
        if data.get('response') == 200:
            groups = self.show_group()
            for i, n in groups.items():
                if n == group_name:
                    self.usr_group = i
        print(data.get('alert'))

    @log
    def exit_of_group(self):
        exit_of_group_msg = {
            'action': 'exit_of_group',
            'time': f'{time.time()}',
            'user_name': f'{self.name_in_chat}',
            'user': f'{self.usr_data}'
        }
        self.send(exit_of_group_msg)
        msg = self.input_queue.get()
        data = msg.get(f'{self.guid}').get('alert')
        print(data)

    @log
    def menu(self):
        continuer = ''
        while continuer.upper() != 'Q':
            try:
                print('Введите:\n',
                      '"1"- чтобы получить список пользователей в чате\n',
                      '"2" - чтобы написать сообщение пользователю\n',
                      '"3" - чтобы написать сообщение всем кто в онлайне\n',
                      '"4" - чтобы написать сообщение пользователям в группу\n',
                      '"Q" - чтобы покинуть чат\n')
                continuer = input(': ')

                if continuer == '1':
                    self.get_list()
                elif continuer == '2':
                    self.send_message()
                elif continuer == '3':
                    self.send_message('All')
                elif continuer == '4':
                    while continuer.upper() != 'Q' or 'B':
                        print('Введите:\n',
                              '"1"- чтобы получить список групп\n',
                              '"2" - чтобы войти в группу\n',
                              '"3" - создать группу\n',
                              '"4" - чтобы выйти из группы\n',
                              '"5" - чтобы написать сообщение в группу\n',
                              '"B" - попасть в меню выше\n',
                              '"Q" - чтобы покинуть чат\n')
                        continuer = input(': ')
                        if continuer == '1':
                            self.show_group()
                        elif continuer == '2':
                            self.open_group()
                        elif continuer == '3':
                            self.create_group()
                        elif continuer == '4':
                            self.exit_of_group()
                        elif continuer == '5':
                            self.send_message(self.usr_group)
                        elif continuer == 'b' or continuer == 'B':
                            break
                        elif continuer == 'q' or continuer == 'Q':
                            self.leave()
                elif continuer == 'q' or continuer == 'Q':
                    self.leave()
                else:
                    print('Вы ввели значение не из списка')
            except:
                pass

    def __init__(self):
        """Инициализация потока и атрибутов"""
        # регистрация имени пользователя
        self.name_in_chat = input('Введите ваше имя для входа в  чат:  ')
        self.sock = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
        self.sock.connect(('localhost', port))  # Соединиться с сервером
        self.usr_group = None
        self.input_queue = PriorityQueue()
        self.guid, self.usr_data = self.registration()
        t = Thread(target=self.rec_message)
        t.daemon = True
        t.start()
        self.menu()


if __name__ == "__main__":
    Client()
