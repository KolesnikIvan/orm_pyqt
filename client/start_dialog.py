from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel , qApp
from PyQt5.QtCore import QEvent

# start dialog with user name selection
class SelectUserNameDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ok_pressed = False
        self.setWindowTitle('Hello world!')
        self.setFixedSize(175, 100)
        self.label = QLabel('Insert user name:', self)
        self.label.move(10, 5)
        self.label.setFixedSize(150, 25)
        self.client_name = QLineEdit(self)
        self.client_name.setFixedSize(150, 20)
        self.client_name.move(10, 30)
        self.btn_ok = QPushButton('Begin', self)
        self.btn_ok.setFixedSize(70, 30)
        self.btn_ok.move(10, 60)
        self.btn_ok.clicked.connect(self.click)
        self.btn_cancel = QPushButton('Cancel', self)
        self.btn_cancel.setFixedSize(70, 30)
        self.btn_cancel.move(90, 60)
        self.btn_cancel.clicked.connect(qApp.exit)
        self.show()

    def click(self):
        # if user_name filed isn't empty, close the application
        if self.client_name.text():
            self.ok_pressed = True
            qApp.exit()


if __name__ == '__main__':
    # import pdb; pdb.set_trace()  # L5
    app = QApplication([])
    the_dialog = SelectUserNameDialog()
    app.exec_()
