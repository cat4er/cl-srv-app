from socket import *
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

# Регистрация на сервере


s = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
s.connect(('localhost', port))  # Соединиться с сервером

reg_msg = {
    'action': 'registration',
    'time': f'{time.time()}',
    'user_name': f'{name_in_chat}',
    'user': f'{usr_data}'
}


def send(socket, msg):
    socket.send(pickle.dumps(json.dumps(msg)))


def load_print(socket):
    data = json.loads(pickle.loads(socket.recv(2048)))
    print('Сообщение от сервера: ', data)
    return data


send(s, reg_msg)
reg_data = load_print(s)
for k, v in reg_data.items():
    if v.get('response') == 200:
        guid = k
    else:
        print('Ошибка регистарции')

continuer = ''

while continuer.upper() != 'Q':
    try:
        ready = select.select([s], [], [], 1)
        if ready[0]:
            msg = load_print(s)
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
                send(s, resp_msg)

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
            get_list_msg = {
                'action': 'get_user_list',
                'time': f'{time.time()}',
                'user_name': f'{name_in_chat}',
                'user': f'{usr_data}'
            }
            send(s, get_list_msg)
            data = load_print(s).get(f'{guid}').get('alert')
            print(data)
        elif continuer == '2':
            to_guid = int(input('Введите кому пишем: '))
            message = input('Введите ваше ссобщение пишем: ')
            get_list_msg = {
                'action': 'get_user_list',
                'time': f'{time.time()}',
                'user_name': f'{name_in_chat}',
                'user': f'{usr_data}'
            }
            send(s, get_list_msg)
            smsg = load_print(s)
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
            send(s, send_message_msg)
            load_print(s)
        elif continuer == '3':
            message = input('Введите ваше ссобщение пишем: ')
            get_list_msg = {
                'action': 'get_user_list',
                'time': f'{time.time()}',
                'user_name': f'{name_in_chat}',
                'user': f'{usr_data}'
            }
            send(s, get_list_msg)
            smsg = load_print(s)
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
                send(s, send_message_msg)
        elif continuer == 'q' or continuer == 'Q':
            leave_msg = {
                'action': 'leave',
                'time': f'{time.time()}',
                'user': {
                    'user_name': f'{name_in_chat}',
                    'user': f'{usr_data}'
                }
            }
            send(s, leave_msg)
            load_print(s)
            exit()
        else:
            print('Вы ввели значение не из списка')
