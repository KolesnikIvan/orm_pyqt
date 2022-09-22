# import pdb; pdb.set_trace()  # L4
import json
import sys
import socket
import time
from common.utils import get_message, send_message, arg_parser
from common.variables import (
    DEFAULT_PORT, DEFAULT_SRV_IP,
    ACTION, TIME,
    USER, ACCOUNT_NAME,
    SENDER, PRESENCE,
    RESPONSE, ERROR,
    MESSAGE, MESSAGE_TEXT,
    DESTINATION, EXIT,
    GET_CONTACTS, LIST_INFO, 
    DEL_CONTACT, ADD_CONTACT, 
    USERS_LIST
    )
from logs.config_log_client import cl_logger
from decos import Log_class, log_function
from errors import IncorrectDataReceived, NonDictInputError, ServerError, MissingReqField
from threading import Thread, Lock
from metaclasses import ClientVerifier
from client_database import ClientDB
from PyQt5.QtWidgets import QApplication

sock_lock = Lock()      # Lock object to work with the client socket
db_lock = Lock()        # Lock object to work with the datbase

class ClientSender(Thread, metaclass=ClientVerifier):
    # class sends messages to server and interacts with a user
    def __init__(self, account_name, client_sock, database):
        self.account_name = account_name
        self.sock = client_sock
        self.db = database
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
        message = input('Введите сообщение или exit для завершения работы. ')
        
        with db_lock:
            # check receiver exists
            # import pdb; pdb.set_trace()
            if not self.db.is_known(send_to):
                cl_logger.info(f'try to send message to unknown user {send_to}')
                return
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: send_to,
            TIME: time.ctime(),
            MESSAGE_TEXT: message,
        }
        cl_logger.info(f'Сформирован словарь-сообщение {message_dict}')

        with db_lock:
            # save message to archive
            self.db.save_message(self.account_name, send_to, message)

        with sock_lock:
            try:
                send_message(self.sock, message_dict)
                time.sleep(1)
                cl_logger.info(f'{send_to} отправлено сообщение ')
            except OSError as e:
                if e.errno:
                    cl_logger.error('lost connection to the werver')
                    exit(1)
                else:
                    cl_logger.error('couldnt send message$ connection timeout')

        # if message == 'exit' or send_to == 'exit':
        #     self.sock.close()
        #     cl_logger.info("Клиент получил команду завершения")
        #     sys.exit(0)
        # message_dict = {
        #     ACTION: MESSAGE,
        #     SENDER: self.account_name,
        #     DESTINATION: send_to,
        #     TIME: time.ctime(),
        #     MESSAGE_TEXT: message,
        # }
        # cl_logger.info(f'Сформирован словарь-сообщение {message_dict}')
        # try:
        #     send_message(self.sock, message_dict)
        #     cl_logger.info(f'{send_to} отправлено сообщение ')
        # except Exception as e:
        #     cl_logger.error(f'lost connection {e}')
        #     sys.exit(1)

    @log_function
    def run(self):  # def user_interaction(self):  # sender_socket, dest_name):
        '''
        функция запрашивает у пользователя команду;
        в зависимости от нее завершает приложение или шлет сообщение
        '''
        self.list_available_commands()
        while True:
            command = input('Введите команду ')
            # import pdb; pdb.set_trace()  # L4
            if command == 'message':
                self.create_message()  # ender_socket, dest_name)
                time.sleep(1)
            elif command == 'help':
                self.list_available_commands()
            elif command == 'exit':
                with sock_lock:
                    try:
                        send_message(self.sock, self.create_exit_message())  # sender_socket, create_exit_message(dest_name))
                    except Exception as e:
                        print(e)
                        cl_logger.info(e)
                        pass
                    print('finishing connecton')
                    cl_logger.info(f'пользователь {self.account_name} завершил работу')
                time.sleep(0.5)
                break
            
            elif command == 'contacts':     # запрос списка контактов
                # import pdb; pdb.set_trace()  #L4
                with db_lock:
                    contacts_list = self.db.get_contacts()
                    for contact in contacts_list:
                        print(contact)
            
            elif command == 'edit':         # запрос редактирования контактов
                self.edit_contacts()

            elif command == 'history':      # запрос списка переданных сообщений
                self.print_history()

            else:
                print('команда {command} не распознана, не поддерживается')

    def list_available_commands(self):
        '''выводит список доступных команд'''
        print('список supported commands')
        print('message ввести сообщение')
        print('history история сообщений')
        print('contacts список контактов')
        print('edit редактировать список контактов')
        print('help список команд')
        print('exit выйти')

    def print_history(self):
        # prints out messages story
        ask = input('what messages to show: INcoming, OUTcoming, all=Enter')
        with db_lock:
            if ask == 'IN':
                hist_list = self.db.get_messages_hist(to_whom=self.account_name)
                for message in hist_list:
                    print(f'message from {message[0]} to {message[3]}:{message[2]}')
            elif ask == 'OUT':
                hist_list = self.db.get_messages_hist(from_whom=self.account_name)
                for message in hist_list:
                    print(f'message from {message[0]} to {message[3]}:{message[2]}')
            else:
                hist_list = self.db.get_messages_hist()
                for message in hist_list:
                    print(f'message from {message[0]} to {message[3]}:{message[2]}')
    
    def edit_contacts(self):
        # changes contact
        # import pdb; pdb.set_trace()  # L4
        act = input('to delete type del, to add type add ')
        if act == 'del':
            contact = input('type name of contact to delete ')
            with db_lock:
                if self.db.is_contact(contact):
                    self.db.del_contact(contact)
                else:
                    cl_logger.error('try to delete the contact that does not exist')
        elif act == 'add':
            contact_name = input('type name of contact to add ')
            if not self.db.is_known(contact_name):
                with db_lock:
                    self.db.add_contact(contact_name)
                with sock_lock:
                    try:
                        add_contact(self.sock, self.account_name, contact_name)
                        time.sleep(1)
                    except ServerError:
                        cl_logger.error('could not send information to server')


class ClientReader(Thread, metaclass=ClientVerifier):
    '''class receives messages from server'''
    def __init__(self, account_name, client_sock, database):
        self.account_name = account_name
        self.sock = client_sock
        self.db = database
        super().__init__()

    @log_function
    def run(self):  # def proc_msg_from_srv(self):  # sock, username):
        '''
        Функция-обработчик сообщений клиентов, 
        поступающих от сервера в клиентский сокет sock
        '''
        while True:
            time.sleep(1)
            with sock_lock:
                try:
                    message = get_message(self.sock)
                except IncorrectDataReceived as e:
                    cl_logger.error(f'{e} не удалось декодировать {message}')
                except OSError as e:
                    if e.errno:
                        cl_logger.critical(f'нет соединения с сервером')
                        break
                except (ConnectionError,ConnectionAbortedError, 
                        ConnectionResetError, json.JSONDecodeError):
                    cl_logger.critical(f'нет соединения с сервером')
                    break
                else:
                    message = get_message(self.sock)
                    if ACTION in message\
                    and message[ACTION] == MESSAGE\
                    and SENDER in message\
                    and DESTINATION in message\
                    and MESSAGE_TEXT in message\
                    and message[DESTINATION] == self.account_name:
                        print(f'got message from {message[SENDER]}:{message[MESSAGE_TEXT]}')
                        with db_lock:
                            try:
                                self.db.save_message(message[SENDER], self.account_name, message[MESSAGE_TEXT])
                            except Exception as e:
                                print(e)
                                cl_logger.error('database interaction error')
                        cl_logger.info(f'got {message[MESSAGE_TEXT]} from {message[SENDER]}')
                    else:
                        cl_logger.error(f'got incorrect {message}')


@log_function
def create_presence(account_name='Guest'):
    '''
    Возвращает словарь-сообщение д.сервера о присутствии клиента
    :param account_name
    :return presence message:
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
def process_presnc_answ(message):
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

def contacts_list_request(sock, user_name):
    # requests contacts list of user_name
    # :param: sock
    # :param: user_name
    cl_logger.info(f'requested list of contacts of {user_name}')
    req = {
        ACTION: GET_CONTACTS,
        TIME: time.ctime(),
        USER: user_name
    }
    cl_logger.info(f'built contacts request {req}')
    send_message(sock, req)
    # time.sleep(1)
    # import pdb; pdb.set_trace()  # L4
    ans = get_message(sock)
    cl_logger.debug(f'got answer {ans}')
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError

def add_contact(sock, user_name, contact_name):
    # adds user to a contact list
    cl_logger.info(f'create contact {contact_name}')
    req = {
        ACTION: ADD_CONTACT,
        TIME: time.ctime(),
        USER: user_name,
        ACCOUNT_NAME: contact_name
    }
    cl_logger.info(f'built add contact request {req}')
    send_message(sock, req)
    # time.sleep(1)
    # import pdb; pdb.set_trace()
    ans = get_message(sock)
    cl_logger.debug(f'got answer {ans}')
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('contact creation error')
    print(f'contact {user_name}:{contact_name} created successfully')

def user_list_request(sock, user_name):
    # requests list of users
    # :param: sock
    # :param: user_name
    cl_logger.info(f'requested list of users of {user_name}')
    req = {
        ACTION: USERS_LIST,
        TIME: time.ctime(),
        ACCOUNT_NAME: user_name
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 202:
        return ans[LIST_INFO]
    else:
        raise ServerError

def remove_contact(sock, user_name, contact_name):
    # remove contact
    # :param: sock
    # :param: user_name
    cl_logger.info(f'delete contact {contact_name}')
    req = {
        ACTION: DEL_CONTACT,
        TIME: time.ctime(),
        USER: user_name,
        ACCOUNT_NAME: contact_name
    }
    send_message(sock, req)
    ans = get_message(sock)
    if RESPONSE in ans and ans[RESPONSE] == 200:
        pass
    else:
        raise ServerError('delete error')
    print('successfully deleted')

def database_load(sock, database, user_name):
    # load database
    # :param: sock
    # :param: database
    # :param: user_name
    # import pdb; pdb.set_trace()
    try:
        users_list = user_list_request(sock, user_name)
    except ServerError:
        cl_logger.error('users list request error')
    else:
        database.add_users(users_list)

    try: 
        contacts_list = contacts_list_request(sock, user_name)
    except ServerError:
        cl_logger.error('contacts request error')
    else:
        for contact in contacts_list:
            database.add_contact(contact)


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
        client_socket.settimeout(1)
        client_socket.connect((server_address, server_port))
        time.sleep(1)
        message_presence = create_presence(client_name)  # {'action': 'presence', 'time': 111, 'user': {account_name'}}
        time.sleep(1)
        send_message(client_socket, message_presence)
        # import pdb; pdb.set_trace()
        time.sleep(1)
        ans = get_message(client_socket)
        answer = process_presnc_answ(ans)
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
        # import pdb; pdb.set_trace()  # L4 initialize db
        db = ClientDB(client_name)
        database_load(client_socket, db, client_name)
        # Запуск потоков приема и отправки
        receiver = ClientReader(client_name, client_socket, db)  # Thread(target=proc_msg_from_srv, args=(client_socket, client_name), daemon=True)
        receiver.daemon = True
        receiver.start()  # запуск потока приема сообщений

        sender = ClientSender(client_name, client_socket, db)  # user_cli = Thread(target=user_interaction, args=(client_socket, client_name), daemon=True)
        sender.daemon = True
        sender.start()  # запуск потока отправки сообщений # user_cli.start()
        cl_logger.info('запущены потоки обработки и отправки сообщений')
        time.sleep(2)

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
