# import pdb; pdb.set_trace()  # L4
# import json
import sys
# import socket
# import time
from common.utils import get_message, send_message, arg_parser
from common.variables import (
    # DEFAULT_PORT, DEFAULT_SRV_IP,
    ACTION, TIME,
    USER, ACCOUNT_NAME,
    SENDER, PRESENCE,
    RESPONSE, ERROR,
    MESSAGE, MESSAGE_TEXT,
    DESTINATION, EXIT,
    GET_CONTACTS, LIST_INFO, 
    DEL_CONTACT, ADD_CONTACT, 
    USERS_LIST
    )
from logs.config_log_client import cl_logger
from common.decos import Log_class, log_function
from common.errors import IncorrectDataReceived, NonDictInputError, ServerError, MissingReqField
# from threading import Thread, Lock
# from metaclasses import ClientVerifier
from client.client_database import ClientDB
from client.client_thread import ClientThread
from client.main_win import ClientMainWin
from client.start_dialog import SelectUserNameDialog
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    # import pdb; pdb.set_trace()
    srv_address, srv_port, client_name = arg_parser()
    cl_app = QApplication(sys.argv)

    # import pdb; pdb.set_trace()  # L5
    if not client_name:  # L5 протестировать безымянного
        start_dialog = SelectUserNameDialog()
        cl_app.exec_()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
        else:
            exit(0)

    cl_logger.info(f'client {client_name} at {srv_address}:{srv_port} is launched')
    # import pdb; pdb.set_trace()  # L5
    cl_db = ClientDB(client_name)
    try:
        cl_transp = ClientThread(srv_port, srv_address, cl_db, client_name)
    except ServerError as e:
        print(e.text)
        exit(1)
    cl_transp.setDaemon(True)
    cl_transp.start()

    # create GUI
    # import pdb; pdb.set_trace()  # L5
    cl_main_win = ClientMainWin(cl_db, cl_transp)
    cl_main_win.make_connection(cl_transp)
    info_string = f'client{client_name} is laucned'
    cl_main_win.setWindowTitle(info_string)
    cl_logger.info(info_string)
    cl_app.exec_()
    # if gui is closed shut down trasport too
    cl_transp.sock_shutdown()
    cl_transp.join()
