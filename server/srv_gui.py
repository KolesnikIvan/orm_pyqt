from PyQt5.QtWidgets import (
    QMainWindow, QAction, qApp, QApplication,
    QLineEdit, QFileDialog, QMessageBox, QLabel,
    QTableView, QDialog, QPushButton)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QTimer
from server.win_hist import HistoryWindow
from server.win_config import ConfigWin
from server.win_add_user import RegUser
from server.win_rem_user import DelUserDialog

class MainWindow(QMainWindow):
    '''основное окно'''
    def __init__(self, database, server, config):
        # import pdb; pdb.set_trace()  # L6
        super().__init__()
        self.db = database  # server database
        self.srv_thread = server
        self.config = config

        # exit button
        self.exitAction = QAction('Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.triggered.connect(qApp.quit)
        # refresh button
        self.refresh = QAction('Refresh list', self)
        # config settings
        self.config_btn = QAction('Server settings', self)
        # register user button
        self.register_btn = QAction("reg user")
        # remove user button
        self.remove_btn = QAction("rm user")
        # show history button
        self.show_hist = QAction("Clients' history", self)
        self.statusBar()
        self.statusBar().showMessage("server is working")
        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(self.exitAction)
        self.toolbar.addAction(self.refresh)
        self.toolbar.addAction(self.show_hist)
        self.toolbar.addAction(self.config_btn)
        self.toolbar.addAction(self.register_btn)
        self.toolbar.addAction(self.remove_btn)

        self.setFixedSize(800, 600)
        self.setWindowTitle("Message_Server")

        self.label = QLabel('connected clients', self)
        self.label.setFixedSize(400, 15)
        self.label.move(10, 35)

        self.active_clients = QTableView(self)
        self.active_clients.move(10, 55)
        self.active_clients.setFixedSize(780, 400)

        self.timer = QTimer()  # timer renews clients list
        self.timer.timeout.connect(self.gui_create_table)
        self.timer.start(1000)
        
        self.refresh.triggered.connect(self.gui_create_table)
        self.show_hist.triggered.connect(self.gui_create_hist)
        self.config_btn.triggered.connect(self.srv_config)
        self.register_btn.triggered.connect(self.reg_user)
        self.remove_btn.triggered.connect(self.rm_user)
        self.show()

    def gui_create_table(self):
        '''создание таблицы QModel'''
        # import pdb; pdb.set_trace()  # L4
        list_users = self.db.active_users_list()
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
        # import pdb; pdb.set_trace()
        self.active_clients.setModel(list_table)
        self.active_clients.resizeColumnsToContents()
        self.active_clients.resizeColumnsToContents()
        # return list_table

    def gui_create_hist(self):
        '''создание таблицы истории посещений'''
        # import pdb; pdb.set_trace()  # L4
        global stat_window
        stat_window = HistoryWindow(self.db)
        stat_window.show()

    def srv_config(self):
        '''creates server settings window'''
        global config_window
        config_window = ConfigWin(self.config)

    def reg_user(self):
        '''create registration window'''
        global reg_window
        reg_window = RegUser(self.db, self.srv_thread)
        reg_window.show()

    def rm_user(self):
        '''creates delete user window'''
        global rem_window
        rem_window = DelUserDialog(self.db, self.srv_thread)
        rem_window.show()

# L5
# if __name__ == '__main__':
#     # import pdb; pdb.set_trace()
#     app = QApplication(sys.argv)
#     main = MainWindow()
#     main.statusBar().showMessage('Test statusbar message')
#     test_list = QStandardItemModel(main)
#     test_list.setHorizontalHeaderLabels(['Name', 'IP', 'Port', 'Logget_at'])
#     test_list.appendRow([
#         QStandardItem('tester1'),
#         QStandardItem('192.168.0.1'),
#         QStandardItem('2534'),
#         QStandardItem('13:42:15')
#     ])
#     test_list.appendRow([
#         QStandardItem('tester12'),
#         QStandardItem('192.168.0.4'),
#         QStandardItem('25344'),
#         QStandardItem('18:45:15')
#     ])
#     main.active_clients.setModel(test_list)
#     main.active_clients.resizeColumnsToContents()
#     # app.exec_()

#     # app = QApplication(sys.argv)
#     window = HistoryWindow()
#     hist_list = QStandardItemModel(window)
#     hist_list.setHorizontalHeaderLabels(['Name', 'Last login', 'Sent', 'Got'])
#     hist_list.appendRow([
#         QStandardItem('testirovschik'),
#         QStandardItem('Mon Jan 15 17:23:32'),
#         QStandardItem(23),
#         QStandardItem(45)])
#     window.history_table.setModel(hist_list)
#     window.history_table.resizeColumnsToContents()
#     # app.exec_()
#     # app = QApplication(sys.argv)
#     dialog = ConfigWindow()
#     app.exec_()
