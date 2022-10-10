import logging
import sys, os
sys.path.append(os.path.join(os.getcwd()))
from common.variables import LOGGING_LEVEL
from pathlib import Path

CL_LOG_PATH = Path().absolute().joinpath('logs', 'client_logs', 'client.log')

cl_formatter = logging.Formatter('%(asctime)s-%(thread)d-%(threadName)s-%(message)s')
# import pdb; pdb.set_trace()
cl_fh = logging.FileHandler(CL_LOG_PATH, encoding='utf-8')
cl_fh.setFormatter(cl_formatter)
cl_fh.setLevel(LOGGING_LEVEL)

cl_sh = logging.StreamHandler(sys.stdout)
cl_sh.setFormatter(cl_formatter)

cl_logger = logging.getLogger('client_log')
cl_logger.addHandler(cl_fh)
cl_logger.addHandler(cl_sh)
cl_logger.setLevel(LOGGING_LEVEL)


if __name__ == "__main__":
    cl_logger.info('клиентский логгер создан, запущен, как main-скрипт')
    cl_logger.critical('client critical message')
    cl_logger.error('client error message')
    cl_logger.warning('client warning message')
    