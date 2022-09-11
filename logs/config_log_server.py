import logging
from logging.handlers import TimedRotatingFileHandler
import sys, os
from pathlib import Path
sys.path.append(os.getcwd())
from common.variables import LOGGING_LEVEL

SRV_LOG_PATH = Path().absolute().joinpath('logs', 'srv_logs', 'srv.log')
formatter = logging.Formatter("%(asctime)s-%(levelname)s-%(lineno)d-%(message)s")

srv_fl_h = TimedRotatingFileHandler(SRV_LOG_PATH, encoding='utf-8', interval=1, when='M')
srv_fl_h.setFormatter(formatter)
srv_fl_h.setLevel(LOGGING_LEVEL)

srv_strm_handler = logging.StreamHandler(sys.stderr)
srv_strm_handler.setFormatter(formatter)


srv_logger = logging.getLogger("srv_log")
srv_logger.addHandler(srv_fl_h)
srv_logger.addHandler(srv_strm_handler)
srv_logger.setLevel(LOGGING_LEVEL)


if __name__ == '__main__':
    srv_logger.info('серверный логгер запущен, как main-скрипт')
    srv_logger.critical('critical error from srv_logger')
    srv_logger.error('error message from srv logger')
    srv_logger.warning('warning from srv_logger')
