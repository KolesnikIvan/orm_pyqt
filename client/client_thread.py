import socket
import sys
import time
import json
from threading import Thread, Lock
from PyQt5.QtCore import pyqtSignal, QObject
from logs.config_log_client import cl_logger

sys.path.append('../')
from common.utils import *
from common.variables import *
from common.errors import ServerError

sock_lock = Lock()

class ClientThread(Thread, QObject):
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, port, ip_addr, database, user_name):
        Thread.__init__(self)
        QObject.__init__(self)

        self.db = database
        self.user_name = user_name
        self.sock = None
        self.connection_init(ip_addr, port)

        try:
            self.update_users_list()
            self.update_contacts_list()
        except OSError as e:
            if e.errno:
                cl_logger.critical(f'{user_name} lost connection')
                raise ServerError(f'{user_name} lost connection')
            cl_logger.error('Timeout by connection refresh')
        except json.JSONDecodeError:
            cl_logger.error('lost connection')
            raise ServerError('lost connection')
        self.running = True

    def connection_init(self, ip_addr, port_num):
        '''initializes socket and notifies the server'''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5)
        connected = False
        for i in range(5):
            cl_logger.info(f'conection try {i+1}')
            try:
                self.sock.connect((ip_addr, port_num))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)

        if not connected:
            cl_logger.error('could not establish a connetction')
            raise ServerError('could not establish a connetction')
        
        else:
            cl_logger.info('client has connected to the server {ip_addr}:{port_num}')
            # if connected, send presence message and get answer
            try:
                # import pdb; pdb.set_trace()  # L5
                with sock_lock:
                    send_message(self.sock, self.create_presence_message())
                    self.process_server_ans(get_message(self.sock))
            except (OSError, json.JSONDecodeError) as e:
                cl_logger.error('lost connection', e)
                raise ServerError('lost connection')

            else:
                cl_logger.info(f'client {self.user_name} successfully connected to a server')

    def create_presence_message(self):
        # generate greeting message to server
        out = {
            ACTION: PRESENCE,
            TIME: time.ctime(),
            USER: {ACCOUNT_NAME: self.user_name}
        }
        cl_logger.info(f'built {PRESENCE} message {out}')
        return out

    def process_server_ans(self, message):
        # processes a message from a server
        logger.debug(f'parsing message {message}')

        # analyze message type
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(message[ERROR])
            else:
                logger.debug(f'got unknown response code {message[RESPONSE]}')

        # if got a message from client, add the message to the base and emit signal
        elif ACTION in message \
                and message[ACTION] == MESSAGE \
                and SENDER in message \
                and DESTINATION in message \
                and MESSAGE_TEXT in message \
                and message[DESTINATION] == self.user_name:
            cl_logger.info(f'got message from {message[SENDER]}:'
                         f'{message[MESSAGE_TEXT]}')
            self.db.save_message(message[SENDER], 'in', message[MESSAGE_TEXT])
            self.new_message.emit(message[SENDER])

    def update_contacts_list(self):
        # updates contacts list of server
        cl_logger.info(f"{self.user_name}'s contacts list requested")
        req = {
            ACTION: GET_CONTACTS,
            TIME: time.ctime(),
            USER: self.user_name
        }
        cl_logger.info(f'built request {req}')
        with sock_lock:
            # import pdb; pdb.set_trace()  # L5
            send_message(self.sock, req)
            ans = get_message(self.sock)
        cl_logger.info(f'got answer {ans}')
        if RESPONSE in ans and ans[RESPONSE] == 202:
            for contact in ans[LIST_INFO]:
                self.db.add_contact(contact)
        else:
            cl_logger.error('could not update contacts list')

    def update_users_list(self):
        # updates familar users list
        cl_logger.debug(f"{self.user_name}'s familar users requested")
        req = {
            ACTION: USERS_LIST,
            TIME: time.ctime(),
            ACCOUNT_NAME: self.user_name
        }
        # import pdb; pdb.set_trace()  # L5
        with sock_lock:
            send_message(self.sock, req)
            ans = get_message(self.sock)
        if RESPONSE in ans and ans[RESPONSE] == 202:
            self.db.add_users(ans[LIST_INFO])
        else:
            cl_logger.error('could not update users list')

    def add_contact_notification(self, contact_name):
        # notes the server the contact's been added
        cl_logger.info(f'createing contact {contact_name}')
        req = {
            ACTION: ADD_CONTACT,
            TIME: time.ctime(),
            USER: self.user_name,
            ACCOUNT_NAME: contact_name
        }
        with sock_lock:
            send_message(self.sock, req)
            self.process_server_ans(get_message(self.sock))

    def remove_contact(self, contact_name):
        # sends deletion contact message
        cl_logger.info(f'removing {contact_name}')
        req = {
            ACTION: DEL_CONTACT,
            TIME: time.ctime(),
            USER: self.user_name,
            ACCOUNT_NAME: contact_name
        }
        with sock_lock:
            send_message(self.sock, req)
            self.process_server_ans(get_message(self.sock))

    def sock_shutdown(self):
        # sends message about connection close
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time.ctime(),
            ACCOUNT_NAME: self.user_name
        }
        with sock_lock:
            try:
                send_message(self.sock, message)
            except OSError:
                pass
        cl_logger.info('ClientThread ends work')
        time.sleep(1)

    def send_message(self, to, message):
        # sends message to server, waits while target socket is available
        msg = {
            ACTION: MESSAGE,
            SENDER: self.user_name,
            DESTINATION: to,
            TIME: time.ctime(),
            MESSAGE_TEXT: message
        }
        cl_logger.info(f'built message {msg}')
        with sock_lock:
            send_message(self.sock, msg)
            # import pdb; pdb.set_trace()
            self.process_server_ans(get_message(self.sock))
            cl_logger.info(f'sent message from {self.user_name} to {to}')

    def run(self):
        cl_logger.info('client message receiver process has been launched')
        while self.running:
            time.sleep(1)
            with sock_lock:
                try:
                    self.sock.settimeout(0.5)
                    msg = get_message(self.sock)
                except OSError as e:
                    if e.errno:  # TimeoutError.errno = None
                        cl_logger.error(f'lost connection')
                        self.running = False
                        self.connection_lost.emit()
                except (ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError, TypeError):
                    cl_logger.info('lost connection')
                    self.running = False
                    self.connection_lost.emit()
                else:  # if got message
                    cl_logger.info(f'got message {msg}')
                    self.process_server_ans(msg)
                finally:
                    self.sock.settimeout(5)
