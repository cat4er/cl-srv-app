# 1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
# Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или
# ip-адресом. В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего
# сообщения («Узел доступен», «Узел н1. Написать функцию host_ping(), в которой с помощью утилиты ping будет
# проверяться доступность сетевых узлов. Аргументом функции является список, в котором каждый сетевой узел должен
# быть представлен именем хоста или ip-адресом. В функции необходимо перебирать ip-адреса и проверять их доступность
# с выводом соответствующего сообщения («Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен
# создаваться с помощью функции ip_address().едоступен»). При этом ip-адрес сетевого узла должен создаваться с
# помощью функции ip_address().


import subprocess
import ipaddress

some_address = ['ya.ru', 'localhost', 'lol.local']
PING_COUNT = 4
ip = ipaddress.ip_address('192.168.1.171')
some_address.append(ip)


def host_ping(address):
    for addr in address:
        res = subprocess.call(f'ping -c {PING_COUNT} {addr}', shell=True, stdout=open("/dev/null"), stderr=open("/dev/null"))
        if res == 0:
            print(f'Узел {addr} доступен')
        else:
            print(f'Узел {addr} недоступен')


host_ping(some_address)