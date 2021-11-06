import socket
import json
import sys
import logging
import time

import logs.server_log_config
import argparse
import select

from common.decorators import log_it

from common.utils import send_message, receive_message

from common.variables import *


log = logging.getLogger('server_log')


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
            socket.inet_aton(namespace.listen_host)
        except socket.error:
            log.critical('Некорректный ip-адрес')
            sys.exit(-1)

    return namespace.port, namespace.listen_host


# @log_it
# def process_message(message):
#     if ACTION in message and\
#             message[ACTION] == PRESENCE and\
#             TIME in message and\
#             USER in message:
#         print(f'{message[TIME]} Получено сообщение о присутствии '
#               f' от пользователя {message[USER][ACCOUNT_NAME]}')
#         return {RESPONSE: '200'}
#     elif ACTION in message and\
#             message[ACTION] == MESSAGE and\
#             TIME in message and\
#             FROM in message and\
#             TO in message and\
#             MESSAGE_TEXT in message:
#         print(f'{message[TIME]} Получено сообщение\n'
#               f'от пользователя {message[FROM]}\n'
#               f'пользователю {message[TO]}\n'
#               f'с текстом {message[MESSAGE_TEXT]}')
#         return {RESPONSE: '200'}
#     return {
#         RESPONSE: '400',
#         ERROR: 'Bad request'
#     }


@log_it
def process_message(message, message_list, client):
    if ACTION in message and\
            message[ACTION] == PRESENCE and\
            TIME in message and\
            USER in message:
        print(f'{message[TIME]} Получено сообщение о присутствии '
              f' от пользователя {message[USER][ACCOUNT_NAME]}')
        send_message(client, {RESPONSE: '200'})
        return
    elif ACTION in message and\
            message[ACTION] == MESSAGE and\
            TIME in message and\
            FROM in message and\
            MESSAGE_TEXT in message:
        print(f'{message[TIME]} Получено сообщение\n'
              f'от пользователя {message[FROM]}\n'
              f'с текстом {message[MESSAGE_TEXT]}')
        message_list.append((message[FROM], message[MESSAGE_TEXT]))
        return
    else:
        send_message(client, {RESPONSE: '400', ERROR: 'Bad request'})
    return


def main():

    listen_port, listen_host = server_args()
    log.info(f'Запущен сервер. Принимаем сообщения от: {listen_host}, порт для подключения: {listen_port}')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((listen_host, listen_port))
    server_socket.settimeout(0.2)

    clients = []
    messages = []

    server_socket.listen(MAX_CONNECTIONS)

    while True:
        try:
            client, address = server_socket.accept()
        except OSError:
            pass
        else:
            log.info(f'Установлено соединение с клиентом по адресу {address}')
            clients.append(client)

        recv_list = []
        send_list = []
        err_list = []

        try:
            if clients:
                recv_list, send_list, err_list = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_list:
            for active_client in recv_list:
                try:
                    process_message(receive_message(active_client),
                                    messages,
                                    active_client)
                except:
                    log.error(f'Клиент {active_client} отключился')
                    clients.remove(active_client)

        if messages and send_list:
            message = {
                ACTION: MESSAGE,
                TIME: time.time(),
                FROM: messages[0][0],
                MESSAGE_TEXT: messages[0][1],
            }
            del messages[0]
            for active_client in send_list:
                try:
                    send_message(active_client, message)
                except:
                    log.error(f'Клиент {active_client} отключился')
                    clients.remove(active_client)


if __name__ == '__main__':
    main()

