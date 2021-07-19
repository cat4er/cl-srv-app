# 4. Продолжаем работать над проектом «Мессенджер»: a) Реализовать скрипт, запускающий два клиентских приложения: на
# чтение чата и на запись в него. Уместно использовать модуль subprocess). b) Реализовать скрипт, запускающий
# указанное количество клиентских приложений.

from subprocess import Popen, check_call, PIPE, TimeoutExpired
import os
import psutil
from threading import Thread
from time import sleep


def is_running(script):
    for q in psutil.process_iter():
        if q.name().startswith('python'):
            if len(q.cmdline()) > 1 and script in q.cmdline()[1] and q.pid != os.getpid():
                print(f'{script} Process is already running')
                return True

    return False


def output(pop):
    while pop.poll() is None:
        print(pop.stdout.readline().decode())


def thread_for_app(app):
    Thread(target=output(app), daemon=True).start()


def main():
    try:
        quantity_of_clients_app = int(input("How many chat's you nedd to start?: "))
    except ValueError:
        print('Incorrect number')
    if not is_running("server.py"):
        print('Process not found: starting it.')
        serv = Popen('python3 server.py', shell=True, stdout=PIPE, stderr=PIPE)
        # sleep(1)
        # Thread(target=output(serv), daemon=True).start()
    for app in range(1, quantity_of_clients_app + 1):
        if app % 2 == 0:
            cl2 = Popen('python3 client.py', shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
            try:
                cl2.communicate(input=f'Name-{app}\n2\n{app - 1}\nHallo Name-{app}!\n'.encode(), timeout=10)
            except TimeoutExpired:
                cl2.kill()
                cl1.kill()
        else:
            cl1 = Popen('python3 client.py', shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
            try:
                cl1.communicate(input=f'Name-{app}\n'.encode(), timeout=1)
            except TimeoutExpired:
                pass
            # Thread(target=output(cl1), daemon=True).start()
    serv.kill()


if __name__ == "__main__":
    try:
        check_call(["pkill", "-9", "-f", "server.py"])
        check_call(["pkill", "-9", "-f", "client.py"])
    except:
        print('Starting main programm')
    finally:
        main()