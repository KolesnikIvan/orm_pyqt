'''Constants'''
import logging
import sys
sys.path.append('..')

DEFAULT_PORT = 7777                 # порт для взаимодействия (как у клиента, так и у сервера)
DEFAULT_SRV_IP = '127.0.0.1'        # адрес сервера

MAX_CONNECTIONS = 5                 # количество клиентов (максимальное), которое можно подключить и обрабатывать
MAX_PACKAGE_LEN = 1024              # длина сообщения в байтах (наибольшая допустимая) 

ENCODING =  'utf-8'                 # кодировка
LOGGING_LEVEL = logging.DEBUG       # NOTSET      # уровень логирования
DB_URL = 'sqlite:///srv_db.db3'     # база, к которой будет обращаться сервер

# Основые ключи протокола Json instant messaging
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'sender'
DESTINATION = 'to'
DATA = 'bin'
PUBLIC_KEY = 'publick_key'
# Прочие ключи JIM json instant messaging
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'list_info'
DEL_CONTACT = 'delete'
ADD_CONTACT = 'add'
USERS_LIST = 'known_users_list'
KEY_REQ = 'public key request'
# dicts-arswers
RESPONSE_200 = {RESPONSE: 200}
RESPONSE_202 = {RESPONSE: 202, LIST_INFO: None}
RESPONSE_400 = {RESPONSE: 400, ERROR: None}
RESPONSE_205 = {RESPONSE: 205}              # L6
RESPONSE_511 = {RESPONSE: 511, DATA: None}  # L6
