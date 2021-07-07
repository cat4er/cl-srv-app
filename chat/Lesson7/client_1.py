from socket import *
from threading import Thread
import platform
import select
import pickle
import json
import time

# config
port = 8007

# регистрация имени пользователя
# name_in_chat = input('Введите ваше имя для входа в  чат:  ')
name_in_chat = 'Алена'


def send(socket, msg):
    socket.send(pickle.dumps(json.dumps(msg)))


def load_print(socket):
    data = json.loads(pickle.loads(socket.recv(2048)))
    # print('Сообщение от сервера: ', data)
    return data


def registration():
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

    s = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
    s.connect(('localhost', port))  # Соединиться с сервером

    reg_msg = {
        'action': 'registration',
        'time': f'{time.time()}',
        'user_name': f'{name_in_chat}',
        'user': f'{usr_data}'
    }

    send(s, reg_msg)
    reg_data = load_print(s)
    for k, v in reg_data.items():
        if v.get('response') == 200:
            guid = k
            return s, guid, usr_data
        else:
            print('Ошибка регистарции')


def send_message(sock, guid, usr_data):

    to_guid = int(input('Введите кому пишем: '))
    message = input('Введите ваше ссобщение пишем: ')
    get_list_msg = {
        'action': 'get_user_list',
        'time': f'{time.time()}',
        'user_name': f'{name_in_chat}',
        'user': f'{usr_data}'
    }
    send(sock, get_list_msg)
    smsg = load_print(sock)
    to_user_name = smsg.get(f'{guid}').get('alert').get(f'{to_guid}')
    send_message_msg = {
        'action': 'send_message',
        'time': f'{time.time()}',
        'from_user_name': f'{name_in_chat}',
        'from_guid': f'{guid}',
        'to_user_name': f'{to_user_name}',
        'to_guid': f'{to_guid}',
        'message': f'{message}',
    }
    send(sock, send_message_msg)
    load_print(sock)


def rec_message(sock, guid, usr_data):

    ready = select.select([sock], [], [], 1)
    if ready[0]:
        msg = load_print(sock)
        if msg.get('action') == 'rec_message':
            print(f'У Вас новое сообщение от {msg.get("from_user_name")}:\n'
                  f'{msg.get("message")}')

            resp_msg = {
                'action': 'send_message',
                'time': f'{time.time()}',
                'from_user_name': f'{name_in_chat}',
                'from_guid': f'{guid}',
                'to_user_name': f'{msg.get("from_user_name")}',
                'to_guid': f'{msg.get("from_guid")}',
            }
            send(sock, resp_msg)


def get_list(sock, guid, usr_data):
    get_list_msg = {
        'action': 'get_user_list',
        'time': f'{time.time()}',
        'user_name': f'{name_in_chat}',
        'user': f'{usr_data}'
    }
    send(sock, get_list_msg)
    data = load_print(sock).get(f'{guid}').get('alert')
    print(data)


def leave(sock, guid, usr_data):
    leave_msg = {
        'action': 'leave',
        'time': f'{time.time()}',
        'user': {
            'user_name': f'{name_in_chat}',
            'user': f'{usr_data}'
        }
    }
    send(sock, leave_msg)
    load_print(sock)
    exit()


def send_message2all(sock, guid, usr_data):
    message = input('Введите ваше ссобщение пишем: ')
    get_list_msg = {
        'action': 'get_user_list',
        'time': f'{time.time()}',
        'user_name': f'{name_in_chat}',
        'user': f'{usr_data}'
    }
    send(sock, get_list_msg)
    smsg = load_print(sock)
    for to_guid, to_user_name in smsg.get(f'{guid}').get('alert').items():
        send_message_msg = {
            'action': 'send_message',
            'time': f'{time.time()}',
            'from_user_name': f'{name_in_chat}',
            'from_guid': f'{guid}',
            'to_user_name': f'{to_user_name}',
            'to_guid': f'{to_guid}',
            'message': f'{message}',
        }
        send(sock, send_message_msg)


def main():
    continuer = ''
    s, guid, usr_data = registration()
    while continuer.upper() != 'Q':
        try:
            # rec_message(s, guid, usr_data)
            t = Thread(target=rec_message, args=(s, guid, usr_data))
            t.daemon = True
            t.start()
        except:
            pass
        finally:
            print('Введите:\n',
                  '"1"- чтобы получить список пользователей в чате\n',
                  '"2" - чтобы написать сообщение пользователю\n',
                  '"3" - чтобы написать сообщение всем кто в онлайне\n',
                  '"Q" - чтобы покинуть чат\n')
            continuer = input(': ')

            if continuer == '1':
                get_list(s, guid, usr_data)
            elif continuer == '2':
                send_message(s, guid, usr_data)
            elif continuer == '3':
                send_message2all(s, guid, usr_data)
            elif continuer == 'q' or continuer == 'Q':
                leave(s, guid, usr_data)
            else:
                print('Вы ввели значение не из списка')


if __name__ == "__main__":
    main()