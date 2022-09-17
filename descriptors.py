import logging
from logs.config_log_other import other_log

class Port:
    '''port descriptor with range check'''
    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            other_log.critical(f'введен номер порта {value} вне диапазона [1024;65535]')
            exit(1)
        else:
            instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
        