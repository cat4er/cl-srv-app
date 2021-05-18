from socket import *
import platform
import hashlib
import pickle
import json
import time

# config
port = 8007

# регистрация имени пользователя
# name_in_chat = input('Введите ваше имя для входа в  чат:  ')
name_in_chat = 'Виктор'

# создание псевдоуникального токена
sys_info = platform.uname()
usr_data = {'system': f'{sys_info[0]}',
            'node': f'{sys_info[1]}',
            'release': f'{sys_info[2]}',
            'version': f'{sys_info[3]}',
            'machine': f'{sys_info[4]}',
            'processor': f'{sys_info[5]}',
            'name_in_chat': f'{name_in_chat}'
            }

hash_usr_data = hashlib.sha256(pickle.dumps(usr_data)).hexdigest()

# Регистрация на сервере


s = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
s.connect(('localhost', port))  # Соединиться с сервером

reg_msg = {
    'action': 'authenticate',
    'time': f'{time.time()}',
    'user': {
        f'{hash_usr_data}': f'{name_in_chat}'
    }
}


def send(socket, msg):
    socket.send(pickle.dumps(json.dumps(msg)))


def load_print(socket):
    data = json.loads(pickle.loads(socket.recv(2048)))
    print('Сообщение от сервера: ', data)


send(s, reg_msg)
load_print(s)

continuer = ''

while continuer.upper() != 'Q':
    print('Введите:\n',
          '"1"- чтобы получить список пользователей в чате\n',
          '"2" - чтобы написать сообщение\n',
          '"Q" - чтобы покинуть чат\n')
    continuer = input(': ')

    if continuer == '1':
        get_list_msg = {
            'action': 'get_user_list',
            'time': f'{time.time()}',
        }
        send(s, get_list_msg)
        load_print(s)
    elif continuer == '2':
        # get_list_msg = {
        #     'action': 'get_user_list',
        #     'time': f'{time.time()}',
        # }
        # s.send(pickle.dumps(json.dumps(get_list_msg)))
        # data = json.loads(pickle.loads(s.recv(2048)))
        # print('Сообщение от сервера: ', data)
        # hash_to_usr = input('hash: ')
        # text_message = input('Введите сообщение пользователю: ')
        send_message_msg = {
            'action': 'send_message',
            'time': f'{time.time()}',
            'user': {
                f'{hash_usr_data}': f'{name_in_chat}',
                # f'{hash_to_usr}': f'{text_message}'
            }
        }
        send(s, send_message_msg)
        load_print(s)
    elif continuer == 'q' or continuer == 'Q':
        leave_msg = {
            'action': 'leave',
            'time': f'{time.time()}',
            'user': {
                f'{hash_usr_data}': f'{name_in_chat}'
            }
        }
        send(s, leave_msg)
        load_print(s)
    else:
        print('Вы ввели значение не из списка')
