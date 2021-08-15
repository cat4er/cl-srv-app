import bcrypt
import inspect
import json
import secrets
import sys
import time
from datetime import datetime
from functools import wraps
from socket import *
from threading import Thread
from binascii import hexlify, unhexlify, Error

from Cryptodome.Cipher import AES
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Enum
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import adminapp
from pyqt.Lesson8.clientapp.log.server_log_config import logger

socket_list = {}

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String, index=True)
    password = Column(String)
    pub_key = Column(String)
    user_status = Column(Enum('online', 'offline'))
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
    user_id = Column(ForeignKey('users.id'))
    event_type = Column(
        Enum('new_session', 'registration', 'leave', 'opengroup', 'creategroup', 'exitgroup', 'sendmessage', 'recmessage'),
        nullable=False)
    ip_address = Column(String(15), index=True)
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
    def add_new_user(user_name, password, user_status, key, user_group, create_time=datetime.now()):
        """метод добавления нового пользователя в БД"""
        new_user = User(user_name=user_name, password=password, user_status=user_status, pub_key=key,
                        user_group=user_group,
                        create_time=create_time)
        session.add(new_user)
        session.commit()
        return new_user

    @staticmethod
    def update_user_data(user_id, column, value):
        """метод обновления пользователей из БД со всеми параметрами"""
        update_user = session.query(User).get(user_id)
        if column == 'user_status':
            update_user.user_status = value
        elif column == 'user_group':
            update_user.user_group = value
        elif column == 'pub_key':
            update_user.pub_key = value
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
    def get_user(type, value):
        """метод получения пользователя из БД"""
        if type == 'guid':
            client = session.query(User).filter_by(id=value).first()
        elif type == 'user_name':
            client = session.query(User).filter_by(user_name=value).first()
        return client

    def del_user(self, guid):
        """метод удаления пользователя из БД"""
        del_user = self.get_user('guid', guid)
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
    def add_new_event(user_id, event_type, ip_address, create_time=datetime.now()):
        """метод добавления нового события в БД"""
        new_event = History(user_id=user_id, event_type=event_type, ip_address=ip_address, create_time=create_time)
        session.add(new_event)
        session.commit()
        return new_event

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

    def __init__(self, client):
        """Инициализация потока и атрибутов"""
        super().__init__()
        self.guid = None
        self.client = client
        self.pub_key = None
        self.user_name = None

    def login_required(func):
        """Проверяет залогинен ли пользователь сейчас"""

        def decorated(cls, *args, **kwargs):
            if cls.guid in socket_list.keys():
                return func(cls, *args, **kwargs)
            else:
                return cls.response([None, 401, 'Пользователь не авторизован'])

        return decorated

    @staticmethod
    def padding_text(text):
        """ Выравнивание сообщения до длины, кратной 16 байтам. В данном случае исходное сообщение дополняется
         пробелами"""
        pad_len = (16 - len(text) % 16) % 16
        return text + b' ' * pad_len

    def _encrypt_message(self, message):
        sixty_message = self.padding_text(message)
        cipher = AES.new(self.pub_key, AES.MODE_CBC)
        ciphertext = cipher.iv + cipher.encrypt(sixty_message)
        return hexlify(ciphertext)

    def _decrypt_message(self, hex_text):
        ciphertext = unhexlify(hex_text)
        cipher = AES.new(self.pub_key, AES.MODE_CBC, iv=ciphertext[:16])
        message = cipher.decrypt(ciphertext[16:])
        return message

    def check_encrypted_request(self, data):
        enc_func_list = ['registration', 'leave', 'opengroup', 'creategroup', 'exitgroup', 'sendmessage', 'recmessage']
        action = data.get('action')
        if action in enc_func_list:
            self.response(True, [self.guid, 400, 'Запрос не прошел проверку'])
            return False
        return True

    def registration(self, data):
        """Запись в словарь основных данных по классу: id, pub_key, socket, имя пользователя"""
        self.user_name = data.get('user_name')
        password = data.get('password')
        # sha_password = sha512(password.encode()).hexdigest()

        while True:
            i = db.get_user('user_name', self.user_name)  # спрашиваем есть ли в бд такой польщователь
            if i is None:
                sha_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))  # шифруем
                new_user = db.add_new_user(self.user_name, sha_password, 'online', self.pub_key, None)  # сохраняем в БД
                socket_list.update({new_user.id: self.client})  # добавляем клиента в список клиентов в онлайне
                self.guid = new_user.id  # передаем в переменную класса, чтобы другие методы могли забирать
                self.response(True, [self.guid, 200, f'{self.user_name} подключен'])  # отвечаем клиенту, что все хорошо
                print(
                    f'пользователь {self.user_name, self.pub_key} уже есть, подключен, статус онлайн')  # выводим тоже самое в консоль
                break  # завершаем цикл
            elif i.user_name == self.user_name and bcrypt.checkpw(password.encode(), i.password):
                db.update_user_data(i.id, 'user_status', 'online')
                db.update_user_data(i.id, 'pub_key', self.pub_key)
                socket_list.update({i.id: self.client})
                self.guid = i.id
                self.response(True, [self.guid, 200, f'{self.user_name} подключен'])
                print(f'пользователь {self.user_name, self.pub_key} уже есть, подключен, статус онлайн')
                break
            elif i.user_name == self.user_name:
                if bcrypt.checkpw(password.encode(), i.password) is False:
                    self.guid = i.id
                    self.response(True, [self.guid, 401, f'{self.user_name} ошибка ввода логина или пароля'])
                    print(f'{self.guid, self.user_name} ошибка ввода пароля')
                break

    def new_session(self):
        """Для новой сессии генереруется публичный 32 битный ключ"""
        hex_key = secrets.token_hex(16)
        self.pub_key = hex_key.encode()
        return None, 200, hex_key

    def run(self):
        """Запуск потока"""
        self.main()

    def response(self, type, data):
        """Метод отправки унифицированного ответа"""
        answer = {data[0]:
            {
                "response": data[1],
                'time': f'{datetime.now()}',
                "alert": data[2]
            }
        }
        if type:
            self.client.send(self._encrypt_message(json.dumps(answer).encode()))
        else:
            self.client.send(json.dumps(answer).encode())

    def request(self):
        """Метод получения запроса"""
        try:
            data = self.client.recv(4096)
            try:
                data = self._decrypt_message(data)
                data = json.loads(data.decode())
                return data
            except (TypeError, AttributeError, Error):
                try:
                    data = json.loads(data.decode())
                    if self.check_encrypted_request:
                        return data
                except json.decoder.JSONDecodeError:
                    print('Bad request from user')
        except ConnectionResetError:
            print('Connection reset by peer')

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
            self.response(True, [self.guid, 400, 'Ошибка запроса выхода из чата'])

    def __del__(self):
        """нотификация о закрытии сессии"""
        print('Сессия разорвана')
        pass

    def main(self):
        """Транслирует запросы по другим методам"""
        try:
            while True:
                data = self.request()
                if 'action' in data.keys():
                    action = data.get('action')
                    if action == 'registration':
                        self.registration(data)
                        self.save_event(event_type='registration')
                    elif action == 'get_session':
                        self.response(False, self.new_session())
                        self.save_event(event_type='new_session')
                    elif action == 'leave':
                        self.save_event(event_type='leave')
                        self.leave()
                        exit()
                    elif action == 'get_user_list':
                        self.response(True, self.get_user_list())
                    elif action == 'send_message':
                        self.send_message(data)
                        self.save_event(event_type='sendmessage')
                    elif action == 'rec_message':
                        self.rec_message(data)
                        self.save_event(event_type='recmessage')
                    elif action == 'show_group':
                        self.response(True, self.show_group())
                    elif action == 'open_group':
                        self.response(True, self.open_group(None, data))
                        self.save_event(event_type='opengroup')
                    elif action == 'create_group':
                        self.response(True, self.create_group(data))
                        self.save_event(event_type='creategroup')
                    elif action == 'exit_of_group':
                        self.response(True, self.exit_of_group())
                        self.save_event(event_type='exitegroup')
        except AttributeError:
            print(f'Невозможно обработать запрос - {data}')

    def save_event(self, event_type):
        db.add_new_event(user_id=self.guid, event_type=event_type, ip_address=self.client.getsockname()[0])

    @login_required
    def get_user_list(self):
        """Метод возвращает список доступных пользователей чата"""
        online_list = {}
        for i in db.get_user_list():
            if i.user_status == 'online':
                if i.id != self.guid:
                    online_list.update({i.id: {'user_name': i.user_name, 'group': i.user_group}})
        return self.guid, 200, online_list

    @login_required
    def send_message(self, data):
        """Метод получает сообшение от пользваотеля и направляет его другому пользователю. Выполняет роль
        маршрутизатора """

        to_client = (socket_list.get(int(data.get('to_guid'))))
        data.update({'action': 'rec_message'})
        print(data)
        if data.get('message'):
            db.save_message(from_user_id=data.get('from_guid'), to_user_id=data.get('to_guid'),
                            text_message=data.get('message'))
        elif data.get('alert'):
            db.save_message(from_user_id=data.get('from_guid'), to_user_id=data.get('to_guid'),
                            text_message=data.get('alert'))
        to_client.send(self._encrypt_message(json.dumps(data).encode()))

    def rec_message(self, data):
        """Метод получает ответ от пользваотеля на сообщение и направляет его отправителю, как подтверждение.
        Выполняет роль маршрутизатора """
        to_client = (socket_list.get(int(data.get('to_guid'))))
        data.update({'action': 'send_message'})
        print(data)
        to_client.send(self._encrypt_message(json.dumps(data).encode()))

    def show_group(self):
        """Метод отображения доступных групп"""
        group_list = {}
        for i in db.get_groups_list():
            group_list.update({i.group_id: {'название группы': i.group_name, 'владелец группы': i.owner_user_id}})
        return self.guid, 200, group_list

    @login_required
    def open_group(self, group_id=None, data=None):
        """Метод открытия существующей группы"""
        if data:
            group_id = data.get('group_id')
        if db.get_user('user', self.guid).user_group is None:
            db.update_user_data(self.guid, 'user_group', group_id)
            return self.guid, 200, f'Группа {db.get_group("group_id", group_id).group_name} открыта для общения'
        else:
            return self.guid, 400, f'Пользователь уже участвует в гурппе {db.get_group("group_id", group_id).group_name}'

    @login_required
    def create_group(self, data):
        """Метод создания группы"""
        for i in db.get_groups_list():
            if i.owner_user_id == self.guid:
                return self.guid, 400, f'Пользователь уже участвует в гурппе {i.group_name}'
        group_name = data.get("user_group")
        db.add_new_group(group_name=group_name, owner_user_id=self.guid)
        self.open_group(group_id=db.get_group("group_name", group_name).group_id)
        return self.guid, 200, f'Группа {group_name} готова для общения'

    @login_required
    @log
    def exit_of_group(self):
        """Метод выхода из группы"""
        group = db.get_user('user', self.guid).user_group
        if group is not None:
            db.update_user_data(self.guid, 'user_group', None)
            for i in db.get_groups_list():
                if i.owner_user_id == self.guid:
                    db.del_group(group)
            return self.guid, 200, f'Вы вышли из группы {group}'
        else:
            return self.guid, 400, 'Пользователь не участвуют в группах'


class Main:
    PORT = 8009

    def __init__(self):
        self.main()

    @staticmethod
    def check_user():
        """Проверяет доступен ли клиент на сервере, и если нет, то закрывает сокет, удаляет клиентскую запись,
        экземплятр класса и поток """
        while True:
            if socket_list:
                MAXCOUNT = 10
                for guid, client in socket_list.items():
                    count = 0
                    ping_msg = {
                        'action': 'ping',
                        'time': f'{datetime.now()}',
                        'user': guid}
                    try:
                        client.send(json.dumps(ping_msg).encode())
                        response = json.loads(client.recv(4096).decode())
                        if response.get('response') == 200 and response.get('action') == 'ping':
                            time.sleep(10)
                            continue
                    except:
                        if count == MAXCOUNT:
                            client.close()
                            socket_list.pop(guid)
                            db.update_user_data(guid, 'user_status', 'offline')
                            time.sleep(10)
                        else:
                            count += 1

    @staticmethod
    def create_thread(client):
        """Создание отдельно потока с экземпляром класса: 1 клиент = 1 поток"""
        thread = Chat(client)
        thread.daemon = True
        thread.start()

    def main(self):
        """Задача функции: открыть сессию, сделать поток пользователя, проверять онлайн ли он"""
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
            self.create_thread(client)
            client = None


if __name__ == "__main__":
    db = Storage()
    m = Thread(target=Main, daemon=True, )
    m.start()
    app = QApplication(sys.argv)  # Новый экземпляр QApplication
    window = AdminApp()  # Создаём объект класса для старта потока AdminApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
