import socket
import sys
import time
import json
from threading import Thread, Lock
import hashlib
import hmac
import binascii

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
    message_205 = pyqtSignal()

    def __init__(self, port, ip_addr, database, user_name, pwd, key):
        Thread.__init__(self)
        QObject.__init__(self)

        self.db = database
        self.user_name = user_name
        self.pwd = pwd
        self.sock = None
        self.key = key
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
                cl_logger.info('connection established')
                break
            time.sleep(1)

        if not connected:
            cl_logger.error('could not establish a connetction')
            raise ServerError('could not establish a connetction')
        
        else:  # if  connected, authorize
            pwd_b = self.pwd.encode('utf-8')
            salt = self.user_name.lower().encode('utf-8')
            pwd_hash = hashlib.pbkdf2_hmac('sha512', pwd_b, salt, 10000)
            pwd_hash_str = binascii.hexlify(pwd_hash)
            
            cl_logger.info(f'pwdw hash is {pwd_hash_str}')

            pubkey = self.key.publickey().export_key().decode('ascii')
            
            # authorization__L6
            # import pdb; pdb.set_trace()  # L5
            with sock_lock:
                presence = {
                    ACTION: PRESENCE,
                    TIME: time.time(),
                    USER:{
                        ACCOUNT_NAME: self.user_name,
                        PUBLIC_KEY: pubkey
                    }
                }
                cl_logger.info(f'presence message {presence}')
                try:
                    # import pdb; pdb.set_trace()
                    send_message(self.sock, presence)
                    ans = get_message(self.sock)
                    cl_logger.info(f'server response {ans}')
                    if RESPONSE in ans:
                        if ans[RESPONSE] == 400:
                            raise ServerError(ans[ERROR])
                        elif ans[RESPONSE] == 511:
                            ans_data = ans[DATA]
                            hash = hmac.new(pwd_hash_str, ans_data.encode('utf-8'), 'MD5')
                            digest = hash.digest()
                            my_ans = RESPONSE_511
                            my_ans[DATA] = binascii.b2a_base64(digest).decode('utf-8')
                            send_message(self.sock, my_ans)
                            self.process_server_ans(get_message(self.sock))
                except (OSError, json.JSONDecodeError) as e:
                    cl_logger.error('lost connection', e)
                    raise ServerError('lost connection')
   
    def process_server_ans(self, message):
        # processes a message from a server
        logger.debug(f'parsing message {message}')

        # analyze message type
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(message[ERROR])
            elif message[RESPONSE] == 205:
                self.update_users_list()
                self.update_contacts_list()
                self.message_205.emit()
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
            # self.db.save_message(message[SENDER], 'in', message[MESSAGE_TEXT])
            self.new_message.emit(message[SENDER])

    def update_contacts_list(self):
        # updates contacts list of server
        self.db.clear_contacts()
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

    def key_request(self, user):
        '''requests users public key for user'''
        cl_logger.info(f"{user}'s public key request")
        req = {
            ACTION: KEY_REQ,
            TIME: time.time(),
            ACCOUNT_NAME: user
        }
        with sock_lock:
            send_message(self.sock, req)
            ans = get_message(self.sock)
        if RESPONSE in ans and ans[RESPONSE] == 511:
            return ans[DATA]
        else:
            cl_logger.error(f"could not get {user}'s key")

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
            time.sleep(1)  # await sendind
            message = None
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
                finally:
                    self.sock.settimeout(5)
                
            # if got message
            if message:
                cl_logger.info(f'got message {msg}')
                self.process_server_ans(msg)
                