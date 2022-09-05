'''
3. Написать функцию host_range_ping_tab(), возможности которой основаны на 
функции из примера 2. Но в данном случае результат должен быть итоговым 
по всем ip-адресам, представленным в табличном формате (использовать модуль 
tabulate). Таблица должна состоять из двух колонок и выглядеть примерно так:
Reachable
10.0.0.1
10.0.0.2

Unreachable
10.0.0.3
10.0.0.4
'''

from tabulate import tabulate
from task2 import host_range_ping

def host_range_ping_tab(first_ip, range_len: int):
    '''
    Определяет доступность диапазона ip-адресов.
    Выводит на печать таблицу с доступными и недоступными адресами
    Аргументы
    first_ip - первый адрес
    range_len - размер диапазона
    '''
    availability_table = dict()
    availability_table['reachable'], availability_table['unreachable'] = host_range_ping(first_ip, range_len)
    # import pdb; pdb.set_trace()
    print(tabulate(availability_table, headers="keys", tablefmt='grid'))


if __name__ == '__main__':
    host_range_ping_tab('10.0.0.1', 3)
