from socket import *
import time
from datetime import datetime
import json
from threading import Thread
import ast
import sys
import secrets
from Crypto.Cipher import AES
from base64 import b64encode, b64decode
import select
from log.server_log_config import logger
from functools import wraps
import inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
import adminapp

salt = 'SlTKeYOpHygTYkP3'
client_list = None  # клиенты и их атрибуты
socket_list = {}

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, index=True)
    pub_key = Column(String)
    user_status = Column(Enum('online', 'offline'))
    token = Column(String, index=True, unique=True)
    user_group = Column(ForeignKey('groups.group_id'))
    create_time = Column(DateTime)


class Group(Base):
    __tablename__ = 'groups'
    group_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_name = Column(String, index=True)
    owner_user_id = Column(ForeignKey('users.id'))
    create_time = Column(DateTime)


class Message(Base):
    __tablename__ = 'messages'
    message_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    from_user_id = Column(ForeignKey('users.id'))
    to_user_id = Column(ForeignKey('users.id'))
    text_message = Column(Text)
    create_time = Column(DateTime)


class History(Base):
    __tablename__ = 'histories'
    event_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    event_type = Column(
        Enum('registration', 'leave', 'opengroup', 'creategroup', 'exitgroup', 'sendmessage', 'recmessage'),
        nullable=False)
    ip_address = Column(String(15), index=True)
    create_time = Column(DateTime)


class Contact(Base):
    __tablename__ = 'contacts'
    contact_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(ForeignKey('users.id'))
    contact_with = Column(ForeignKey('users.id'))
    token = Column(ForeignKey('users.token'))
    create_time = Column(DateTime)


engine = create_engine('sqlite:///server.db', echo=True, connect_args={'check_same_thread': False})
Base.metadata.bind = engine
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()


class AdminApp(QMainWindow, adminapp.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.storage_info)

    def storage_info(self):
        self.tableWidget.setItem(0, 0, QTableWidgetItem(str(db.get_users_count())))
        self.tableWidget.setItem(1, 0, QTableWidgetItem(str(db.get_messages_count())))
        self.tableWidget.setItem(2, 0, QTableWidgetItem(str(db.get_groups_count())))


class Storage:
    """Класс методов по управлению хранилищем"""

    @staticmethod
    def add_new_user(guid, user_name, user_status, token, key, user_group, create_time=datetime.now()):
        """метод добавления нового пользователя в БД"""
        new_user = User(id=guid, user_name=user_name, user_status=user_status, token=token, pub_key=key,
                        user_group=user_group,
                        create_time=create_time)
        session.add(new_user)
        session.commit()

    @staticmethod
    def update_user_data(user_id, column, value):
        """метод обновления пользователей из БД со всеми параметрами"""
        update_user = session.query(User).get(user_id)
        if column == 'user_status':
            update_user.user_status = value
        elif column == 'user_group':
            update_user.user_group = value
        elif column == 'token':
            update_user.token = value
        session.add(update_user)
        session.commit()

    @staticmethod
    def get_user_list():
        """метод получения пользователей из БД со всеми параметрами"""
        user_list = session.query(User).all()
        return user_list

    @staticmethod
    def get_users_count():
        """метод получения количества сообщений из БД"""
        users_count = session.query(User).count()
        return users_count

    @staticmethod
    def get_user(guid):
        """метод получения пользователя из БД"""
        client = session.query(User).filter_by(id=guid).first()
        return client

    def del_user(self, guid):
        """метод удаления пользователя из БД"""
        del_user = self.get_user(guid)
        session.delete(del_user)
        session.commit()
        return del_user

    @staticmethod
    def save_message(from_user_id, to_user_id, text_message, create_time=datetime.now()):
        """метод добавления нового сообщения в БД"""
        new_message = Message(from_user_id=from_user_id, to_user_id=to_user_id, text_message=text_message,
                              create_time=create_time)
        session.add(new_message)
        session.commit()
        return new_message

    @staticmethod
    def read_messages(guid):
        """метод чтения сообщений пользователя из БД"""
        message_list = session.query(Message).filter_by(from_user_id=guid, to_user_id=guid).all()
        return message_list

    @staticmethod
    def get_messages_count():
        """метод получения количества сообщений из БД"""
        messages_count = session.query(Message).count()
        return messages_count

    @staticmethod
    def add_contact(user_id, contact_with, token, create_time=datetime.now()):
        """метод получения списков контакта пользователя из БД"""
        new_contact = Contact(user_id=user_id, contact_with=contact_with, token=token,
                              create_time=create_time)
        session.add(new_contact)
        session.commit()
        return new_contact

    @staticmethod
    def get_contacts(guid):
        """метод получения списков контакта пользователя из БД по пользователю"""
        contacts_list = session.query(Contact).filter_by(user_id=guid).all()
        return contacts_list

    @staticmethod
    def add_new_event(user_id, event_type, ip_address, create_time=datetime.now()):
        """метод добавления нового события в БД"""
        new_event = History(user_id=user_id, event_type=event_type, ip_address=ip_address, create_time=create_time)
        session.add(new_event)
        session.commit()
        return new_event

    @staticmethod
    def read_event_list(guid):
        """метод чтения событий из БД по пользователю"""
        event_list = session.query(Contact).filter_by(user_id=guid).all()
        return event_list

    @staticmethod
    def add_new_group(group_name, owner_user_id, create_time=datetime.now()):
        """метод добавления новой группы в БД"""
        new_group = Group(group_name=group_name, owner_user_id=owner_user_id, create_time=create_time)
        session.add(new_group)
        session.commit()
        return new_group

    @staticmethod
    def clean_all_table():
        session.query(User).delete()
        session.query(Group).delete()
        session.query(Message).delete()
        session.query(History).delete()
        session.query(Contact).delete()

    @staticmethod
    def get_groups_list():
        """метод получения групп из БД"""
        group_list = session.query(Group).all()
        return group_list

    @staticmethod
    def get_groups_count():
        """метод получения количества групп из БД"""
        groups_count = session.query(Group).count()
        return groups_count

    @staticmethod
    def get_group(column, value):
        """метод получения группы из БД"""
        if column == 'group_id':
            group = session.query(Group).filter_by(group_id=value).first()
        if column == 'group_name':
            group = session.query(Group).filter_by(group_name=value).first()
        return group

    @staticmethod
    def del_group(group_id):
        """метод удаления группы"""
        group = session.query(Group).filter_by(group_id=group_id).first()
        session.delete(group)
        session.commit()
        return group


def log(func):
    """Логирование взаимодействий между функциями"""

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

    def response(self, data):
        """Метод отправки унифицированного ответа"""
        answer = {data[0]:
            {
                "response": data[1],
                'time': f'{datetime.now()}',
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
            socket_list.pop(self.guid)
            db.update_user_data(self.guid, 'user_status', 'offline')
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
                    self.save_event(event_type='registration')
                elif action == 'leave':
                    self.save_event(event_type='leave')
                    self.leave()
                    exit()
                elif action == 'get_user_list':
                    self.response(self.get_user_list())
                elif action == 'send_message':
                    self.send_message(data)
                    self.save_event(event_type='sendmessage')
                elif action == 'rec_message':
                    self.rec_message(data)
                    self.save_event(event_type='recmessage')
                elif action == 'show_group':
                    self.response(self.show_group())
                elif action == 'open_group':
                    self.response(self.open_group(None, data))
                    self.save_event(event_type='opengroup')
                elif action == 'create_group':
                    self.response(self.create_group(data))
                    self.save_event(event_type='creategroup')
                elif action == 'exit_of_group':
                    self.response(self.exit_of_group())
                    self.save_event(event_type='exitegroup')
            else:
                print('Такой команды в списке доступных')

    def save_event(self, event_type):
        db.add_new_event(user_id=self.guid, event_type=event_type, ip_address=self.client.getsockname()[0])

    def get_user_list(self):
        """Метод возвращает список доступных пользователей чата"""
        online_list = {}
        for i in db.get_user_list():
            if i.user_status == 'online':
                online_list.update({i.id: {'user_name': i.user_name, 'group': i.user_group}})
        return self.guid, 200, online_list

    def send_message(self, data):
        """Метод получает сообшение от пользваотеля и направляет его другому пользователю.
        Выполняет роль маршрутизатора"""
        to_client = (socket_list.get(int(data.get('to_guid'))))
        data.update({'action': 'rec_message'})
        print(data)
        if data.get('message'):
            db.save_message(from_user_id=data.get('from_guid'), to_user_id=data.get('to_guid'),
                            text_message=data.get('message'))
        elif data.get('alert'):
            db.save_message(from_user_id=data.get('from_guid'), to_user_id=data.get('to_guid'),
                            text_message=data.get('alert'))
        to_client.send(json.dumps(data).encode())
        db.add_contact(user_id=self.guid, contact_with=data.get('to_guid'), token=self.token)

    @staticmethod
    def rec_message(data):
        """Метод получает ответ от пользваотеля на сообщение и направляет его отправителю, как подтверждение.
        Выполняет роль маршрутизатора"""
        to_client = (socket_list.get(int(data.get('to_guid'))))
        data.update({'action': 'send_message'})
        print(data)
        to_client.send(json.dumps(data).encode())

    def show_group(self):
        """Метод отображения доступных групп"""
        group_list = {}
        for i in db.get_groups_list():
            group_list.update({i.group_id: {'название группы': i.group_name, 'владелец группы': i.owner_user_id}})
        return self.guid, 200, group_list

    def open_group(self, group_id=None, data=None):
        """Метод открытия существующей группы"""
        if data:
            group_id = data.get('group_id')
        if db.get_user(self.guid).user_group is None:
            db.update_user_data(self.guid, 'user_group', group_id)
            return self.guid, 200, f'Группа {db.get_group("group_id", group_id).group_name} открыта для общения'
        else:
            return self.guid, 400, f'Пользователь уже участвует в гурппе {db.get_group("group_id", group_id).group_name}'

    def create_group(self, data):
        """Метод создания группы"""
        for i in db.get_groups_list():
            if i.owner_user_id == self.guid:
                return self.guid, 400, f'Пользователь уже участвует в гурппе {i.group_name}'
        group_name = data.get("user_group")
        db.add_new_group(group_name=group_name, owner_user_id=self.guid)
        self.open_group(group_id=db.get_group("group_name", group_name).group_id)
        return self.guid, 200, f'Группа {group_name} готова для общения'

    @log
    def exit_of_group(self):
        """Метод выхода из группы"""
        group = db.get_user(self.guid).user_group
        if group is not None:
            db.update_user_data(self.guid, 'user_group', None)
            for i in db.get_groups_list():
                if i.owner_user_id == self.guid:
                    db.del_group(group)
            return self.guid, 200, f'Вы вышли из группы {group}'
        else:
            return self.guid, 400, 'Пользователь не участвуют в группах'

    # def check_token():
    """Проверят выданный клиенту токен в каждом реквесте перед обработкой"""
    #     pass


class Main:
    PORT = 8007

    def __init__(self, cl_list, slt):
        self.salt = slt
        self.client_list = cl_list  # клиенты и их атрибуты
        self.main()

    def check_user(self):
        """Проверяет доступен ли клиент на сервере, и если нет, то закрывает сокет,
        удаляет клиентскую запись, экземплятр класса и поток"""
        while True:
            if socket_list:
                try:
                    for guid, client in socket_list.items():
                        ping_msg = {
                            'action': 'ping',
                            'time': f'{datetime.now()}',
                            'user': guid}
                        client.send(json.dumps(ping_msg).encode())
                        try:
                            ready = select.select([client], [], [], 5)
                            if ready[0]:
                                response = json.loads(client.recv(2048).decode())
                                if response.get('response') == 200 and response.get('action') == 'ping':
                                    time.sleep(10)
                        except:
                            client.close()
                            socket_list.pop(guid)
                            db.update_user_data(guid, 'user_status', 'offline')
                            time.sleep(10)
                except RuntimeError:
                    break

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
        while True:
            i = db.get_user(guid)
            if i is None:
                db.add_new_user(guid, user_name, 'online', token, key, None)
                socket_list.update({guid: client})
                break
            elif i.user_name == user_name:
                db.update_user_data(guid, 'user_status', 'online')
                db.update_user_data(guid, 'token', token)
                socket_list.update({guid: client})
                print(f'пользователь {user_name, token} уже есть, статус онлайн')
                break
            else:
                guid += 1

        client.send(json.dumps({guid:
            {
                "response": 200,
                'time': f'{datetime.now()}',
                "alert": f'{guid, user_name} подключен'
            }
        }).encode())
        print(f'{guid, user_name} подключен')

        self.create_thread(guid, token, key, client, user_name)

    def main(self):
        """Задача функции: открыть сессию, зарегистрировать пользователя"""
        s = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP
        s.bind(('localhost', self.PORT))  # Присваивает порт
        s.listen()
        client = None
        # p = Thread(target=self.check_user)
        # p.daemon = True
        # p.start()
        while True:
            if client is None:
                client = s.accept()[0]

            receive_data = json.loads(client.recv(2048).decode())
            self.registration(client, receive_data)
            client = None


if __name__ == "__main__":
    db = Storage()
    m = Thread(target=Main, args=(client_list, salt), daemon=True, )
    m.start()
    app = QApplication(sys.argv)  # Новый экземпляр QApplication
    window = AdminApp()  # Создаём объект класса для старта потока AdminApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

