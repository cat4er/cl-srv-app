from socket import *
from threading import Thread
import platform
import pickle
import json
import time
from queue import PriorityQueue

# config
port = 8006

# регистрация имени пользователя
# name_in_chat = input('Введите ваше имя для входа в  чат:  ')
name_in_chat = 'Виктор'
usr_group = None


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


def send_message(sock, guid, q, usr_data, group=None):
    def create_message(*args):
        send_message_msg = {
            'action': 'send_message',
            'time': f'{time.time()}',
            'from_user_name': f'{name_in_chat}',
            'from_guid': f'{guid}',
            'to_user_name': f'{to_user_name}',
            'to_guid': f'{to_guid}',
            'message': f'{message}',
        }
        return send_message_msg

    if group is None:
        to_guid = int(input('Введите кому пишем: '))
        message = 'Личное:' + input('Введите ваше ссобщение: ')
        smsg = get_list(sock, guid, q, usr_data)
        to_user_name = smsg.get(f'{to_guid}').get('user_name')
        send(sock, create_message(to_user_name, to_guid, message))

    elif group != 'All' and group is not None:
        message = 'Групповое:' + input('Введите ваше ссобщение: ')
        smsg = get_list(sock, guid, q,  usr_data)
        for to_guid, v in smsg.items():
            if str(v.get('group')) == usr_group:
                to_user_name = v.get('user_name')
                send(sock, create_message(to_user_name, to_guid, message))

    elif group == 'All':
        message = 'Публичное:' + input('Введите ваше ссобщение: ')
        smsg = get_list(sock, guid, q,  usr_data)
        for to_guid, user_data in smsg.items():
            to_user_name = user_data.get('user_name')
            send(sock, create_message(to_user_name, to_guid, message))


def rec_message(sock, guid, q):
    while True:
        q.put(load_print(sock))
        req = q.queue[0].get('action')
        if req == 'rec_message':
            msg = q.get()
            if msg.get('response') == 200:
                pass
            elif 'response' not in msg:
                print(f'У Вас новое сообщение от {msg.get("from_user_name")}:\n'
                      f'{msg.get("message")}')
                resp_msg = {
                    'response': 200,
                    'action': 'send_message',
                    'time': f'{time.time()}',
                    'from_user_name': f'{name_in_chat}',
                    'from_guid': f'{guid}',
                    'to_user_name': f'{msg.get("from_user_name")}',
                    'to_guid': f'{msg.get("from_guid")}',
                    'alert': 'Сообщение доставлено'
                }
                send(sock, resp_msg)
        elif req == 'ping':
            q.get()
            resp_msg = {
                'response': 200,
                'action': 'ping',
                'time': f'{time.time()}',
                'guid': f'{guid}',
                'alert': 'я тут'
            }
            send(sock, resp_msg)
        else:
            pass


def get_list(sock, guid, q, usr_data, group=None):
    get_list_msg = {
        'action': 'get_user_list',
        'time': f'{time.time()}',
        'user_name': f'{name_in_chat}',
        'group': group,
        'user': f'{usr_data}',
    }
    send(sock, get_list_msg)
    msg = q.get()
    data = msg.get(f'{guid}').get('alert')
    print(data)
    return data


def leave(sock, guid, q,  usr_data):
    leave_msg = {
        'action': 'leave',
        'time': f'{time.time()}',
        'user': {
            'user_name': f'{name_in_chat}',
            'user': f'{usr_data}'
        }
    }
    send(sock, leave_msg)
    msg = q.get()
    data = msg.get(f'{guid}').get('alert')
    print(data)
    exit()


def show_group(sock, guid, q, usr_data):
    get_gr_list_msg = {
        'action': 'show_group',
        'time': f'{time.time()}',
        'user_name': f'{name_in_chat}',
        'user': f'{usr_data}'
    }
    send(sock, get_gr_list_msg)
    msg = q.get()
    data = msg.get(f'{guid}').get('alert')
    print(data)
    return data


def open_group(sock, guid, q, usr_data):
    global usr_group
    show_group(sock, guid, q, usr_data)
    group_id = int(input('Введите номер группы:  '))
    open_msg = {
        'action': 'open_group',
        'time': f'{time.time()}',
        'user_name': f'{name_in_chat}',
        'group_id': group_id,
        'user': f'{usr_data}'
    }
    send(sock, open_msg)
    msg = q.get()
    data = msg.get(f'{guid}')
    if data.get('response') == 200:
        usr_group = f'{group_id}'
    print(data.get('alert'))


def create_group(sock, guid, q, usr_data):
    global usr_group
    group_name = input('Введите название группы:  ')
    create_group_msg = {
        'action': 'create_group',
        'time': f'{time.time()}',
        'user_group': group_name,
        'user_name': f'{name_in_chat}',
        'user': f'{usr_data}'
    }
    send(sock, create_group_msg)
    msg = q.get()
    data = msg.get(f'{guid}')
    if data.get('response') == 200:
        groups = show_group(sock, guid, q, usr_data)
        for i, n in groups.items():
            if n == group_name:
                usr_group = i
    print(data.get('alert'))


def exit_of_group(sock, guid, q,  usr_data):
    exit_of_group_msg = {
        'action': 'exit_of_group',
        'time': f'{time.time()}',
        'user_name': f'{name_in_chat}',
        'user': f'{usr_data}'
    }
    send(sock, exit_of_group_msg)
    msg = q.get()
    data = msg.get(f'{guid}').get('alert')
    print(data)


def menu(sock, guid, usr_data, q):
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
                get_list(sock, guid, q,  usr_data)
            elif continuer == '2':
                send_message(sock, guid, q,  usr_data)
            elif continuer == '3':
                send_message(sock, guid, q,  usr_data, 'All')
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
                        show_group(sock, guid, q, usr_data)
                    elif continuer == '2':
                        open_group(sock, guid, q,  usr_data)
                    elif continuer == '3':
                        create_group(sock, guid, q,  usr_data)
                    elif continuer == '4':
                        exit_of_group(sock, guid, q, usr_data)
                    elif continuer == '5':
                        send_message(sock, guid, q,  usr_data, usr_group)
                    elif continuer == 'b' or continuer == 'B':
                        break
                    elif continuer == 'q' or continuer == 'Q':
                        leave(sock, guid, q,  usr_data)
            elif continuer == 'q' or continuer == 'Q':
                leave(sock, guid, q,  usr_data)
            else:
                print('Вы ввели значение не из списка')
        except:
            pass


def main():
    input_queue = PriorityQueue()
    s, guid, usr_data = registration()
    t = Thread(target=rec_message, args=(s, guid, input_queue))
    t.daemon = True
    t.start()
    menu(s, guid, usr_data, input_queue)


if __name__ == "__main__":
    main()
