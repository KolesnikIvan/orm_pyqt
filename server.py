import sys
import socket
import json
from common.utils import get_message, send_message, arg_parser
from common.variables import (
    MAX_CONNECTIONS,
    DEFAULT_PORT,
    ACTION,
    ACCOUNT_NAME,
    PRESENCE,
    TIME,
    USER,
    SENDER,
    RESPONSE,
    PRESENCE,
    ERROR,
    MESSAGE,
    MESSAGE_TEXT,
    RESPONSE_400,
    DESTINATION,
    RESPONSE_200,
    EXIT,
    )
from logs.config_log_server import srv_logger
from decos import log_function, Log_class
from select import select
import time


class Server:
    def __init__(self, listen_address, listen_ports):
        self.ip = listen_address
        self.port = listen_ports
        self.clients = []        # список активных клиентов
        self.msgs_to_send = []  # список сообщений
        self.names = dict()      # словарь {имя: клиент-сокет}

    def init_socket(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.settimeout(1)
        self.sock = server_socket
        self.sock.listen(MAX_CONNECTIONS)    # связывание сокета с портом
        srv_logger.info(f'Сервер запущен по адресу {self.ip}:{self.port}')

    def main(self):
        ''' Создает сокет на стороне сервера на хосте и порте из командной строки.'''
        # import pdb; pdb.set_trace()
        self.init_socket()
        while True:
            try:
                client_sock, client_address = self.sock.accept()
            except (ValueError, json.JSONDecodeError):
                srv_logger.error('Сообщение от клиента некорректно')
                sys.exit(1)
            except OSError as e:
                srv_logger.error(f'ошибка {e} на сервере')
                pass
            else:
                srv_logger.info(f'установлено соединение с клиентом {client_address}')
                self.clients.append(client_sock)
            socks_to_receive = []
            socks_to_answer = []
            err = []
            try:
                if self.clients:
                    socks_to_receive, socks_to_answer, err = select(self.clients, self.clients, [], 0)
                    print('read', socks_to_receive)
            except OSError as e:
                srv_logger.error(f'ошибка {e} при использовании сервером модуля select')
                pass

            # если сообщение, то в словарь, иначе - удаляем клиента из списка
            if socks_to_receive:
                for sender in socks_to_receive:
                    try:  # process message to add it in messages list
                        # import pdb; pdb.set_trace()
                        self.proc_msg_fr_client(get_message(sender), sender)
                    except Exception as e:
                        srv_logger.info(f'клиент {sender} отключился')
                        self.clients.remove(sender)

            for msg in self.msgs_to_send:
                try:
                    self.proc_msg_to_client(msg, socks_to_answer)
                except Exception as e:
                    srv_logger.info(f'утрачена связь с клиентом msg[DESTINATION]')
                    self.clients.remove(self.names[msg[DESTINATION]])
                    del self.names[msg[DESTINATION]]
            self.msgs_to_send.clear()

    @log_function
    def proc_msg_to_client(self, message, dest_socks):
        '''
        отправляет сообщение в соответствии с его DESTNATION
        принимает сообщение, список имен клиентов, список сокетов ожидающих сообщения
        '''
        if message[DESTINATION] in self.names\
        and self.names[message[DESTINATION]] in dest_socks:
            send_message(self.names[message[DESTINATION]], message)
            srv_logger.info(f'отправлено сообщение {message[MESSAGE_TEXT]} от пользователя {message[SENDER]} пользователю {message[DESTINATION]}')
        elif message[DESTINATION] in self.names\
        and message[DESTINATION] not in dest_socks:
            raise ConnectionError
        else:
            srv_logger.error(f'пользователь {message[DESTINATION]} не подключен к серверу')

    # @Log_class(srv_logger)
    @log_function
    def proc_msg_fr_client(self, message, client_sock):
        '''Проверка сообщения от клиента. Если надо, отправит словарь-ответ.'''
        srv_logger.info(f'разбор сообщения {message} от клиента {client_sock}')
        # если дежурное приветствие, то принять и ответить
        # import pdb; pdb.set_trace
        if ACTION in message\
        and message[ACTION] == PRESENCE\
        and TIME in message\
        and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                # если клиент обратился впервые, внести его в names и ответить 200:ok
                self.names[message[USER][ACCOUNT_NAME]] = client_sock
                # import pdb; pdb.set_trace()
                send_message(client_sock, RESPONSE_200)
                srv_logger.info('Получено корректное сообщение от клиента, сформирован ответ 200')
            else:
                response = RESPONSE_400
                response[ERROR] = 'клиент с таким именем уже находится на связи'
                srv_logger.error('Получено некорректное сообщение от клиента')
                send_message(client_sock, response)
            return
        # если целевое сообщение, то внести в список сообщений, не отвечать
        elif ACTION in message\
        and message[ACTION] == MESSAGE\
        and TIME in message\
        and MESSAGE_TEXT in message\
        and SENDER in message\
        and DESTINATION in message:
            self.msgs_to_send.append(message)
            return
        elif ACTION in message\
        and message[ACTION] == EXIT\
        and ACCOUNT_NAME in message:
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            return
        # иначе уведомить об ошибке
        else:
            response = RESPONSE_400
            response[ERROR] = 'request is incorrect'
            send_message(client_sock, response)
            return 

def main():
    '''получение хоста и порта из командной строки'''    
    listen_address, listen_port, _ = arg_parser()
    # создание экземпляра сервер
    server = Server(listen_address, listen_port)
    server.main()
    
if __name__ == '__main__':
    main()
