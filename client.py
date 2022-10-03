# import pdb; pdb.set_trace()  # L4
# import json
import sys
import os
from Cryptodome.PublicKey import RSA
# import socket
# import time
# from threading import Thread, Lock

from PyQt5.QtWidgets import QApplication, QMessageBox

# from metaclasses import ClientVerifier
from logs.config_log_client import cl_logger
from client.client_database import ClientDB
from client.client_thread import ClientThread
from client.main_win import ClientMainWin
from client.start_dialog import SelectUserNameDialog
from common.utils import get_message, send_message, arg_parser
from common.variables import *
from common.decos import Log_class, log_function
from common.errors import ServerError, IncorrectDataReceived, NonDictInputError, MissingReqField

if __name__ == '__main__':
    # import pdb; pdb.set_trace()
    srv_address, srv_port, client_name, client_pwd, _ = arg_parser()
    cl_logger.info('Args loaded')
    cl_app = QApplication(sys.argv)

    # import pdb; pdb.set_trace()  # L5
    start_dialog = SelectUserNameDialog()
    if not client_name or not client_pwd:  # L5 протестировать безымянного
        cl_app.exec_()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            client_pwd = start_dialog.client_name.text()
            cl_logger.info(f'got name {client_name} and pass {client_pwd}')
            # del start_dialog
        else:
            exit(0)

    cl_logger.info(f'client {client_name} at {srv_address}:{srv_port} is launched')
    # load or generate keys if there's no 
    # pth = os.path.dirname(os.path.realpath(__file__))
    pth = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'client')
    key_file = os.path.join(pth, f'{client_name}.key')
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())

    # import pdb; pdb.set_trace()  # L5
    cl_db = ClientDB(client_name)
    try:
        cl_transp = ClientThread(
            srv_port, 
            srv_address, 
            cl_db, 
            client_name,
            client_pwd,
            keys)
        cl_logger.info('transpot socket is ready')
    except ServerError as e:
        message = QMessageBox()
        message.critical(start_dialog, 'server error', e.text)
        print(e.text)
        sys.exit(1)
    cl_transp.setDaemon(True)
    cl_transp.start()
    del start_dialog
    # create GUI
    # import pdb; pdb.set_trace()  # L5
    cl_main_win = ClientMainWin(cl_db, cl_transp, keys)
    cl_main_win.make_connection(cl_transp)
    info_string = f'client{client_name} is launched'
    cl_main_win.setWindowTitle(info_string)
    cl_logger.info(info_string)
    cl_app.exec_()
    # if gui is closed shut down trasport too
    cl_transp.sock_shutdown()
    cl_transp.join()
