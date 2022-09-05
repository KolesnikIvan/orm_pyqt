'''
2. Написать функцию host_range_ping() (возможности которой основаны на функции 
из примера 1) для перебора ip-адресов из заданного диапазона. Меняться должен 
только последний октет каждого адреса. По результатам проверки должно выводиться 
соответствующее сообщение.
'''

import ipaddress
from task1 import host_ping

def host_range_ping(first_ip: str, range_len: int):
    ip = ipaddress.ip_address(first_ip)
    ip_list = []
    # import pdb; pdb.set_trace()
    while ip < ipaddress.ip_address(first_ip) + range_len\
        and int(str(ip).split('.')[-1]) <= 255:
        ip_list.append(ip)
        ip += 1
    
    av, nav = host_ping(ip_list)
    
    print(f'доступны ip-адреса {av}')
    print(f'не доступны адреса {nav}')
    return av, nav


if __name__ == '__main__':
    host_range_ping('192.168.0.1', 10)
