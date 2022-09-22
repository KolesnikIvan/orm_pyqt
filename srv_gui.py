import sys
import os
from turtle import window_height
from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    qApp,
    QApplication,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QLabel,
    QTableView,
    QDialog,
    QPushButton)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt


def gui_create_table(db):
    '''создание таблицы QModel'''
    # import pdb; pdb.set_trace()  # L4
    list_users = db.active_users_list()
    list_table = QStandardItemModel()
    list_table.setHorizontalHeaderLabels(['Name', 'IP', 'Port', 'Connected_at'])
    for row in list_users:
        user, ip, port, tm = row
        crr_user = QStandardItem(user)
        crr_ip = QStandardItem(ip)
        crr_port = QStandardItem(port)
        # import pdb; pdb.set_trace()  # test tm.microseconds
        crr_tm = QStandardItem(str(tm.replace(microsecond=0)))
        crr_user.setEditable(False)
        crr_ip.setEditable(False)
        crr_port.setEditable(False)
        crr_tm.setEditable(False)
        list_table.appendRow([crr_user, crr_ip, crr_port, crr_tm])
    return list_table

def gui_create_hist(db):
    '''создание таблицы истории посещений'''
    # import pdb; pdb.set_trace()  # L4
    hist_list = db.message_history()
    hist_table = QStandardItemModel()
    hist_table.setHorizontalHeaderLabels(['Name', 'Last logged_ad', 'Sent messages', 'Got message'])
    for row in hist_list:
        user, last_log, sent, rcvd = row
        crr_user = QStandardItem(user)
        crr_lastlog = QStandardItem(last_log)
        crr_sent = QStandardItem(sent)
        crr_rcvd = QStandardItem(rcvd)
        crr_user.setEditable(False)
        crr_lastlog.setEditable(False)
        crr_sent.setEditable(False)
        crr_rcvd.setEditable(False)
        hist_table.appendRow([crr_user, crr_lastlog, crr_sent, crr_rcvd])
    return hist_table

class MainWindow(QMainWindow):
    '''основное окно'''
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # exit button
        self.exitAction = QAction('Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.triggered.connect(qApp.quit)
        # refresh button
        self.refresh = QAction('Refresh list', self)
        # show history button
        self.show_hist = QAction("Clients' history", self)
        # config settings
        self.config = QAction('Server settings', self)

        self.statusBar()
        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(self.exitAction)
        self.toolbar.addAction(self.refresh)
        self.toolbar.addAction(self.show_hist)
        self.toolbar.addAction(self.config)

        self.setFixedSize(800, 600)
        self.setWindowTitle("Message_Server")

        self.label = QLabel('connected clients', self)
        self.label.setFixedSize(400, 15)
        self.label.move(10, 35)

        self.active_clients = QTableView(self)
        self.active_clients.move(10, 55)
        self.active_clients.setFixedSize(780, 400)

        self.show()


class HistoryWindow(QDialog):
    def __init__(self):
        super().__init__()
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
        self.show()

class  ConfigWindow(QDialog):
    LEN = 100
    HGT = 20
    H1 = 10
    H2 = 200
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Server settings window')
        self.setFixedSize(365, 260)
        
        self.db_path_lb = QLabel('db address')
        self.db_path_lb.move(self.H1, 10)
        self.db_path_lb.setFixedSize(240, 15)
        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(self.LEN, self.HGT)
        self.db_path.move(self.H2, 30)
        self.db_path.setReadOnly(True)
        # select path button
        self.db_select = QPushButton('path to db', self)
        self.db_select.setToolTip('press to change path')
        self.db_select.move(self.H1, 30)

        def open_dialog():
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            path = path.replace('/','\\')
            # import pdb; pdb.set_trace()
            self.db_path.insert(path)

        self.db_select.clicked.connect(open_dialog)

        self.db_label = QLabel('db name', self)
        self.db_label.setFixedSize(180, 15)
        self.db_label.move(self.H1, 68)
        self.db = QLineEdit(self)
        self.db.setFixedSize(self.LEN, self.HGT)
        self.db.move(self.H2, 66)

        self.port_lb = QLabel('port num', self)
        self.port_lb.setFixedSize(180, 15)
        self.port_lb.move(self.H1, 108)
        self.port = QLineEdit(self)
        self.port.setFixedSize(self.LEN, self.HGT)
        self.port.move(self.H2, 108)

        self.ip_lb = QLabel('db ip address', self)
        self.ip_lb.setFixedSize(180, 15)
        self.ip_lb.move(self.H1, 148)
        self.ip_note = QLabel('leave it empty to accept all the connections', self)
        self.ip_note.setFixedSize(500, 30)
        self.ip_note.move(self.H1, 168)
        self.ip = QLineEdit(self)
        self.ip.setFixedSize(self.LEN, self.HGT)
        self.ip.move(self.H2, 148)

        self.save_btn = QPushButton('Save', self)
        self.save_btn.move(self.H1, 220)

        self.close_btn = QPushButton('Close', self)
        self.close_btn.move(self.H2, 220)
        self.close_btn.clicked.connect(self.close)

        self.show()


if __name__ == '__main__':
    # import pdb; pdb.set_trace()
    app = QApplication(sys.argv)
    main = MainWindow()
    main.statusBar().showMessage('Test statusbar message')
    test_list = QStandardItemModel(main)
    test_list.setHorizontalHeaderLabels(['Name', 'IP', 'Port', 'Logget_at'])
    test_list.appendRow([
        QStandardItem('tester1'),
        QStandardItem('192.168.0.1'),
        QStandardItem('2534'),
        QStandardItem('13:42:15')
    ])
    test_list.appendRow([
        QStandardItem('tester12'),
        QStandardItem('192.168.0.4'),
        QStandardItem('25344'),
        QStandardItem('18:45:15')
    ])
    main.active_clients.setModel(test_list)
    main.active_clients.resizeColumnsToContents()
    # app.exec_()

    # app = QApplication(sys.argv)
    window = HistoryWindow()
    hist_list = QStandardItemModel(window)
    hist_list.setHorizontalHeaderLabels(['Name', 'Last login', 'Sent', 'Got'])
    hist_list.appendRow([
        QStandardItem('testirovschik'),
        QStandardItem('Mon Jan 15 17:23:32'),
        QStandardItem(23),
        QStandardItem(45)])
    window.history_table.setModel(hist_list)
    window.history_table.resizeColumnsToContents()
    # app.exec_()
    # app = QApplication(sys.argv)
    dialog = ConfigWindow()
    app.exec_()
