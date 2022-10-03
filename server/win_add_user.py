from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel, QMessageBox
import binascii
import hashlib


class RegUser(QDialog):
    """ class dialog to register user on server """
    def __init__(self, database, server):
        super().__init__()
        self.db = database
        self.srv = server
        self.setWindowTitle('Registration')
        self.setFixedSize(175, 183)
        self.setModal(True)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.label_username = QLabel('Insert user name: ', self)
        self.label_username.move(10, 10)
        self.label_username.setFixedSize(150, 15)

        self.client_name = QLineEdit(self)
        self.client_name.setFixedSize(154, 20)
        self.client_name.move(10, 30)

        self.label_passwd = QLabel('Type Pass:', self)
        self.label_passwd.move(10, 55)
        self.label_passwd.setFixedSize(150, 15)

        self.client_passwd = QLineEdit(self)
        self.client_passwd.setFixedSize(154, 20)
        self.client_passwd.move(10, 75)
        self.client_passwd.setEchoMode(QLineEdit.Password)
        self.label_conf = QLabel('Confirm pass:', self)
        self.label_conf.move(10, 100)
        self.label_conf.setFixedSize(150, 15)

        self.client_conf = QLineEdit(self)
        self.client_conf.setFixedSize(154, 20)
        self.client_conf.move(10, 120)
        self.client_conf.setEchoMode(QLineEdit.Password)
        self.btn_ok = QPushButton('Save', self)
        self.btn_ok.move(10, 150)
        self.btn_ok.clicked.connect(self.save_data)

        self.btn_cancel = QPushButton('Exit', self)
        self.btn_cancel.move(90, 150)
        self.btn_cancel.clicked.connect(self.close)

        self.msg_box = QMessageBox()

        self.show()

    def save_data(self):
        """
        test user input is correct and saves him into data base
        """
        # import pdb; pdb.set_trace()
        if not self.client_name.text():
            self.msg_box.critical(
                self, 'Error', 'User name is absent')
            return
        elif self.client_passwd.text() != self.client_conf.text():
            self.msg_box.critical(
                self, 'Error', 'Entered pwds are different')
            return
        #FUNC NAME IN DB
        elif self.db.user_is_in_base(self.client_name.text()):
            self.msg_box.critical(
                self, 'Error', 'User already exists')
            return
        else:
            # gen hash, use lower pass as a salt
            passwd_bytes = self.client_passwd.text().encode('utf-8')
            salt = self.client_name.text().lower().encode('utf-8')
            passwd_hash = hashlib.pbkdf2_hmac(
                'sha512', passwd_bytes, salt, 10000)
            self.db.add_user(
                self.client_name.text(),
                binascii.hexlify(passwd_hash))
            # import pdb; pdb.set_trace()
            self.msg_box.information(
                self, 'Ok', 'User successfully registered')
            # noting clients to renew user lists
            self.srv.service_update_lists()
            self.close()


if __name__ == '__main__':
    import pdb; pdb.set_trace()
    app = QApplication([])
    from srv_db import ServerStorage
    database = ServerStorage('server\srv_db.db3')
    import os
    import sys
    pth = os.path.join(os.getcwd(), '..')
    sys.path.insert(0, pth)
    from core import MessageProcessor
    server = MessageProcessor('127.0.0.1', 7777, database)
    dial = RegUser(database, server)
    app.exec_()
