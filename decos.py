import sys
import logging
import traceback
import inspect
from logs.config_log_client import cl_logger
from logs.config_log_server import srv_logger
from logs.config_log_other import other_log
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
    # decorator-function
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
