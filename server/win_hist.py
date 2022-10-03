from sqlite3 import Row
from PyQt5.QtWidgets import QDialog, QPushButton, QTableView
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt


class HistoryWindow(QDialog):
    def __init__(self, database):
        super().__init__()
        self.db = database
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Clients' statictisc")
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)
        # exit button
        self.close_btn = QPushButton('Close', self)
        self.close_btn.move(250, 650)
        self.close_btn.clicked.connect(self.close)
        # history list
        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 620)
        self.create_stat_model()

    def create_stat_model(self):
        '''fills stat table with messages history'''
        stat_list = self.db.message_history()
        # data model object
        list = QStandardItemModel()
        list.setHorizontalHeaderLabels(['Name', 'last logged', 'sent messages', 'received_message'])
        for rw in stat_list:
            user, last_seen, sent, recvd = rw
            user = QStandardItem(user)
            user.setEditable(False)
            last_seen = QStandardItem(user)
            last_seen.setEditable(False)
            sent = QStandardItem(str(sent))
            sent.setEditable(False)
            received = QStandardItem(recvd)
            received.setEditable(False)
            list.appendRow([user, last_seen, sent, received])
        self.history_table.setModel(list)
        self.history_table.resizeColumnsToContents()
        self.history_table.resizeRowsToContents()
