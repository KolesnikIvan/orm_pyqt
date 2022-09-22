import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pathlib import Path
import socket
import json
from common.utils import get_message, send_message, arg_parser
from common.variables import (
    MAX_CONNECTIONS, DEFAULT_PORT, ACTION, ACCOUNT_NAME,
    PRESENCE, RESPONSE_202, TIME, USER,
    SENDER, RESPONSE, PRESENCE, ERROR,
    MESSAGE, MESSAGE_TEXT, RESPONSE_400, DESTINATION,
    RESPONSE_200, RESPONSE_202, EXIT, GET_CONTACTS,
    LIST_INFO, ADD_CONTACT, DEL_CONTACT, USERS_LIST
    )
from logs.config_log_server import srv_logger
from common.decos import log_function, Log_class  # L5
from select import select
import time
from metaclasses import ServerVerifier
from descriptors import Port
from threading import Thread, Lock
from srv_db import ServerStorage

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from srv_gui import (
    MainWindow,
    gui_create_table,
    HistoryWindow,
    gui_create_hist,
    ConfigWindow,
)
import configparser

# если пользователь новый, обратиться к базе
connection_is_new = False  
conn_flag_lock = Lock()

class Server(Thread, metaclass=ServerVerifier):
    port = Port()
    def __init__(self, listen_address, listen_port, database):
        self.ip = listen_address
        self.port = listen_port
        self.clients = []           # список активных клиентов
        self.msgs_to_send = []      # список сообщений
        self.names = dict()         # словарь {имя: клиент-сокет}
        self.db = database          # lesson3 server database
        super().__init__()

    def init_socket(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # import pdb; pdb.set_trace()
        server_socket.bind((self.ip, self.port))
        server_socket.settimeout(0.5)
        self.sock = server_socket
        self.sock.listen() # MAX_CONNECTIONS)    # связывание сокета с портом
        srv_logger.info(f'Сервер запущен по адресу {self.ip}:{self.port}')

    def run(self):
        ''' Создает сокет на стороне сервера на хосте и порте из командной строки.'''
        # import pdb; pdb.set_trace()
        global connection_is_new
        self.init_socket()
        while True:
            try:
                client_sock, client_address = self.sock.accept()
            except (ValueError, json.JSONDecodeError):
                srv_logger.error('Сообщение от клиента некорректно')
                sys.exit(1)
            except OSError as e:
                # srv_logger.error(f'ошибка {e} на сервере')  # эта строка вывод при работе сервера
                pass
            else:
                srv_logger.info(f'установлено соединение с клиентом {client_address}')
                self.clients.append(client_sock)
            socks_to_receive = []
            socks_to_answer = []
            err = []
            try:  # проверка наличия клиентов
                if self.clients:
                    socks_to_receive, socks_to_answer, err = select(self.clients, self.clients, [], 0)
                    print('read', socks_to_receive)
            except OSError as e:
                srv_logger.error(f'ошибка {e} при использовании сервером модуля select')
                pass

            # сообщение в словарь, иначе удаляем клиента из списка
            if socks_to_receive:
                for sender in socks_to_receive:
                    try:  # process message to add it in messages list
                        # import pdb; pdb.set_trace()
                        self.proc_msg_fr_client(get_message(sender), sender)
                    # except Exception as e:
                    #     pass
                        # srv_logger.info(f'клиент {sender} отключился')
                        # self.clients.remove(sender)
                    except OSError as e:  # L5
                        # import pdb; pdb.set_trace()  # L5
                        srv_logger.info(f'client {sender.getpeername()} has disconnected')
                        for nm in self.names:
                            if self.names[nm] == sender:
                                self.db.user_logout(nm)
                                del self.names[nm]
                                break
                        self.clients.remove(sender)
                        with conn_flag_lock:
                            connection_is_new = True

            for msg in self.msgs_to_send:
                # import pdb; pdb.set_trace()  # L5
                try:
                    self.proc_msg_to_client(msg, socks_to_answer)
                except Exception as e:
                    srv_logger.info(f'утрачена связь с клиентом msg[DESTINATION]')
                    self.clients.remove(self.names[msg[DESTINATION]])
                    self.db.user_logout(msg[DESTINATION])
                    del self.names[msg[DESTINATION]]
                    with conn_flag_lock:
                        connection_is_new = True
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
        global connection_is_new
        srv_logger.info(f'разбор сообщения {message} от клиента {client_sock}')
        # если дежурное приветствие, то принять и ответить
        # import pdb; pdb.set_trace()  # L4  из-за этой остановки клиенты отключаются по таймауту, остановка в начале процедуры обработки сообщений не позволяет им подключиться
        if ACTION in message\
        and message[ACTION] == PRESENCE\
        and TIME in message\
        and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                # если клиент впервые, внести в names, в базу, ответить 200:ok
                self.names[message[USER][ACCOUNT_NAME]] = client_sock
                client_ip, client_port = client_sock.getpeername()  # L3
                self.db.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                # import pdb; pdb.set_trace()
                send_message(client_sock, RESPONSE_200)
                with conn_flag_lock:
                    connection_is_new = True
                srv_logger.info('Получено корректное сообщение от клиента, сформирован ответ 200')
            else:
                response = RESPONSE_400
                response[ERROR] = 'клиент с таким именем зарегистрирован'
                send_message(client_sock, response)
                srv_logger.error('Получено некорректное сообщение от клиента')
                self.clients.remove(client_sock)    # L3
                client_sock.close()
            return
        # если целевое сообщение, внести в список сообщений, не отвечать
        elif ACTION in message\
        and message[ACTION] == MESSAGE\
        and DESTINATION in message\
        and TIME in message\
        and SENDER in message\
        and MESSAGE_TEXT in message\
        and self.names[message[SENDER]] == client_sock:
            
            if message[DESTINATION] in self.names:
                self.msgs_to_send.append(message)
                # import pdb; pdb.set_trace()  # L4
                self.db.reg_message(
                    message[SENDER],
                    message[DESTINATION]
                )
                send_message(client_sock, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = f'user {message[DESTINATION]} is not registred'
                send_message(client_sock, response)
            return
        # если сообщение о выходе
        elif ACTION in message\
        and message[ACTION] == EXIT\
        and ACCOUNT_NAME in message\
        and self.names[message[ACCOUNT_NAME]] == client_sock:  # client disconnects
            self.db.user_logout(message[ACCOUNT_NAME]) # L3
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            with conn_flag_lock:
                connection_is_new = True
            srv_logger.info(f'user {message[ACCOUNT_NAME]} left the chat')
            return
        # запрос списка контактов
        elif ACTION in message\
        and message[ACTION] == GET_CONTACTS\
        and USER in message\
        and self.names[message[USER]] == client_sock:
            # import pdb; pdb.set_trace() 
            response = RESPONSE_202
            response[LIST_INFO] = self.db.get_user_contacts(message[USER])
            send_message(client_sock, response)
        # запрос на добавление контакта
        elif ACTION in message\
        and message[ACTION] == ADD_CONTACT\
        and ACCOUNT_NAME in message\
        and USER in message\
        and self.names[message[USER]] == client_sock:
            # import pdb; pdb.set_trace()  # L4 # остановка здесь тоже вызывает TimeoutError у клиента
            self.db.add_contact(message[USER], message[ACCOUNT_NAME])
            send_message(client_sock, RESPONSE_200)
        # запрос на удаление контакта
        elif ACTION in message\
        and message[ACTION] == DEL_CONTACT\
        and ACCOUNT_NAME in message\
        and USER in message\
        and self.names[message[USER]] == client_sock:
            self.db.remove_contact(message[USER], message[ACCOUNT_NAME])
            send_message(message[USER], RESPONSE_200)
        # запрос списка пользователей 
        elif ACTION in message\
        and message[ACTION] == USERS_LIST\
        and ACCOUNT_NAME in message\
        and self.names[message[ACCOUNT_NAME]] == client_sock:
            response = RESPONSE_202
            response[LIST_INFO] = [user[0] for user in self.db.users_list()]
            send_message(client_sock, response)
        # иначе уведомить об ошибке
        else:
            response = RESPONSE_400
            response[ERROR] = 'request is incorrect'
            send_message(client_sock, response)
            return 

def server_config_load():
    # downloads server configuration from a server.ini file
    # import pdb; pdb.set_trace()  # L5
    config = configparser.ConfigParser()
    config_path = os.path.dirname(os.path.realpath(__file__))
    # config.read(f"{config_path}/{'server.ini'}")
    config.read(os.path.join(config_path, 'server.ini'))
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'srv_db.db3')
        return config

def main():
    '''получение хоста и порта из командной строки'''    
    # import pdb; pdb.set_trace()  # L4
    config = server_config_load()

    listen_address, listen_port, _ = arg_parser(config['SETTINGS']['listen_address'], config['SETTINGS']['default_port'])
    # создание экземпляра сервер
    # import pdb; pdb.set_trace()  # L4 added path
    # db = ServerStorage(config['SETTINGS']['database_path'])  # database initialize
    db = ServerStorage(os.path.join(config['SETTINGS']['database_path'],
                                    config['SETTINGS']['database_file']))  # database initialize
    server = Server(listen_address, listen_port, db)
    server.daemon = True
    # import pdb; pdb.set_trace()  # L4 crete gui
    server.start()  # L3
    
    # list_available_commands()   # print help
    # create server gui
    server_app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.statusBar().showMessage('Server is on')
    main_win.active_clients.setModel(gui_create_table(db))
    main_win.active_clients.resizeColumnsToContents()
    main_win.active_clients.resizeRowsToContents()

    def list_update():
        # func to renews connected clients list
        global connection_is_new
        if connection_is_new:
            main_win.active_clients.setModel(gui_create_table(db))
            main_win.active_clients.resizeColumnsToContents()
            main_win.active_clients.resizeRowsToContents()
            with conn_flag_lock:
                connection_is_new = False
    
    def show_stat():
        # func shows clients' satisctics window
        # import pdb; pdb.set_trace()
        global stat_win  # declare as global to access in the outer scope
        stat_win = HistoryWindow()
        stat_win.history_table.setModel(gui_create_hist(db))
        stat_win.history_table.resizeColumnsToContents()
        stat_win.history_table.resizeRowsToContents()
        stat_win.show()

    def server_config_win(): # L4
        # func creates server settings window
        global config_window
        config_window = ConfigWindow()
        config_window.db_path.insert(config['SETTINGS']['database_path'])
        config_window.db.insert(config['SETTINGS']['database_file'])
        config_window.port.insert(config['SETTINGS']['default_port'])
        config_window.ip.insert(config['SETTINGS']['listen_address'])
        config_window.save_btn.clicked.connect(server_config_save)

    def server_config_save():
        # import pdb; pdb.set_trace()  # L4 follow thiss function
        global config_window
        message = QMessageBox()
        config['SETTINGS']['database_path'] = config_window.db_path.text()
        config['SETTINGS']['database_file'] = config_window.db_file.text() 
        # при приеме этих параметров могут вохникнуть синтаксические ошибки
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Error', 'Port must be a number')
        else:
            config['SETTINGS']['listen_address'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['default_port'] = str(port)
                print('port is ', port)
                with open('srv.ini', 'w') as conf:
                    config.write(conf)
                    message.information(config_window, 'OK', 'Settigns are successfully saved')
            else:
                message.warning(config_window, 'OK', 'Settigns are not saved')
    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    main_win.refresh.triggered.connect(list_update)
    main_win.show_hist.triggered.connect(show_stat)
    main_win.config.triggered.connect(server_config_win)

    server_app.exec_()  # launch gui in a main thread


if __name__ == '__main__':
    import pdb; pdb.set_trace()  #L4
    main()
    # db = ServerStorage('sqlite:///srv_db.db3')
    # hist_table = gui_create_hist(db) # L4 debug microsecond(s)
