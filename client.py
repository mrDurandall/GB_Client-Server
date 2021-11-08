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


log = logging.getLogger('client_log')


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

    print(namespace)

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


@log_it
def process_server_response(message):
    if RESPONSE in message:
        if message[RESPONSE] == '200':
            return 'response 200: OK'
        return f'response 400. ERROR - {message[ERROR]}'
    raise ValueError


@log_it
def create_message(account_name='Guest', message_type=PRESENCE, message_text='', to_user=''):
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


def check_username(username):
    if not (2 < len(username) < 9):
        print('Некорректная длина имени пользователя!')
    return 2 < len(username) < 9


def interface(client_socket, host_number, username):
    while True:
        try:
            to_user = input('Введите имя получателя (оставьте пустым, чтобы отправить всем): ')
            message_text = input('Введите текст сообщения: ')
            message = create_message(message_type=MESSAGE,
                                     message_text=message_text,
                                     account_name=username,
                                     to_user=to_user)
            log.info(f'сформировано сообщение {message}')
            send_message(client_socket, message)
            log.info(f'Сообщение отправлено серверу')
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
            log.error(f'Соединение с сервером {host_number} было потеряно.')
            sys.exit(1)


def listen_server(client_socket, host_number):
    while True:
        try:
            answer = receive_message(client_socket)
            log.info(f'От пользователя {answer[FROM]} Получено сообщение {answer[MESSAGE_TEXT]}')
            print(f'{time.ctime(answer[TIME])} {answer[FROM]}: {answer[MESSAGE_TEXT]}')
        except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
            log.error(f'Соединение с сервером {host_number} было потеряно.')
            sys.exit(1)


def main():

    server_port, host_number, username = client_args()

    while not check_username(username):
        username = input('Введите ваше имя (от 3 до 8 символов): ')

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host_number, server_port))

    log.info(f'Установлено соединение с сервером по адресу {host_number} через порт {server_port} с именем {username}')

    send_message(client_socket, create_message(account_name=username))
    server_answer = process_server_response(receive_message(client_socket))
    log.info(f'Получен ответ от сервера {server_answer}')

    listen_thread = Thread(target=listen_server, args=(client_socket, host_number))
    listen_thread.daemon = True
    listen_thread.start()

    send_thread = Thread(target=interface, args=(client_socket, host_number, username))
    send_thread.daemon = True
    send_thread.start()

    while True:
        pass


if __name__ == '__main__':
    main()
