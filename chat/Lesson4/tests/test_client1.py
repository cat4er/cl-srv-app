# 1. Для всех функций из урока 3 написать тесты с использованием unittest. Они должны быть оформлены
# в отдельных скриптах с префиксом test_ в имени файла (например, test_client.py).

import unittest
from chat.Lesson4.client1 import send, load_print, s as sock

"""Для прохождения тестов, нужно запускать серверное приложение (server) в окружении prod, a (client) в  test"""


class TestServerModuleFunc(unittest.TestCase):
    def setUp(self):
        self.s = sock

    def test_send(self):
        reg_msg = {'action': 'authenticate', 'time': '1620891672.5071292', 'user': {'15f2685cb7d3aeb4e1789ba70f3b98db3544766633959d4a33dc88dfd057fjk4': 'Александр'}}
        self.assertEqual(send(self.s, reg_msg), None)

    def test_load_print(self):
        self.assertEqual(load_print(self.s), None)


if __name__ == '__main__':
    unittest.main()