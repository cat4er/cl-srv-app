from socket import *
from threading import Thread
import platform
import json
from datetime import datetime
from queue import PriorityQueue
from log.client_log_config import logger
from functools import wraps
import inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

# config
PORT = 8007

Base = declarative_base()


class Message(Base):
    __tablename__ = 'messages'
    message_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    from_user_id = Column(Integer, index=True)
    to_user_id = Column(Integer, index=True)
    text_message = Column(Text)
    create_time = Column(DateTime)


class Group(Base):
    __tablename__ = 'groups'
    group_id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String, index=True)
    owner_user_id = Column(Integer, index=True)
    create_time = Column(DateTime)


class Storage:
    """Класс методов по управлению хранилищем"""

    def __init__(self, session):
        self.session = session

    def save_message(self, from_user_id, to_user_id, text_message, create_time=datetime.now()):
        """метод добавления нового сообщения в БД"""
        new_message = Message(from_user_id=from_user_id, to_user_id=to_user_id, text_message=text_message,
                              create_time=create_time)
        self.session.add(new_message)
        self.session.commit()
        return new_message

    def read_messages(self, guid):
        """метод чтения сообщений пользователя из БД"""
        message_list = self.session.query(Message).filter_by(from_user_id=guid, to_user_id=guid).all()
        return message_list

    def get_messages_count(self):
        """метод получения количества сообщений из БД"""
        messages_count = self.session.query(Message).count()
        return messages_count

    def add_new_group(self, group_id, group_name, owner_user_id, create_time=datetime.now()):
        """метод добавления новой группы в БД"""
        new_group = Group(group_id=group_id, group_name=group_name, owner_user_id=owner_user_id, create_time=create_time)
        self.session.add(new_group)
        self.session.commit()
        return new_group

    def get_groups_list(self):
        """метод получения групп из БД"""
        group_list = self.session.query(Group).all()
        return group_list

    def get_groups_count(self):
        """метод получения количества групп из БД"""
        groups_count = self.session.query(Group).count()
        return groups_count

    def get_group(self, column, value):
        """метод получения группы из БД"""
        if column == 'group_id':
            group = self.session.query(Group).filter_by(group_id=value).first()
        if column == 'group_name':
            group = self.session.query(Group).filter_by(group_name=value).first()
        return group

    def del_group(self, group_id):
        """метод удаления группы"""
        group = self.session.query(Group).filter_by(group_id=group_id).first()
        self.session.delete(group)
        self.session.commit()
        return group


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


class Client:
    session = None

    @log
    def send(self, msg):
        self.sock.send(json.dumps(msg).encode())

    @log
    def load_print(self):
        data = json.loads(self.sock.recv(2048).decode())
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
            'time': f'{datetime.now()}',
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
                'time': f'{datetime.now()}',
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
            db.save_message(from_user_id=self.guid, to_user_id=to_guid, text_message=message)
            self.send(create_message(to_user_name, to_guid, message))

        elif group != 'All' and group is not None:
            message = 'Групповое:' + input('Введите ваше ссобщение: ')
            smsg = self.get_list()
            for to_guid, v in smsg.items():
                if str(v.get('group')) == self.usr_group:
                    to_user_name = v.get('user_name')
                    db.save_message(from_user_id=self.guid, to_user_id=to_guid, text_message=message)
                    self.send(create_message(to_user_name, to_guid, message))

        elif group == 'All':
            message = 'Публичное:' + input('Введите ваше ссобщение: ')
            smsg = self.get_list()
            for to_guid, user_data in smsg.items():
                to_user_name = user_data.get('user_name')
                db.save_message(from_user_id=self.guid, to_user_id=to_guid, text_message=message)
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
                    from_user_name = msg.get("from_user_name")
                    from_guid = msg.get("from_guid")
                    message = msg.get("message")
                    db.save_message(from_user_id=from_guid, to_user_id=self.guid, text_message=message)
                    print(f'У Вас новое сообщение от {from_user_name}:\n'
                          f'{message}')
                    resp_msg = {
                        'response': 200,
                        'action': 'send_message',
                        'time': datetime.now(),
                        'from_user_name': self.name_in_chat,
                        'from_guid': self.guid,
                        'to_user_name': from_user_name,
                        'to_guid': from_guid,
                        'alert': 'Сообщение доставлено'
                        }
                    self.send(resp_msg)
            elif req == 'ping':
                self.input_queue.get()
                resp_msg = {
                    'response': 200,
                    'action': 'ping',
                    'time': f'{datetime.now()}',
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
            'time': f'{datetime.now()}',
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
            'time': f'{datetime.now()}',
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
            'time': f'{datetime.now()}',
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
            'time': f'{datetime.now()}',
            'user_name': f'{self.name_in_chat}',
            'group_id': group_id,
            'user': f'{self.usr_data}'
        }
        self.send(open_msg)
        msg = self.input_queue.get()
        data = msg.get(f'{self.guid}')
        if data.get('response') == 200:
            groups = self.show_group()
            for i, value in groups.items():
                if i == group_id:
                    db.add_new_group(group_id=i, group_name=value.get('название группы'),
                                     owner_user_id=value.get('владелец группы'))
            self.usr_group = group_id
        print(data.get('alert'))

    @log
    def create_group(self):
        group_name = input('Введите название группы:  ')
        create_group_msg = {
            'action': 'create_group',
            'time': f'{datetime.now()}',
            'user_group': group_name,
            'user_name': f'{self.name_in_chat}',
            'user': f'{self.usr_data}'
        }
        self.send(create_group_msg)
        msg = self.input_queue.get()
        data = msg.get(f'{self.guid}')
        if data.get('response') == 200:
            groups = self.show_group()
            for group_id, value in groups.items():
                if value.get('название группы') == group_name and value.get('владелец группы') == self.guid:
                    db.add_new_group(group_id=group_id, group_name=group_name, owner_user_id=self.guid)
        print(data.get('alert'))

    @log
    def exit_of_group(self):
        exit_of_group_msg = {
            'action': 'exit_of_group',
            'time': datetime.now(),
            'user_name': self.name_in_chat,
            'user': self.usr_data
        }
        self.send(exit_of_group_msg)
        msg = self.input_queue.get()
        data = msg.get(self.guid)
        if data.get('response') == 200:
            for i in db.get_groups_list():
                db.del_group(i.group_id)
        print(data.get('alert'))

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

    def create_storage(self):
        engine = create_engine('sqlite:///client_%s.db' % self.guid, echo=True, connect_args={'check_same_thread': False})
        Base.metadata.bind = engine
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        Session.configure(bind=engine)
        self.session = Session()

    def __init__(self):
        """Инициализация потока и атрибутов"""
        # регистрация имени пользователя
        self.name_in_chat = input('Введите ваше имя для входа в  чат:  ')
        self.sock = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
        self.sock.connect(('localhost', PORT))  # Соединиться с сервером
        self.usr_group = None
        self.input_queue = PriorityQueue()
        self.guid, self.usr_data = self.registration()
        self.create_storage()
        self.db = Storage(self.session)
        t = Thread(target=self.rec_message, daemon=True)
        t.start()
        self.menu()


if __name__ == "__main__":
    Client()
    db = Storage()
