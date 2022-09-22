# import pdb; pdb.set_trace()
import sys, os
sys.path.append('../')
from pathlib import Path
sys.path.append(Path(__file__).absolute().parent.parent)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logs.config_log_client import cl_logger
# import logging
from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem


# cl_logger = logging.getLogger('cl_log')
class SelectContactToAddDialog(QDialog):
    def __init__(self, client_socket, database):
        super().__init__()
        self.sock = client_socket #?????????is socket& or what a transport
        self.db = database

        self.setFixedSize(350, 120)
        # self.setFixedSize(500, 300)
        self.setWindowTitle('Select contact to add ')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_lb = QLabel('Select contact to add ', self)
        self.selector_lb.setFixedSize(200, 20)
        self.selector_lb.move(10, 0)
        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)

        self.btn_refresh = QPushButton('Renew list', self)
        self.btn_refresh.setFixedSize(100, 30)
        self.btn_refresh.move(60, 60)

        self.btn_ok = QPushButton('Add', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)

        self.btn_cancel = QPushButton('Cancel', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        self.update_possible_contacts()  # fill possible contacts
        self.btn_refresh.clicked.connect(self.update_familiar_users)

    def update_possible_contacts(self):
        # возможные новые контакты - разница между всеми и уже знакомыми
        self.selector.clear()
        contact_users = set(self.db.get_contacts())
        known_users = set(self.db.get_users())
        known_users.remove(self.sock.user_name)  # L5 delet the client himself
        self.selector.addItems(known_users - contact_users)  # L5 fullfill QComboBox

    def update_familiar_users(self):        
        try:
            self.sock.update_users_list()
        except OSError:
            pass
        else:
            cl_logger.info('users list renewed from server')
            self.update_possible_contacts()


if __name__ == '__main__':
    import pdb; pdb.set_trace()
    app = QApplication(sys.argv)
    from client_database import ClientDB
    db = ClientDB('test_add_dialog')
    from client_thread import ClientThread
    transport = ClientThread(7777, '127.0.0.1', db, 'test_L5')
    window = SelectContactToAddDialog(transport, db)
    window.show()
    app.exec_()
