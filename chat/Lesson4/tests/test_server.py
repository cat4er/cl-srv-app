# 1. Для всех функций из урока 3 написать тесты с использованием unittest. Они должны быть оформлены
# в отдельных скриптах с префиксом test_ в имени файла (например, test_client.py).

import unittest
from chat.Lesson4.server import authenticate, leave, request, responce, main

"""Для прохождения тестов, нужно запускать клиента (client1) в окружении test и сервер (server) в  test"""


class TestServerModuleFunc(unittest.TestCase):
    def setUp(self):
        self.client_list = {'8e1975eadd30aff5693cbbacda1d8cca85f2bd872ad3c8740cbf058626ae974': 'Игорь'}
        self.client = None

    def test_authenticate(self):
        user_data = {'8e1975eadd30aff5693cbbacda1d8cca85f2bd872ad3c8740cbf058626ae974': 'Victor'}
        self.assertEqual(authenticate(user_data), ('8e1975eadd30aff5693cbbacda1d8cca85f2bd872ad3c8740cbf058626ae974', 200,'Пользователь Victor вошел в чат'))

    def test_leave(self):
        user_data = {'8e1975eadd30aff5693cbbacda1d8cca85f2bd872ad3c8740cbf058626ae974': 'Victor'}
        self.assertEqual(leave(user_data), ('8e1975eadd30aff5693cbbacda1d8cca85f2bd872ad3c8740cbf058626ae974', 200, 'Пользователь Victor вышел из чата'))

    def test_request(self):
        get_list_msg = {'action': 'get_user_list', 'time': '1620864900.513133'}
        self.assertEqual(request(get_list_msg), None)

    def test_responce(self):
        answer = ['15f2685cb7d3aeb4e1789ba70f3b98db3544766633959d4a33dc88dfd057f8bc', 200, 'Пользователь Виктор вошел в чат']
        self.assertEqual(responce(answer), None)

    def test_main(self):
        self.assertEqual(main(), None)


if __name__ == '__main__':
    unittest.main()
