import logging
import sys, os
sys.path.append(os.getcwd())
from pathlib import Path
from common.variables import LOGGING_LEVEL

LOG_PATH = Path().absolute().joinpath('logs', 'other.log')
other_formatter = logging.Formatter(fmt='%(asctime)s-%(thread)s-%(threadsName)s-%(message)s')
other_handler = logging.FileHandler(LOG_PATH, encoding='utf-8')
other_handler.setFormatter(other_formatter)
other_log = logging.getLogger('other_log')
other_log.addHandler(other_handler)
other_log.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    other_log.info('other_logger is on')
