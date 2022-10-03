import sys 
import os
import json
import base64
# import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt5.QtWidgets import QMainWindow, qApp, QMessageBox, QApplication, QListView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtCore import pyqtSlot, QEvent, Qt
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA

from client.main_win_converted import Ui_MainClientWindow
from client.add_contact_dialog import SelectContactToAddDialog
from client.del_contact_dialog import SelectContactToDelDialog
from client.client_database import ClientDB
from client.client_thread import ClientThread
# from client.start_dialog import SelectUserNameDialog
from common.errors import ServerError
from common.variables import *
from logs.config_log_client import cl_logger

# client main window
class ClientMainWin(QMainWindow):
    def __init__(self, database, client_thread, keys):
        super().__init__()
        self.db = database
        self.sock = client_thread

        self.decrypter = PKCS1_OAEP.new(keys)

        self.ui = Ui_MainClientWindow()
        self.ui.setupUi(self)
        self.ui.menu_exit.triggered.connect(qApp.exit)
        self.ui.btn_send.clicked.connect(self.send_message)
        self.ui.btn_add_contact.clicked.connect(self.add_contact_window)
        self.ui.menu_add_contact.triggered.connect(self.add_contact_window)
        # del contact
        self.ui.btn_remove_contact.clicked.connect(self.delete_contact_window)
        self.ui.menu_del_contact.triggered.connect(self.delete_contact_window)
        # additional attributes
        self.contacts_model = None
        self.hist_model = None
        self.messages = QMessageBox()
        self.current_chat = None  # current conversation
        self.current_chat_key = None
        # import pdb; pdb.set_trace()  # L5
        self.encryptor = None

        self.ui.messages_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.messages_list.setWordWrap(True)
        # tie double click on contact list with handler
        self.ui.list_contacts.doubleClicked.connect(self.select_active_user)
        self.update_clients_list()
        # import pdb; pdb.set_trace()
        self.set_disabled_input()
        self.show()        

    def set_disabled_input(self):
        # clears destination field
        self.ui.label_new_message.setText('to select receiver double click him')
        self.ui.message_text.clear()
        if self.hist_model:
            self.hist_model.clear()
        self.ui.btn_clear.setDisabled(True)
        self.ui.btn_send.setDisabled(True)
        self.ui.message_text.setDisabled(True)
        # L6
        self.encryptor = None
        self.current_chat = None
        self.current_chat_key = None

    def update_hist_list(self):
        # fill communication history
        import pdb; pdb.set_trace()  # L5
        messages_list = sorted(self.db.get_messages_hist(self.current_chat), key=lambda item: item[3])
        # messages_list = self.db.get_messages_hist(self.current_chat)
        print('hello___', messages_list)
        if not self.hist_model:  # if there's no model, create one
            self.hist_model = QStandardItemModel()
            self.ui.messages_list.setModel(self.hist_model)
        self.hist_model.clear()  # clear old data
        # show 20 records
        length = len(messages_list)
        msg_index = 0 if length <= 20 else length - 20    
        for i in range (msg_index, length):
            item = messages_list[i]
            if item[1] == 'in':
                mess = QStandardItem(f'in from {item[3]}:{item[2]}')  # .replace(microsecond=0)}:\n {item[2]}')
                mess.setEditable(False)
                mess.setBackground(QBrush(QColor(255, 213, 213)))
                mess.setTextAlignment(Qt.AlignLeft)
                self.hist_model.appendRow(mess)
            else:
                mess = QStandardItem(f'out from {item[3]}:{item[2]}')  # .replace(microsecond=0)}:\n {item[2]}')
                mess.setEditable(False)
                mess.setBackground(QBrush(QColor(204, 255, 204)))
                mess.setTextAlignment(Qt.AlignRight)
                self.hist_model.appendRow(mess)
        self.ui.messages_list.scrollToBottom()

    def select_active_user(self):
        # handles contact double click
        # import pdb; pdb.set_trace()  # L5
        self.current_chat = self.ui.list_contacts.currentIndex().data()
        self.set_active_user()

    def set_active_user(self):
        try:
            self.current_chat_key = self.sock.key_request(self.current_chat)
            cl_logger.info(f'public key {self.current_chat} is loaded')
            if self.current_chat_key:
                self.encryptor = PKCS1_OAEP.new(RSA.import_key(self.current_chat_key))
        except (OSError, json.JSONDecodeError):
            self.current_chat_key = None
            self.encryptor = None
            cl_logger.info(f'could not get public key for {self.current_chat}')
        if not self.current_chat_key:  # error if theres no key
            self.messages.warning(self, 'Error', 'selected user has no encryptor key')
            return
        # L5 sets active current vis-a-vis
        self.ui.label_new_message.setText(f'type message for {self.current_chat}')
        self.ui.btn_clear.setDisabled(False)
        self.ui.btn_send.setDisabled(False)
        self.ui.message_text.setDisabled(False)
        self.update_hist_list()

    def update_clients_list(self):
        # updates list of contcts
        contacts_list = self.db.get_contacts()
        self.contacts_model = QStandardItemModel()
        for cont in sorted(contacts_list):
            item = QStandardItem(cont)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.ui.list_contacts.setModel(self.contacts_model)

    def add_contact_window(self):
        # adds contact
        global select_dialog
        select_dialog = SelectContactToAddDialog(self.sock, self.db)
        select_dialog.btn_ok.clicked.connect(lambda: self.add_contact_action(select_dialog))
        select_dialog.show()

    def add_contact_action(self, item):
        # handles add, notes server, updates table and contact list
        new_contact = item.selector.currentText()
        self.add_contact(new_contact)
        item.close()

    def add_contact(self, new_contact):
        # adds a contact into the database
        try:
            self.sock.add_contact_notification(new_contact)
        except ServerError as e:
            self.messages.critical(self, 'server error', e.text)
        except OSError as e:
            if e.errno:
                self.messages.critical(self, 'lost connection', e.text)
                self.close()
            self.messages.critical(self, 'connection lost', 'timeout')
        else:
            self.db.add_contact(new_contact)
            new_contact = QStandardItem(new_contact)
            new_contact.setEditable(False)
            self.contacts_model.appendRow(new_contact)
            cl_logger.info(f'contact {new_contact} succesfully added')
            self.messages.information(self, 'success', 'new contact succesfully added {new_contact}')

    def delete_contact_window(self):
        # deletes contact
        global remove_dialog
        remove_dialog = SelectContactToDelDialog(self.db)
        remove_dialog.btn_ok.clicked.connect(lambda: self.delete_contact(remove_dialog))
        remove_dialog.show()

    def delete_contact(self, item):
        # handles contact deletion, notes server, updtaes table of contacts
        # import pdb; pdb.set_trace()  # L5
        selected = item.selector.currentText()
        try:
            self.sock.remove_contact(selected)
        except ServerError as e:
            self.messages.critical(self, 'server error', e.text)
        except OSError as e:
            if e.errno:
                self.messages.critical(self, f'lost connection', e.text)
                self.close()
            self.messages.critical(self, 'timeout error', 'timeout')
        else:
            self.db.del_contact(selected)
            self.update_clients_list()
            cl_logger.info(f'Успешно удалён контакт {selected}')
            self.messages.information(self, 'contact successfully dleted', 'deleted')
            item.close()
            if selected == self.current_chat: # deactive input, if active user've been deleted
                self.current_chat = None
                self.set_disabled_input()   

    def send_message(self):
        # send message to user
        # import pdb; pdb.set_trace()
        message_text = self.ui.message_text.toPlainText()
        self.ui.message_text.clear()
        # if text field isn't empty, get it, clear field
        if not message_text:
            return
        # L6
        message_text_encrypted = self.encryptor.encrypt(
            message_text.encode('utf-8'))
        message_text_encrypted_base64 = base64.b64encode(
            message_text_encrypted)

        try:
            self.sock.send_message(self.current_chat, message_text_encrypted_base64.decode('ascii'))
            pass
        except ServerError as e:
            self.messages.critical(self, 'server error', e.text)
        except OSError as e:
            if e.errno:
                self.messages.critical(self, 'lost connection', e.text)
                self.close()
            self.messages.critical(self, 'error', 'timeout error')
        except (ConnectionResetError, ConnectionAbortedError):
            self.messages.critical(self, 'lost connection', 'connection timeout')
            self.close()
            # self.message.critical(self, 'error', 'lost connection')
        else:
            self.db.save_message(self.current_chat, 'out', message_text)
            cl_logger.info(f'send message {self.current_chat}: {message_text}')
            self.update_hist_list()

    @pyqtSlot(str)
    def message(self, message):
        # receives new message, byte string
        encrypted_message = base64.b64decode(message[MESSAGE_TEXT])
        try:  # decode message
            decrypted_message = self.decrypter.decrypt(encrypted_message)
        except (ValueError, TypeError) as e:
            self.messages.warning(self, 'error', f'could not decode message {encrypted_message}')
        self.db.save_message(self.current_chat, 'in', decrypted_message.decode('utf-8'))

        sender = message[SENDER]
        if sender == self.current_chat:
            self.update_hist_list()
        else:
            if self.db.is_contact(sender): 
                if self.messages.question(self, 'new_message',  # if got any message, ask if want to begin conversation
                                          f'got new message from {sender}, '
                                          f'do you whant to open chat with {sender}?', QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.current_chat = sender
                    self.set_active_user()
            else:
                print('NO')
                # if contact is new, ask if wnats to add the new contact into the contacts list
                if self.messages.question(self, 'new_message',
                              f'got new message from {sender}, \n '
                              f'the user is not in client list yet. \n'
                              f'do you want to add {sender} and begin to chat with him?',
                              QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes:
                    self.add_contact(sender)
                    self.current_chat = sender
                    self.db.save_message(self.current_chat, 'in', decrypted_message.decode('utf-8'))
                    self.set_active_user()

    @pyqtSlot()
    def connection_lost(self):
        self.messages.warning(self, 'connection fail', 'lost connection')
        self.close()

    def make_connection(self, trans_obj):
        trans_obj.new_message.connect(self.message)
        trans_obj.connection_lost.connect(self.connection_lost)
        trans_obj.message_205.connect(self.signal_205)

    @pyqtSlot()
    def signal_205(self):
        '''renews db by the command from the server'''
        if self.current_chat and not self.db.is_user(self.current_chat):
            self.messages.warning(self, 'sorry', 'user was deleted from chat server')
            self.set_disabled_input()
            self.current_chat = None
        self.update_clients_list()

if __name__ == '__main__':
    import pdb; pdb.set_trace()  # L5
    app = QApplication(sys.argv)
    from client_database import ClientDB
    db = ClientDB('test_main_win')
    from client_thread import ClientThread
    transp = ClientThread(7777, '127.0.0.1', db, 'test_main_win_1')
    window = ClientMainWin(db, transp)
    sys.exit(app.exec_())
