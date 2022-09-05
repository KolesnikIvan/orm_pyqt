'''
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет 
проверяться доступность сетевых узлов. Аргументом функции является список, 
в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом. 
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом 
соответствующего сообщения («Узел доступен», «Узел недоступен»). При этом 
ip-адрес сетевого узла должен создаваться с помощью функции ip_address(). 
(Внимание! Аргументом сабпроцесcа должен быть список, а не строка!!! Для 
уменьшения времени работы скрипта при проверке нескольких ip-адресов, решение 
необходимо выполнить с помощью потоков)
'''

import ipaddress
import subprocess as sp
# import chardet
from threading import Thread
import platform


PING_TIMES = "2"  # сколько раз пинговать


def ping_one(ip, av: dict, nav: dict):
    '''
    определяет доступность отдельного ip-адреса
    '''
    # import pdb; pdb.set_trace()
    # if is_host(ip):
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, PING_TIMES, str(ip)]
        result = sp.run(command, stdout=sp.DEVNULL)
        if result.returncode == 0:
            print(f'Node {ip} is available')
            av[ip] = True
        else:
            print(f'Node {ip} is not available')
            nav[ip] = False
        return (ip, result.returncode)
    except Exception as e:
        print(e)

def host_ping(ip_list: list = []):
    '''ОПределяет доступность списка ip-адресов'''
    available_ips = dict()
    notavailable_ips = dict()
    for ip in ip_list:
        thr = Thread(target=ping_one, args=(ip,available_ips, notavailable_ips))
        thr.start()
        thr.join()
    return available_ips, notavailable_ips


if __name__ == '__main__':
    ip_list = ['192.168.0.1', '172.168.0.1', '80.0.1.0',\
        'google.com', 'yandex.ru', 'ya.ru',\
        'kommersant.ru', ]
    av, nav = host_ping(ip_list)
    print(av)
    print(nav)

# ______________________________________________________________________
# ниже наброски
# def is_host(ip:str):
#     '''
#     Проверка соответствия переданного адреса хосту (иначе сети)
#     аргумент - ip
#     '''
#     # import pdb; pdb.set_trace()
#     try:
#         ip = ipaddress.ip_address(ip)
#         ipaddress.ip_network(ip)
#         return False
#     except Exception:
#         return True

# from concurrent.futures import ThreadPoolExecutor
# def ping_list(ip_list:list):
#     with ThreadPoolExecutor(max_workers=round(len(list)/2,0)) as executor:
#         result = executor(map(ping_one), ip_list)
#         return result
