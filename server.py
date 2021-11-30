import socket
import json
import sys
import logging
import time
import os
import logs.server_log_config
import argparse
import select
import ipaddress
from threading import Thread, Lock

import configparser

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

from common.decorators import log_it

from common.utils import send_message, receive_message

from common.variables import *

from common.descriptors import CorrectPort

from common.meta import ServerVerifier

from server_DB import ServerDatabase

from server_GUI import *


log = logging.getLogger('server_log')

new_connection = False
conflag_lock = Lock()


class Server(metaclass=ServerVerifier):

    listen_port = CorrectPort()

    def __init__(self, listen_port, listen_host):

        self.database = ServerDatabase()

        self.port = listen_port
        self.host = listen_host

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(0.2)

        self.clients = []
        self.usernames = dict()
        self.messages = []
        print(self.database.session.query(self.database.AllUsers.username).all())
        pass

    def mainloop(self):
        self.socket.listen(MAX_CONNECTIONS)

        while True:
            try:
                client, address = self.socket.accept()
            except OSError:
                pass
            else:
                log.info(f'Установлено соединение с клиентом по адресу {address}')
                self.clients.append(client)

            recv_list = []
            send_list = []
            err_list = []

            try:
                if self.clients:
                    recv_list, send_list, err_list = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if recv_list:
                for active_client in recv_list:
                    try:
                        self.process_message(receive_message(active_client),
                                             active_client)
                    except:
                        log.error(f'Клиент {active_client} отключился')
                        self.clients.remove(active_client)

            for message in self.messages:
                try:
                    self.send_message_from_server(message, send_list)
                except Exception:
                    log.info(f'Связь с пользователем {message[TO]} прервана')
                    self.clients.remove(self.usernames[message[TO]])
                    del self.usernames[message[TO]]
            self.messages.clear()

    @log_it
    def send_message_from_server(self, message, clients):
        if message[TO] == '':
            message[MESSAGE_TEXT] = f'(Всем) {message[MESSAGE_TEXT]}'
            for client in clients:
                try:
                    send_message(client, message)
                except Exception:
                    pass
        elif message[TO] in self.usernames and self.usernames[message[TO]] in clients:
            send_message(self.usernames[message[TO]], message)
        else:
            log.info(f'Пользователь с именем {message[TO]} отсутствует на сервере.')

    @log_it
    def process_message(self, message, client):
        global new_connection
        if self.is_presence(message):
            if message[USER][ACCOUNT_NAME] not in self.usernames:
                print(f'{message[TIME]} Получено сообщение о присутствии '
                      f' от пользователя {message[USER][ACCOUNT_NAME]}')
                self.usernames[message[USER][ACCOUNT_NAME]] = client
                print(message[USER][ACCOUNT_NAME])
                client_ip, client_port = client.getpeername()
                send_message(client, {RESPONSE: '200'})
                self.database.login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                with conflag_lock:
                    new_connection = True
            else:
                send_message(client, {RESPONSE: '400', ERROR: 'Имя уже занято!'})
                self.clients.remove(client)
                client.close()
            return
        elif self.is_request_users(message):
            print(f'{message[TIME]} Получен запрос списка пользователей'
                  f' от пользователя {message[FROM]}')
            users_list = {
                ACTION: REQUEST_USERS,
                TIME: time.time(),
                MESSAGE_TEXT: f'На сервере: \n {" ".join(list(self.usernames.keys()))}',
                TO: message[FROM]
            }
            send_message(client, users_list)
            return
        elif self.is_message(message):
            print(f'{message[TIME]} Получено сообщение\n'
                  f'от пользователя {message[FROM]}\n'
                  f'пользователю {message[TO]}\n'
                  f'с текстом {message[MESSAGE_TEXT]}')
            self.messages.append(message)
            return
        elif self.is_exit(message):
            log.info(f'Пользователь {message[FROM]} отключился от сервера')
            self.database.logout(message[FROM])
            self.clients.remove(self.usernames[message[FROM]])
            self.usernames[message[FROM]].close()
            del self.usernames[message[FROM]]
            with conflag_lock:
                new_connection = True
        else:
            send_message(client, {RESPONSE: '400', ERROR: 'Bad request'})
        return

    @staticmethod
    def is_presence(message):
        return ACTION in message and\
               message[ACTION] == PRESENCE and\
               TIME in message and\
               USER in message

    @staticmethod
    def is_request_users(message):
        return ACTION in message and\
               message[ACTION] == REQUEST_USERS and\
               TIME in message and\
               FROM in message

    @staticmethod
    def is_message(message):
        return ACTION in message and\
               message[ACTION] == MESSAGE and\
               TIME in message and\
               FROM in message and\
               TO in message and\
               MESSAGE_TEXT in message

    @staticmethod
    def is_exit(message):
        return ACTION in message and\
               message[ACTION] == EXIT and\
               TIME in message and\
               FROM in message


@log_it
def server_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('-p',
                        '--port',
                        type=int,
                        default=DEFAULT_PORT,
                        nargs='?',
                        help=f'Задает прослушиваемый порт, если не задан, слушаем порт {DEFAULT_PORT}')
    parser.add_argument('-a',
                        '--listen_host',
                        default='',
                        nargs='?',
                        help='Задает адрес, с которого принимаются подключения.'
                             ' Если не задан - принимать с любых адресов')

    namespace = parser.parse_args()

    if not 1023 < namespace.port < 65536:
        log.critical('Прослушиваемый порт должен быть в диапазоне от 1025 до 65635')
        sys.exit(-1)

    if namespace.listen_host != '':
        try:
            ipaddress.ip_address(namespace.listen_host)
        except ValueError:
            log.critical('Некорректный ip-адрес')
            sys.exit(-1)

    return namespace.port, namespace.listen_host


def main():

    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f'{dir_path}/server.ini')
    # listen_port, listen_host = server_args()
    listen_port, listen_host = int(config['SETTINGS']['port']), config['SETTINGS']['listen_address']
    log.info(f'Запущен сервер. Принимаем сообщения от: {listen_host}, порт для подключения: {listen_port}')

    current_server = Server(listen_port, listen_host)

    server_thread = Thread(target=current_server.mainloop)
    server_thread.name = 'Server Thread'
    server_thread.daemon = True
    server_thread.start()

    server_app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.statusBar().showMessage('Server Working')
    main_window.active_clients_table.setModel(gui_create_model(current_server.database))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()

    def list_update():
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(
                gui_create_model(current_server.database))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    def show_statistics():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(current_server.database))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        stat_window.show()

    def server_config():
        global config_window
        # Создаём окно и заносим в него текущие параметры
        config_window = ConfigWindow()
        config_window.db_path.insert(config['SETTINGS']['Database_path'])
        config_window.db_file.insert(config['SETTINGS']['Database_file'])
        config_window.port.insert(config['SETTINGS']['port'])
        config_window.ip.insert(config['SETTINGS']['Listen_Address'])
        config_window.save_btn.clicked.connect(save_server_config)

    def save_server_config():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['Database_path'] = config_window.db_path.text()
        config['SETTINGS']['Database_file'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            config['SETTINGS']['Listen_Address'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['port'] = str(port)
                print(port)
                with open('server.ini', 'w') as conf:
                    config.write(conf)
                    message.information(
                        config_window, 'OK', 'Настройки успешно сохранены!')
            else:
                message.warning(
                    config_window,
                    'Ошибка',
                    'Порт должен быть от 1024 до 65536')

    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    main_window.refresh_button.triggered.connect(list_update)
    main_window.show_history_button.triggered.connect(show_statistics)
    main_window.config_btn.triggered.connect(server_config)

    server_app.exec_()


if __name__ == '__main__':
    main()

