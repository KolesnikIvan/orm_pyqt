import sys
# import os
import logging
import traceback
import inspect
import socket
from logs.config_log_client import cl_logger
from logs.config_log_server import srv_logger
from logs.config_log_other import other_log
# from variables import *
# sys.path.append(os.abspath(os.path.join(os.path.dirname(__file__), '..')))
# import pdb;pdb.set_trace()
# if 'client' in sys.argv[0]:
#     logger = logging.getLogger('client_log')
# elif 'server' in sys.argv[0]:
#     logger = logging.getLogger('srv_log')
# else:
#     print('Error')

if ['client' in itm for itm in sys.argv]:
    logger = logging.getLogger('client_log')
elif ['server' in itm for itm in sys.argv]:
    logger = logging.getLogger('srv_log')
else:
    logger = logging.getLogger('other_log')


def log_function(func):
    """
    decorator-function
    :param: func"""
    # import pdb; pdb.set_trace()
    def log_fname(*args, **kwargs):
        res = func(*args, **kwargs)
        logger.info(
        f'Из модуля {func.__module__} '
        f'функцией {traceback.format_stack()[0].strip().split()[-1]} '
        f'вызвана функция {func.__name__}({args}, {kwargs}) = {res}.',
        stacklevel=2)
        return res
    return log_fname


class Log_class:
    def __init__(self, logger):
        self.logger = logger

    def __call__(self, func):
        # import pdb; pdb.set_trace()
        def callf(*args, **kwargs):
            res = func(*args, **kwargs)
            self.logger.info(
                f'Из модуля {func.__module__} '
                f'функцией {inspect.stack()[1][3]} '
                f'вызвана функция {func.__name__}({args},{kwargs})={res}.',
                stacklevel=2)
            return res
        return callf



def need_login(func):
    """
    deco checking the client is authenticated
    :params: func
    """
    def checker(*args, **kwargs):
        from server.core import MessageProcessor
        from common.variables import ACTION, PRESENCE
        if isinstance(args[0], MessageProcessor):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    # check socket is in names
                    # import pdb; pdb.set_trace()
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True
                            # break
            
            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            # import pdb; pdb.set_trace()
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker
