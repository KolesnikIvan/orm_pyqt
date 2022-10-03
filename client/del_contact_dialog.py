# import pdb; pdb.set_trace()  # L5
import sys, os
# import logging

sys.path.append('../')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from logs.config_log_client import cl_logger



class SelectContactToDelDialog(QDialog):
    def __init__(self, database):
        super().__init__()
        self.db = database
        self.setFixedSize(350, 120)
        self.setWindowTitle('Choose a contact to delete')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)
        self.select_label = QLabel('Choose a contact to delete ', self)
        self.select_label.setFixedSize(200, 20)
        self.select_label.move(10, 0)
        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)
        self.selector.addItems(sorted(self.db.get_contacts()))
        self.btn_ok = QPushButton('Delete ', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)
        self.btn_cancel = QPushButton('Cancelation', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)


if __name__ == '__main__':
    import pdb; pdb.set_trace()  # L5
    app = QApplication(sys.argv)
    from client_database import ClientDB
    db = ClientDB('test_del')
    window = SelectContactToDelDialog(db)
    db.add_contact('test_dd')
    db.add_contact('test_ddial')
    print(db.get_contacts())
    window.selector.addItems(sorted(db.get_contacts()))
    window.show()
    app.exec_()
