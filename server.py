import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import socket
import json
from select import select
from threading import Thread, Lock
import configparser

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer, Qt

from common.variables import *
from common.utils import get_message, send_message, arg_parser
from common.decos import log_function, Log_class  # L5
from common.metaclasses import ServerVerifier
from common.descriptors import Port

from logs.config_log_server import srv_logger

from server.core import MessageProcessor
from server.srv_db import ServerStorage
from server.srv_gui import MainWindow


def server_config_load():
    # downloads server configuration from a server.ini file
    # import pdb; pdb.set_trace()  # L5
    config = configparser.ConfigParser()
    config_path = os.path.dirname(os.path.realpath(__file__))
    config.read(os.path.join(config_path, 'server', 'srv.ini'))
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'srv_db.db3')
        return config

def main():
    '''получение хоста и порта из командной строки'''    
    # import pdb; pdb.set_trace()  # L4
    config = server_config_load()

    listen_address, listen_port, _, _, gui_flag = arg_parser(config['SETTINGS']['listen_address'], config['SETTINGS']['default_port'])
    # создание экземпляра сервер
    # database initialize
    db_path = os.path.join(config['SETTINGS']['database_path'],
                            config['SETTINGS']['database_file'])
    db = ServerStorage(db_path)  # database initialize
    # import pdb; pdb.set_trace()  # L4 added path
    server = MessageProcessor(listen_address, listen_port, db)
    server.daemon = True
    # import pdb; pdb.set_trace()  # L4 crete gui
    server.start()  # L3
    
    if gui_flag:
        # create server gui
        server_app = QApplication(sys.argv)
        server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        # import pdb; pdb.set_trace()  # L6
        main_win = MainWindow(db, server, config)
        server_app.exec_()      # launch gui
        server.running = False  # stop server after closing

    else:  # if no gui launch CLI
        while True:
            command = input("Type exit to finish")
            if command == 'exit':
                server.running = False
                server.join()
                break

if __name__ == '__main__':
    # import pdb; pdb.set_trace()  #L4
    main()
