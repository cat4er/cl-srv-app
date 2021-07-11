# 2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона. Меняться должен только
# последний октет каждого адреса. По результатам проверки должно выводиться соответствующее сообщение.


import subprocess
import ipaddress


NET_ADDR = '192.168.1.'
PING_COUNT = 4


def host_range_ping(a, b):
    try:
        if a >= b:
            while not a < b:
                ping(ip_generator(a))
                a -= 1
        elif a < b:
            while not a > b:
                ping(ip_generator(a))
                a += 1
    except:
        print('Неверно задан диапазон')


def ip_generator(oct):
    return ipaddress.ip_address(f'{NET_ADDR + str(oct)}')


def ping(addr):
    res = subprocess.call(f'ping -c {PING_COUNT} {addr}', shell=True, stdout=open("/dev/null"), stderr=open("/dev/null"))
    if res == 0:
        print(f'Узел {addr} доступен')
    else:
        print(f'Узел {addr} недоступен')


host_range_ping(5, 1)
