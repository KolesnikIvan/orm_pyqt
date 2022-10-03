from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
import os


class ConfigWin(QDialog):
    '''class configuration window'''

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_UI()

    def init_UI(self):
        '''womdow settings'''
        self.setFixedSize(365, 260)
        self.setWindowTitle('server settings')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)
        # db_path input field's label 
        self.db_path_label = QLabel('path to the database: ', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)
        # db_path imput field
        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)
        # path selection buttin
        self.db_path_select = QPushButton('Browse...', self)
        self.db_path_select.move(275, 28)
        # db filename label
        self.db_file_label = QLabel('database file name ', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)
        # db filename input text box
        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150, 20)
        # port number label
        self.port_label = QLabel('port number for connections ', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)
        # port input text box
        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)
        # connection address label
        self.ip_label = QLabel('ip to accept connections from', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(180, 15)
        # empty field notation label
        self.ip_label_note = QLabel(
            ' lass this field empty to accept all the connections',
            self)
        self.ip_label_note.move(10, 168)
        self.ip_label_note.setFixedSize(500, 30)
        # ip input text box
        self.ip = QLineEdit(self)
        self.ip.move(200, 148)
        self.ip.setFixedSize(150, 20)
        # save settings button
        self.save_btn = QPushButton('save', self)
        self.save_btn.move(190, 220)
        # close window button
        self.close_button = QPushButton('close', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        self.db_path_select.clicked.connect(self.open_file_dialog)

        self.show()
        # what a settings config???????
        # import pdb; pdb.set_trace()
        self.db_path.insert(self.config['SETTINGS']['database_path'])
        self.db_file.insert(self.config['SETTINGS']['database_file'])
        self.port.insert(self.config['SETTINGS']['default_port'])
        self.ip.insert(self.config['SETTINGS']['listen_address'])
        self.save_btn.clicked.connect(self.save_server_config)

    def open_file_dialog(self):
        '''folder open handler'''
        global dialog
        dialog = QFileDialog(self)
        path = dialog.getExistingDirectory()
        path = path.replace('/', '\\')
        self.db_path.clear()
        self.db_path.insert(path)

    def save_server_config(self):
        '''
        checks settings are correct and saves them into an ini-file
        '''
        global config_window
        message = QMessageBox()
        self.config['SETTINGS']['database_path'] = self.db_path.text()
        self.config['SETTINGS']['database_file'] = self.db_file.text()
        try:
            port = int(self.port.text())
        except ValueError:
            message.warning(self, 'Error', 'Port num must be a number')
        else:
            self.config['SETTINGS']['listen_address'] = self.ip.text()
            if 1023 < port < 65536:
                self.config['SETTINGS']['default_port'] = str(port)
                dir_path = os.path.dirname(os.path.realpath(__file__))
                dir_path = os.path.join(dir_path, '..')
                with open(f"{dir_path}/{'server_dist+++.ini'}", 'w') as conf:
                    self.config.write(conf)
                    message.information(
                        self, 'Ok', 'settings are saved')
            else:
                message.warning(
                    self, 'Error', 'port number must be in range 1024..65536')


# class  ConfigWindow(QDialog):
#     LEN = 100
#     HGT = 20
#     H1 = 10
#     H2 = 200
#     def __init__(self):
#         super().__init__()
#         self.initUI()

#     def initUI(self):
#         self.setWindowTitle('Server settings window')
#         self.setFixedSize(365, 260)
        
#         self.db_path_lb = QLabel('db address')
#         self.db_path_lb.move(self.H1, 10)
#         self.db_path_lb.setFixedSize(240, 15)
#         self.db_path = QLineEdit(self)
#         self.db_path.setFixedSize(self.LEN, self.HGT)
#         self.db_path.move(self.H2, 30)
#         self.db_path.setReadOnly(True)
#         # select path button
#         self.db_select = QPushButton('path to db', self)
#         self.db_select.setToolTip('press to change path')
#         self.db_select.move(self.H1, 30)

#         def open_dialog():
#             global dialog
#             dialog = QFileDialog(self)
#             path = dialog.getExistingDirectory()
#             path = path.replace('/','\\')
#             # import pdb; pdb.set_trace()
#             self.db_path.insert(path)

#         self.db_select.clicked.connect(open_dialog)

#         self.db_label = QLabel('db name', self)
#         self.db_label.setFixedSize(180, 15)
#         self.db_label.move(self.H1, 68)
#         self.db = QLineEdit(self)
#         self.db.setFixedSize(self.LEN, self.HGT)
#         self.db.move(self.H2, 66)

#         self.port_lb = QLabel('port num', self)
#         self.port_lb.setFixedSize(180, 15)
#         self.port_lb.move(self.H1, 108)
#         self.port = QLineEdit(self)
#         self.port.setFixedSize(self.LEN, self.HGT)
#         self.port.move(self.H2, 108)

#         self.ip_lb = QLabel('db ip address', self)
#         self.ip_lb.setFixedSize(180, 15)
#         self.ip_lb.move(self.H1, 148)
#         self.ip_note = QLabel('leave it empty to accept all the connections', self)
#         self.ip_note.setFixedSize(500, 30)
#         self.ip_note.move(self.H1, 168)
#         self.ip = QLineEdit(self)
#         self.ip.setFixedSize(self.LEN, self.HGT)
#         self.ip.move(self.H2, 148)

#         self.save_btn = QPushButton('Save', self)
#         self.save_btn.move(self.H1, 220)

#         self.close_btn = QPushButton('Close', self)
#         self.close_btn.move(self.H2, 220)
#         self.close_btn.clicked.connect(self.close)

#         self.show()
