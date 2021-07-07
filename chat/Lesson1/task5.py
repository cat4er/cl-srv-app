# 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтовового в строковый
# тип на кириллице.

import subprocess

# сайт: колво запросов к сайту
exam = {"yandex.ru": 4, "youtube.com": 2}


def ping_any_res(args):
    for site, q_ty in args.items():
        print(f"Пингую сайт {site}, направив {q_ty} пакета ")
        subproc_ping = subprocess.Popen(["ping", "-c", f"{q_ty}", site], stdout=subprocess.PIPE)
        for line in subproc_ping.stdout:
            print(line.decode('cp1251'))


ping_any_res(exam)



# у меня консоль по-русски не говорит :)
#
# Пингую сайт yandex.ru, направив 4 пакета
# PING yandex.ru (5.255.255.55): 56 data bytes
# 64 bytes from 5.255.255.55: icmp_seq=0 ttl=249 time=19.937 ms
# 64 bytes from 5.255.255.55: icmp_seq=1 ttl=249 time=13.088 ms
# 64 bytes from 5.255.255.55: icmp_seq=2 ttl=249 time=13.368 ms
# 64 bytes from 5.255.255.55: icmp_seq=3 ttl=249 time=13.463 ms
# --- yandex.ru ping statistics ---
# 4 packets transmitted, 4 packets received, 0.0% packet loss
#
# Пингую сайт youtube.com, направив 4 пакета
# PING youtube.com (74.125.205.190): 56 data bytes
# 64 bytes from 74.125.205.190: icmp_seq=0 ttl=109 time=23.164 ms
# 64 bytes from 74.125.205.190: icmp_seq=1 ttl=109 time=30.896 ms
# --- youtube.com ping statistics ---
# 4 packets transmitted, 4 packets received, 0.0% packet loss