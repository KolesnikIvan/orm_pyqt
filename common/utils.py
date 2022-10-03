import json
import sys, os
import configparser
from pathlib import Path
# sys.path.append(Path().absolute())
sys.path.append(os.getcwd())
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.variables import (
    MAX_PACKAGE_LEN,
    ENCODING,
    MAX_CONNECTIONS,
    DEFAULT_PORT,
    DEFAULT_SRV_IP,
)
from common.decos import Log_class, log_function
from logs.config_log_client import cl_logger
from logs.config_log_server import srv_logger
import argparse
from common.errors import IncorrectDataReceived, NonDictInputError


if 'server' in sys.argv[0]:
    logger = srv_logger
elif 'client' in sys.argv[0]:
    logger = cl_logger

@Log_class(logger)
def get_message(sock):
    '''
    Принимает и декодирует сообщение из сокета. 
    :param sock - объект сокет (клиента или сервера). 
    Возвращает словарь. Если получает не байты, возвращает ошибку.
    '''
    # import pdb; pdb.set_trace()
    message_encoded = sock.recv(MAX_PACKAGE_LEN)
    if isinstance(message_encoded, bytes):
        message_json = message_encoded.decode(ENCODING)
        message = json.loads(message_json)
        if isinstance(message, dict):
            return message
        else:
            raise IncorrectDataReceived
    else:
        raise IncorrectDataReceived

@log_function
def send_message(sock, message: dict):
    '''
    Кодирует сообщение и посылает его  в сокет.
    :param sock: объект сокет
    :param message: dict сообщение-словарь
    :return:
    '''
    if not isinstance(message, dict):
        raise NonDictInputError
    message_json = json.dumps(message)
    message_encoded = message_json.encode(ENCODING)
    sock.send(message_encoded)


@Log_class(logger)
def arg_parser(def_ip: str = None, def_port: int = None):
    '''из аргументо CLI получаем адрес, порт и наименование; наименование идентифицирует клиента'''
    # import pdb; pdb.set_trace()  # L5
    config = configparser.ConfigParser()
    pth = Path().absolute().parent.joinpath('server', 'srv.ini')
    config.read(pth) 
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', dest='ip', default=def_ip if def_ip is not None else DEFAULT_SRV_IP, nargs='?', type=str)
    parser.add_argument('-p', '--port', dest='port', default=def_port if def_port is not None else DEFAULT_PORT, nargs='?', type=int)
    parser.add_argument('-n', '--name', dest='name', default='user', nargs='?', type=str, required=False)
    parser.add_argument('-s', '--password', dest='pwd', default='1234', nargs='?', type=str, required=False)
    parser.add_argument('-i', '--gui', dest='gui', help='show gui', action='store_true', default=True)
    args = parser.parse_args(sys.argv[1:])
    # import pdb; pdb.set_trace()
    if not 1023 < args.port < 65536:
        cl_logger.critical(f'Указан заведомо неверный номер порта {args.port}. Допустимы номера портов в диапазоне [1024; 65535].')
        sys.exit(1)

    return args.ip, args.port, args.name, args.pwd, args.gui

    
if __name__ == '__main__':
    import subprocess
    import pdb; pdb.set_trace()
    subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
    # for _ in range(MAX_CONNECTIONS):
    #     subprocess.Popen('python client.py 192.168.0.101 8079', close_fds=False, creationflags=subprocess.CREATE_NEW_CONSOLE)
