import json
import sys
import socket
import time
from common.utils import get_message, send_message, arg_parser
from common.variables import (
    DEFAULT_PORT,
    DEFAULT_SRV_IP,
    ACTION,
    TIME,
    USER,
    ACCOUNT_NAME,
    SENDER,
    PRESENCE,
    RESPONSE,
    ERROR,
    MESSAGE,
    MESSAGE_TEXT,
    DESTINATION,
    EXIT,
    )
from logs.config_log_client import cl_logger
from decos import Log_class, log_function
from errors import IncorrectDataReceived, NonDictInputError, ServerError, MissingReqField
from threading import Thread


class ClientSender(Thread):
    '''class sends messages to server and interacts with a user'''
    def __init__(self, account_name, client_sock):
        self.account_name = account_name
        self.sock = client_sock
        super().__init__()

    
    @log_function
    def create_exit_message(self):
        '''возвращает словарь с действием:выход'''
        return {
            ACTION: EXIT,
            TIME: time.ctime(),
            ACCOUNT_NAME: self.account_name,
        }

    @log_function
    def create_message(self):  # sender_sock, sender_name='Guest'):
        '''запрашивает адресата и сообщение и отправляет на сервер
        '''
        # import pdb; pdb.set_trace()
        send_to = input('введите адресата сообщения ')
        message = input('Введите сообщение или x для завершения работы. ')
        if message == 'x' or send_to == 'x':
            self.sock.close()
            cl_logger.info("Клиент получил команду завершения")
            sys.exit(0)
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: send_to,
            TIME: time.ctime(),
            MESSAGE_TEXT: message,
        }
        cl_logger.info(f'Сформирован словарь-сообщение {message_dict}')
        try:
            send_message(self.sock, message_dict)
            cl_logger.info(f'{send_to} отправлено сообщение ')
        except Exception as e:
            cl_logger.error(f'lost connection {e}')
            sys.exit(1)


    @log_function
    def run(self):  # def user_interaction(self):  # sender_socket, dest_name):
        '''
        функция запрашивает у пользователя команду;
        в зависимости от нее завершает приложение или шлет сообщение
        '''
        self.list_available_commands()
        while True:
            command = input('Введите команду ')
            if command == 'message':
                self.create_message()  # ender_socket, dest_name)
            elif command == 'help':
                self.list_available_commands()
            elif command == 'exit':
                send_message(self.sock, self.create_exit_message())  # sender_socket, create_exit_message(dest_name))
                cl_logger.info(f'пользователь {self.account_name} завершил работу')
                time.sleep(0.5)
                break
            else:
                print('команда не распознана, не поддерживается')


    def list_available_commands(self):
        '''выводит список доступных команд'''
        print('список supported commands')
        print('message ввести сообщение')
        print('help список команд')
        print('exit выйти')


class ClientReader(Thread):
    '''class receives messages from server'''
    def __init__(self, account_name, client_sock):
        self.account_name = account_name
        self.sock = client_sock
        super().__init__()

    @log_function
    def run(self):  # def proc_msg_from_srv(self):  # sock, username):
        '''
        Функция-обработчик сообщений клиентов, 
        поступающих от сервера в клиентский сокет sock
        '''
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message\
                and message[ACTION] == MESSAGE\
                and SENDER in message\
                and DESTINATION in message\
                and MESSAGE_TEXT in message\
                and message[DESTINATION] == self.account_name:
                    cl_logger.info(f'got {message[MESSAGE_TEXT]} from {message[SENDER]}')
                else:
                    cl_logger.error(f'got incorrect {message}')
            except IncorrectDataReceived:
                cl_logger.error(f'не удалось декодировать {message}')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                cl_logger.critical(f'нет соединения с сервером')
                break


@log_function
def create_presence(account_name='Guest'):
    '''
    Возвращает словарь-сообщение д.сервера о присутствии клиента
    :param account_name
    :return:
    '''
    # {'action': 'presence', 'time': 111, 'user':{'account_name': account_name}}
    presence_msg = {
        ACTION: PRESENCE,
        TIME: time.ctime(),
        USER: {ACCOUNT_NAME: account_name}
    }
    cl_logger.info('Сформировано presence-сообщение')
    return presence_msg 


@Log_class(cl_logger)
def process_presns_answ(message):
    '''создает ответ на сообщение о присутствии'''
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            cl_logger.info('Обработан ответ сервера')
            return '200 : OK'
        elif message[RESPONSE] == 400:
            cl_logger.error('Неверный формат ответа сервера')
            raise ServerError(f'400 : {message[ERROR]}')
    else:
        cl_logger.critical('в словаре-ответе сервера нет необходимого ключа')
        raise MissingReqField(RESPONSE)


def main():
    '''
    Создает сокет на стороне клиента. Параметры получает из командной строки.
    Пример команды client.py -p 8079 -a 192.168.0.100
    '''
    # import pdb; pdb.set_trace()
    server_address, server_port, client_name = arg_parser()  # get ip and port
    if not client_name:
        client_name = input('Введите имя клиента. Это необходимо. ')
    print(f'CLIENT_MODULE {client_name}') 
    cl_logger.info(f'запущен клиент по имени {client_name}')
    # инициализация сокета
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        message_presence = create_presence(client_name)  # {'action': 'presence', 'time': 111, 'user': {account_name'}}
        send_message(client_socket, message_presence)
        # import pdb; pdb.set_trace()
        answer = process_presns_answ(get_message(client_socket))
        cl_logger.info(f'Установлено соединение с сервером {answer}')
    
    except (ValueError, json.JSONDecodeError) as e:
        cl_logger.error(f'Не удалось декодировать ответ сервера {e}')
        sys.exit(1)
    except ServerError as e:
        cl_logger.error(f'ошибка соединения с сервером {e}')
        sys.exit(1)
    except MissingReqField as e:
        cl_logger.error(f'в ответе сервера пропущено поле {e.missing_field}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError) as e:
        cl_logger.error(f'не удалось подключиться к {server_address}:{server_port}')
        sys.exit(1)
    else:
        # Запуск потоков приема и тправки
        receiver = ClientReader(client_name, client_socket)  # Thread(target=proc_msg_from_srv, args=(client_socket, client_name), daemon=True)
        # receiver.daemon = True
        receiver.start()  # запуск потока приема сообщений

        sender = ClientSender(client_name, client_socket)  # user_cli = Thread(target=user_interaction, args=(client_socket, client_name), daemon=True)
        # sender.daemon = True
        sender.start()  # запуск потока отправки сообщений # user_cli.start()
        cl_logger.info('запущены потоки обработки и отправки сообщений')
        
        # проверка условия прекращения работы модуля (существования обоих потоков)
        while True:
            time.sleep(1)
            if receiver.is_alive() and sender.is_alive():
                continue
            else:
                cl_logger.info('клиент прекратил работу')
                break
        
 
if __name__ == '__main__':
    # import pdb; pdb.set_trace()
    main()
    cl_logger.info('Клиент запущен в режиме main-скрипта')
