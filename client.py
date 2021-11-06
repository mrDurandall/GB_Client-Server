import socket
import time
import sys
import logging
import argparse
import ipaddress

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
    parser.add_argument('-m',
                        '--mode',
                        default='listen',
                        nargs='?',
                        help='Задает режим клиента.\n'
                             'send для отправки сообщений\n'
                             'listen для получения сообщений')

    namespace = parser.parse_args()

    print(namespace)

    if not 1023 < namespace.port < 65536:
        log.critical('Прослушиваемый порт должен быть в диапазоне от 1025 до 65635')
        sys.exit(-1)

    if namespace.listen_host != '':
        try:
            ipaddress.ip_address(namespace.listen_host)
        except ValueError:
            log.critical('Некорректный ip-адрес')
            sys.exit(-1)

    if namespace.mode not in ('listen', 'send'):
        log.critical('Некорректно указан режим клиента.')
        sys.exit(-1)

    return namespace.port, namespace.host_address, namespace.mode


@log_it
def process_server_response(message):
    if RESPONSE in message:
        if message[RESPONSE] == '200':
            return 'response 200: OK'
        return f'response 400. ERROR - {message[ERROR]}'
    raise ValueError


@log_it
def create_message(account_name='Guest', message_type=PRESENCE, message_text=''):
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
            MESSAGE_TEXT: message_text
        }
        return message
    raise ValueError


def main():
    username = input('Введите ваше имя: ')
    server_port, host_number, mode = client_args()
    log.info(f'Установлено соединение с сервером по адресу {host_number} через порт {server_port}')

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host_number, server_port))
    send_message(client_socket, create_message(account_name=username))
    server_answer = process_server_response(receive_message(client_socket))
    log.info(f'Получен ответ от сервера {server_answer}')

    if mode == 'listen':
        print('Режим работы - получение сообщений')
    else:
        print('Режим работы - отправка сообщений')

    while True:
        if mode == 'send':
            try:
                message_text = input('Введите текст сообщения: ')
                message = create_message(message_type=MESSAGE,
                                         message_text=message_text,
                                         account_name=username)
                log.info(f'сформировано сообщение {message}')
                send_message(client_socket, message)
                log.info(f'Сообщение отправлено серверу')
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                log.error(f'Соединение с сервером {host_number} было потеряно.')
                sys.exit(1)

        if mode == 'listen':
            try:
                answer = receive_message(client_socket)
                log.info(f'От пользователя {answer[FROM]} Получено сообщение {answer[MESSAGE_TEXT]}')
                print(f'{answer[TIME]} {answer[FROM]}: {answer[MESSAGE_TEXT]}')
            except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                log.error(f'Соединение с сервером {host_number} было потеряно.')
                sys.exit(1)


if __name__ == '__main__':
    main()
