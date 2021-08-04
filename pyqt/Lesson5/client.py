import time
from socket import *
from threading import Thread
import platform
import sys
import json
from datetime import datetime
from queue import PriorityQueue
from log.client_log_config import logger
from functools import wraps
import inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDialog, QMessageBox, QLineEdit, QPushButton, \
    QVBoxLayout, QListWidgetItem
from PyQt5 import QtGui, QtCore
import userapp

front_input_queue = PriorityQueue()
front_output_queue = PriorityQueue()
# config
PORT = 8009

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

    def read_messages(self):
        """метод чтения сообщений пользователя из БД"""
        message_list = self.session.query(Message).all()
        return message_list

    def get_messages_count(self):
        """метод получения количества сообщений из БД"""
        messages_count = self.session.query(Message).count()
        return messages_count

    def add_new_group(self, group_id, group_name, owner_user_id, create_time=datetime.now()):
        """метод добавления новой группы в БД"""
        new_group = Group(group_id=group_id, group_name=group_name, owner_user_id=owner_user_id,
                          create_time=create_time)
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


class UserApp(QMainWindow, userapp.Ui_MainWindow):
    user_chat = None
    user_name = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.commandLinkButton_2.clicked.connect(self.update_contact_list)
        self.commandLinkButton.clicked.connect(self.send_message)
        self.lineEdit.returnPressed.connect(self.send_message)
        self.listWidget.itemDoubleClicked.connect(self.open_chat)
        self.thread = QtCore.QThread()
        self.rec_message = RecMessage()
        self.rec_message.moveToThread(self.thread)
        self.thread.start()
        self.update_contact_list()

    def update_contact_list(self):
        req = {'action': 'get_list',
               'time': f'{datetime.now()}'}
        front_input_queue.put(req)
        resp = front_output_queue.get()
        if resp.get('response') == 200:
            data = resp.get('alert')
            self.listWidget.clear()
            layout = QVBoxLayout()
            for k, v in data.items():
                item = QListWidgetItem()
                item.guid = int(k)
                item.name = v.get("user_name")
                item.setText(f'{item.name}')
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("user.png"),
                               QtGui.QIcon.Normal, QtGui.QIcon.Off)
                item.setIcon(icon)
                self.listWidget.addItem(item)

            layout.addWidget(self.listWidget)
        else:
            self.dialog_message('Error', 'Упс, что-то пошло не так')

    def run_check_message(self):
        self.thread.started.connect(self.rec_message.rec_message())

    def open_chat(self):
        self.listWidget_2.clear()
        if self.listWidget:
            self.user_chat = self.listWidget.currentItem().guid
            self.user_name = self.listWidget.currentItem().name
            self.update_chat()

    def update_chat(self):
        if self.user_chat:
            req = {'action': 'read_messages',
                   'guid': self.user_chat,
                   'time': f'{datetime.now()}'}
            front_input_queue.put(req)
            res = front_output_queue.get()
            for i in res:
                if i.from_user_id == self.user_chat:
                    text_mes = QListWidgetItem()
                    text_mes.setText(f'{i.text_message}')
                    text_mes.setTextAlignment(QtCore.Qt.AlignLeft)
                    self.listWidget_2.addItem(text_mes)
                elif i.to_user_id == self.user_chat:
                    text_mes = QListWidgetItem()
                    text_mes.setText(f'{i.text_message}')
                    text_mes.setTextAlignment(QtCore.Qt.AlignRight)
                    self.listWidget_2.addItem(text_mes)

            layout = QVBoxLayout()
            layout.addWidget(self.listWidget_2)
        #
        # else:
        #     self.dialog_message('Error', 'Упс, что-то пошло не так')

    def send_message(self):
        message_text = self.lineEdit.text()
        if message_text:
            req = {'action': 'send_message',
                   'message_text': message_text,
                   'to_user_id': self.user_chat,
                   'to_user_name': self.user_name,
                   'time': f'{datetime.now()}'}
            front_input_queue.put(req)
            self.lineEdit.clear()
            resp = front_output_queue.get()
            if resp.get('response') == 200:
                self.open_chat()
        else:
            self.dialog_message('Error', 'Введите сообщение')

    def dialog_message(self, type, alert):
        QMessageBox.information(
            self, type, alert)


class RecMessage(QtCore.QObject):
    @staticmethod
    def rec_message():
        while True:
            try:
                req = front_output_queue.queue[0]
                if req.get('action') == 'rec_message':
                    request = front_output_queue.get()
                    from_user_name = request.get("from_user_name")
                    from_guid = request.get("from_user_id")
                    message = request.get("message_text")
                    alert = f'У Вас новое сообщение от {from_user_name}:{message}'
                    UserApp().dialog_message('Message', alert)
                    if UserApp().user_chat == int(from_guid):
                        UserApp().open_chat()
                else:
                    pass
            except IndexError:
                time.sleep(1)


class Login(QDialog, QMainWindow, userapp.Ui_MainWindow):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.retranslateUi(self)
        self.setWindowTitle('Введите логин')
        self.textName = QLineEdit(self)
        # self.textPass = QLineEdit(self)
        self.buttonLogin = QPushButton('Войти в чат', self)
        self.buttonLogin.clicked.connect(self.handle_login)
        layout = QVBoxLayout(self)
        layout.addWidget(self.textName)
        # layout.addWidget(self.textPass)
        layout.addWidget(self.buttonLogin)

    def handle_login(self):
        if self.textName.text():
            user_name = self.textName.text()
            msg = {'action': 'registration',
                   'time': f'{datetime.now()}',
                   'group': None,
                   'user_name': user_name}
            front_input_queue.put(msg)
            resp = front_output_queue.get()
            if resp.get('response') == 200:
                self.accept()
            else:
                QMessageBox.warning(
                    self, 'Error', resp.get('alert'))


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

    def send(self, msg):
        self.sock.send(json.dumps(msg).encode())

    def load_print(self):
        data = json.loads(self.sock.recv(2048).decode())
        return data

    def registration(self, request):
        self.name_in_chat = request.get('user_name')
        sys_info = platform.uname()
        self.usr_data = {'system': f'{sys_info[0]}',
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
            'user_data': f'{self.usr_data}'
        }

        self.send(reg_msg)
        reg_data = self.input_queue.get()
        for k, v in reg_data.items():
            if v.get('response') == 200:
                self.guid = k
                front_reg_resp_msg = {
                    'action': 'registration',
                    'time': f'{datetime.now()}',
                    'response': 200,
                }
                front_output_queue.put(front_reg_resp_msg)
                self.create_storage()
            else:
                resp_msg = {
                    'action': 'registration',
                    'time': f'{datetime.now()}',
                    'response': 500,
                    'alert': 'Ошибка регистарции'
                }
                front_output_queue.put(resp_msg)
                print('Ошибка регистарции')

    def send_message(self, request, group=None):
        to_user_name = request.get("to_user_name")
        to_guid = request.get("to_user_id")
        message = request.get("message_text")

        def create_message(*args):
            send_message_msg = {
                'action': 'send_message',
                'time': f'{datetime.now()}',
                'from_user_name': f'{self.name_in_chat}',
                'from_guid': f'{self.guid}',
                'to_user_name': to_user_name,
                'to_guid': to_guid,
                'message': message,
            }
            return send_message_msg

        if group is None:
            front_reg_resp_msg = {
                'action': 'send_message',
                'time': f'{datetime.now()}',
                'response': 200,
            }
            front_output_queue.put(front_reg_resp_msg)
            self.db.save_message(from_user_id=self.guid, to_user_id=to_guid, text_message=message)
            self.send(create_message(to_user_name, to_guid, message))

    def front_api(self):
        while True:
            try:
                req = front_input_queue.get()
                action = req.get('action')
                if action == 'registration':
                    self.registration(req)
                elif action == 'get_list':
                    self.get_list()
                elif action == 'read_messages':
                    self.read_message()
                elif action == 'send_message':
                    self.send_message(req)
                elif action == 'send_message_group':
                    self.send_message(req)
                elif action == 'show_group':
                    self.show_group()
                elif action == 'open_group':
                    self.open_group(req)
                elif action == 'create_group':
                    self.create_group(req)
                elif action == 'exit_group':
                    self.exit_of_group()
            except IndexError:
                pass

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
                    req = {'action': 'rec_message',
                           'message_text': message,
                           'from_user_id': from_guid,
                           'from_user_name': from_user_name,
                           'time': f'{datetime.now()}'}
                    front_output_queue.put(req)
                    self.db.save_message(from_user_id=from_guid, to_user_id=self.guid, text_message=message)
                    resp_msg = {
                        'response': 200,
                        'action': 'send_message',
                        'time': f'{datetime.now()}',
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
        data = msg.get(f'{self.guid}')
        front_output_queue.put(data)
        return data.get('alert')

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
                    self.db.add_new_group(group_id=i, group_name=value.get('название группы'),
                                          owner_user_id=value.get('владелец группы'))
            self.usr_group = group_id
        print(data.get('alert'))

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
                    self.db.add_new_group(group_id=group_id, group_name=group_name, owner_user_id=self.guid)
        print(data.get('alert'))

    def exit_of_group(self):
        exit_of_group_msg = {
            'action': 'exit_of_group',
            'time': f'{datetime.now()}',
            'user_name': self.name_in_chat,
            'user': self.usr_data
        }
        self.send(exit_of_group_msg)
        msg = self.input_queue.get()
        data = msg.get(self.guid)
        if data.get('response') == 200:
            for i in self.db.get_groups_list():
                self.db.del_group(i.group_id)
        print(data.get('alert'))

    def read_message(self):
        data = self.db.read_messages()
        front_output_queue.put(data)
        return data

    def create_storage(self):
        engine = create_engine('sqlite:///client_%s.db' % self.guid, echo=True,
                               connect_args={'check_same_thread': False})
        Base.metadata.bind = engine
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        Session.configure(bind=engine)
        self.session = Session()
        self.db = Storage(self.session)

    def __init__(self):
        super().__init__()
        """Инициализация потока и атрибутов"""
        # self.name_in_chat = input('Введите ваше имя для входа в  чат:  ')
        self.name_in_chat = None
        self.sock = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
        self.sock.connect(('localhost', PORT))  # Соединиться с сервером
        self.usr_group = None
        self.input_queue = PriorityQueue()
        self.guid = None
        self.db = None
        self.usr_data = None
        t = Thread(target=self.rec_message, daemon=True)
        t.start()
        f = Thread(target=self.front_api, daemon=True)
        f.start()


if __name__ == "__main__":
    b = Thread(target=Client, daemon=True)
    b.start()
    ui_app = QApplication(sys.argv)  # Новый экземпляр QApplication
    login = Login()
    if login.exec_() == QDialog.Accepted:
        window = UserApp()  # Создаём объект класса для старта потока
        window.show()
        ui_app.exec_()
        sys.exit(window.run_check_message())

