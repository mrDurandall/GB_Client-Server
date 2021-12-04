import sys
import os
import configparser

from PyQt5.QtWidgets import QMainWindow, QDialog, qApp, QMessageBox, QApplication, QListView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtCore import pyqtSlot, QEvent, Qt

sys.path.append('../')
from client.connect_conv import Ui_Dialog
from common.utils import ip_check, port_check


class ConnectWindow(QDialog):
    def __init__(self):

        self.ok_pressed = False

        self.config = configparser.ConfigParser()
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.config.read(f'{self.dir_path}/client.ini')

        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.username_input.setText(self.config['SETTINGS']['username'])
        self.ui.IP_input.setText(self.config['SETTINGS']['server_IP'])
        self.ui.port_input.setText(self.config['SETTINGS']['port'])

        self.ui.exit_button.clicked.connect(qApp.exit)
        self.ui.connect_button.clicked.connect(self.connect)

    def connect(self):
        if not ip_check(self.ui.IP_input.text()):
            self.ui.error_lable.setText('Некорректный IP адрес!')
        elif not port_check(int(self.ui.port_input.text())):
            self.ui.error_lable.setText('Некорректный номер порта!')
        elif len(self.ui.username_input.text()) < 3:
            self.ui.error_lable.setText('Слишком короткое имя!')
        else:
            self.config['SETTINGS']['DB_name'] = f'client_{self.ui.username_input.text()}.db3'
            self.config['SETTINGS']['username'] = self.ui.username_input.text()
            self.config['SETTINGS']['port'] = self.ui.port_input.text()
            self.config['SETTINGS']['server_IP'] = self.ui.IP_input.text()
            with open(f'{self.dir_path}/client.ini', 'w') as conf:
                self.config.write(conf)
            self.ok_pressed = True
            qApp.exit()


if __name__ == '__main__':
    connect_app = QApplication(sys.argv)
    connect_window = ConnectWindow()
    connect_window.show()
    connect_app.exec()
    print('1')
