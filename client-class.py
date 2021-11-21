import json
import socket
import time
import sys
import logging
import argparse
import ipaddress
from threading import Thread

import logs.client_log_config

from common.utils import send_message, receive_message
from common.variables import *
from common.decorators import log_it
from common.descriptors import CorrectPort


log = logging.getLogger('client_log')


class Client:

    server_port = CorrectPort()

    def __init__(self, server_port, host_number, username):

        # Аргументы клиента
        self.server_port = server_port
        self.host_number = host_number
        self.username = username

        while not self.check_username():
            self.username = input('Введите ваше имя (от 3 до 8 символов): ')

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def check_username(self):
        if not (2 < len(self.username) < 9):
            print('Некорректная длина имени пользователя!')
        return 2 < len(self.username) < 9

    @log_it
    def create_message(self, account_name='Guest', message_type=PRESENCE, message_text='', to_user=''):
        if message_type == PRESENCE:
            message = {
                ACTION: message_type,
                TIME: time.time(),
                USER: {
                    ACCOUNT_NAME: account_name
                }
            }
            return message
        elif message_type == MESSAGE:
            message = {
                ACTION: message_type,
                TIME: time.time(),
                FROM: account_name,
                TO: to_user,
                MESSAGE_TEXT: message_text
            }
            return message
        raise ValueError

    @log_it
    def process_server_response(self, message):
        if RESPONSE in message:
            if message[RESPONSE] == '200':
                return 'response 200: OK'
            return f'response 400. ERROR - {message[ERROR]}'
        raise ValueError

    def print_help(self):
        print('Список действий:\n'
              'message - отправить сообщение\n'
              'users - получить список пользователей онлайн\n'
              'help - получить список действий\n'
              'exit - отключиться от сервера и выйти\n')

    def request_users(self):
        message = {
            ACTION: REQUEST_USERS,
            FROM: self.username,
            TIME: time.time()
        }
        return message

    def send_exit(self):
        message = {
            ACTION: EXIT,
            FROM: self.username,
            TIME: time.time()
        }
        return message

    def interface(self):
        while True:
            try:
                action = input(f'{self.username}, Выберите действие (help): ')
                if action == 'message':
                    to_user = input('Введите имя получателя (оставьте пустым, чтобы отправить всем): ')
                    message_text = input('Введите текст сообщения: ')
                    message = self.create_message(message_type=MESSAGE,
                                                  message_text=message_text,
                                                  account_name=self.username,
                                                  to_user=to_user)
                    log.info(f'сформировано сообщение {message}')
                    send_message(self.socket, message)
                    log.info(f'Сообщение отправлено серверу')
                elif action == 'help':
                    self.print_help()
                elif action == 'users':
                    send_message(self.socket, self.request_users())
                elif action == 'exit':
                    send_message(self.socket, self.send_exit())
                    time.sleep(0.5)
                    break
                else:
                    print('Некорректное действие. Для получения списка действий введите help')
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                log.error(f'Соединение с сервером {self.host_number} было потеряно.')
                sys.exit(1)

    def listen_server(self):
        while True:
            try:
                answer = receive_message(self.socket)
                if ACTION in answer.keys() and answer[ACTION] == REQUEST_USERS:
                    print(f'{answer[MESSAGE_TEXT]}')
                else:
                    log.info(f'От пользователя {answer[FROM]} Получено сообщение {answer[MESSAGE_TEXT]}')
                    print(f'{time.ctime(answer[TIME])} {answer[FROM]}: {answer[MESSAGE_TEXT]}')
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError,
                    json.JSONDecodeError):
                log.error(f'Соединение с сервером {self.host_number} было потеряно.')
                break

    def mainloop(self):
        self.socket.connect((self.host_number, self.server_port))
        log.info(
            f'Установлено соединение с сервером по адресу {self.host_number} через порт {self.server_port}'
            f' с именем {self.username}')

        send_message(self.socket, self.create_message(account_name=self.username))

        server_answer = self.process_server_response(receive_message(self.socket))
        log.info(f'Получен ответ от сервера {server_answer}')

        listen_thread = Thread(target=self.listen_server)
        listen_thread.name = 'Listen Thread'
        listen_thread.daemon = True
        listen_thread.start()

        send_thread = Thread(target=self.interface)
        send_thread.name = 'Sending Thread'
        send_thread.daemon = True
        send_thread.start()

        self.print_help()

        while True:
            if not listen_thread.is_alive() or not send_thread.is_alive():
                break


@log_it
def client_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('-p',
                        '--port',
                        type=int,
                        default=DEFAULT_PORT,
                        nargs='?',
                        help=f'Задает порт для подключения на сервере,'
                             f' если не задан, соединяемся с портом {DEFAULT_PORT}')
    parser.add_argument('-a',
                        '--host_address',
                        default=DEFAULT_HOST,
                        nargs='?',
                        help=f'Задает адрес сервера.'
                             f' Если не задан связываемся с {DEFAULT_HOST}')
    parser.add_argument('-n',
                        '--name',
                        default='',
                        nargs='?',
                        help='Имя пользователя'
                             'от 3 до 8 символов'
                        )

    namespace = parser.parse_args()

    if not 1023 < namespace.port < 65536:
        log.critical('Прослушиваемый порт должен быть в диапазоне от 1025 до 65635')
        sys.exit(-1)

    if namespace.host_address != '':
        try:
            ipaddress.ip_address(namespace.host_address)
        except ValueError:
            log.critical('Некорректный ip-адрес')
            sys.exit(-1)

    return namespace.port, namespace.host_address, namespace.name


def main():

    server_port, host_number, username = client_args()

    current_client = Client(server_port, host_number, username)

    current_client.mainloop()


if __name__ == '__main__':
    main()
