# 3. Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2. Но в данном случае
# результат должен быть итоговым по всем ip-адресам, представленным в табличном формате (использовать модуль
# tabulate). Таблица должна состоять из двух колонок и выглядеть примерно так:
# Reachable
# 10.0.0.1
# 10.0.0.2
#
# Unreachable
# 10.0.0.3
# 10.0.0.4

import subprocess
import ipaddress
import tabulate


PING_COUNT = 4
NET_ADDR = '192.168.1.'
result = {'Reachable': [],
          'Unreachable': []}


def host_range_ping_tab(a, b):
    try:
        if a >= b:
            while not a < b:
                ping(ip_generator(a))
                a -= 1
        elif a < b:
            while not a > b:
                ping(ip_generator(a))
                a += 1
        print(tabulate.tabulate(result, headers='keys', tablefmt="grid"))
    except:
        print('Неверно задан диапазон')


def ip_generator(oct):
    return ipaddress.ip_address(f'{NET_ADDR + str(oct)}')


def ping(addr):
    res = subprocess.call(f'ping -c {PING_COUNT} {addr}', shell=True, stdout=open("/dev/null"), stderr=open("/dev/null"))
    if res == 0:
        result.get("Reachable").append(addr)
    else:
        result.get("Unreachable").append(addr)


host_range_ping_tab(3, 1)
