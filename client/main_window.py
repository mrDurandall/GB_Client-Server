import sys
import os
import configparser

from PyQt5.QtWidgets import QMainWindow, QDialog, qApp, QMessageBox, QApplication, QListView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtCore import pyqtSlot, QEvent, Qt

from client.main_window_conv import Ui_MainWindow
from client.client_DB import ClientDatabase
from common.variables import IN, OUT


class MainWindow(QMainWindow):

    def __init__(self, database):

        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.send_message_button.clicked.connect(self.send_message)
        self.ui.add_contact_button.clicked.connect(self.add_contact)
        self.ui.delete_contact_button.clicked.connect(self.delete_contact)

        self.contacts_model = None
        self.history_model = None

        self.database = database
        self.clients_list_fill()

        self.ui.contacts.doubleClicked.connect(self.select_current_contact)

    def clients_list_fill(self):
        contacts_list = self.database.get_contacts()
        self.contacts_model = QStandardItemModel()
        for contact in contacts_list:
            item = QStandardItem(contact)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.ui.contacts.setModel(self.contacts_model)

    def message_history_fill(self, contact_name):
        print('1')
        print(contact_name)
        contact_messages = self.database.get_messages(contact_name)
        print('2')
        self.history_model = QStandardItemModel()
        print('3')
        self.ui.messages.setModel(self.history_model)
        print('4')
        self.history_model.clear()
        print('5')
        for item in contact_messages:
            if item[2] == IN:
                message = QStandardItem(f'{item[0]}\n{item[3].replace(microsecond=0)}\n{item[1]}')
                message.setEditable(False)
                message.setBackground(QBrush(QColor(0, 153, 153)))
                self.history_model.appendRow(message)
                print('6')
            else:
                message = QStandardItem(f'Вы:\n{item[3].replace(microsecond=0)}\n{item[1]}')
                message.setEditable(False)
                message.setTextAlignment(Qt.AlignRight)
                message.setBackground(QBrush(QColor(255, 170, 00)))
                self.history_model.appendRow(message)
                print('7')

    def select_current_contact(self):
        self.message_history_fill(self.ui.contacts.currentIndex().data())


    def send_message(self):
        pass

    def add_contact(self):
        pass

    def delete_contact(self):
        pass


if __name__ == '__main__':
    main_app = QApplication(sys.argv)
    client_database = ClientDatabase('Petrov')
    client_database.get_contacts()
    main_window = MainWindow(client_database)
    main_window.show()
    main_app.exec()