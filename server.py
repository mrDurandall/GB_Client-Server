import socket
import json
import sys
import logging
import time

import logs.server_log_config
import argparse
import select
import ipaddress

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
            ipaddress.ip_address(namespace.listen_host)
        except ValueError:
            log.critical('Некорректный ip-адрес')
            sys.exit(-1)

    return namespace.port, namespace.listen_host


@log_it
def process_message(message, message_list, client, usernames, clients):
    if ACTION in message and\
            message[ACTION] == PRESENCE and\
            TIME in message and\
            USER in message:
        if message[USER][ACCOUNT_NAME] not in usernames:
            print(f'{message[TIME]} Получено сообщение о присутствии '
                  f' от пользователя {message[USER][ACCOUNT_NAME]}')
            usernames[message[USER][ACCOUNT_NAME]] = client
            send_message(client, {RESPONSE: '200'})
        else:
            send_message(client, {RESPONSE: '400', ERROR: 'Имя уже занято!'})
            clients.remove(client)
            client.close()
        return
    elif ACTION in message and\
            message[ACTION] == REQUEST_USERS and\
            TIME in message and\
            FROM in message:
        print(f'{message[TIME]} Получен запрос списка пользователей'
              f' от пользователя {message[FROM]}')
        users_list = {
            ACTION: REQUEST_USERS,
            TIME: time.time(),
            MESSAGE_TEXT: f'На сервере: \n {" ".join(list(usernames.keys()))}',
            TO: message[FROM]
        }
        send_message(client, users_list)
        return
    elif ACTION in message and\
            message[ACTION] == MESSAGE and\
            TIME in message and\
            FROM in message and \
            TO in message and \
            MESSAGE_TEXT in message:
        print(f'{message[TIME]} Получено сообщение\n'
              f'от пользователя {message[FROM]}\n'
              f'пользователю {message[TO]}\n'
              f'с текстом {message[MESSAGE_TEXT]}')
        message_list.append(message)
        return
    elif ACTION in message and\
            message[ACTION] == EXIT and\
            TIME in message and\
            FROM in message:
        log.info(f'Пользователь {message[FROM]} отключился от сервера')
        clients.remove(usernames[message[FROM]])
        usernames[message[FROM]].close()
        del usernames[message[FROM]]
    else:
        send_message(client, {RESPONSE: '400', ERROR: 'Bad request'})
    return


@log_it
def send_message_from_server(message, usernames, clients):
    if message[TO] == '':
        message[MESSAGE_TEXT] = f'(Всем) {message[MESSAGE_TEXT]}'
        for client in clients:
            try:
                send_message(client, message)
            except Exception:
                pass
    elif message[TO] in usernames and usernames[message[TO]] in clients:
        send_message(usernames[message[TO]], message)
    else:
        log.info(f'Пользователь с именем {message[TO]} отсутствует на сервере.')


def main():

    listen_port, listen_host = server_args()
    log.info(f'Запущен сервер. Принимаем сообщения от: {listen_host}, порт для подключения: {listen_port}')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((listen_host, listen_port))
    server_socket.settimeout(0.2)

    clients = []
    usernames = dict()
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
                                    active_client,
                                    usernames,
                                    clients)
                except:
                    log.error(f'Клиент {active_client} отключился')
                    clients.remove(active_client)

        for message in messages:
            try:
                send_message_from_server(message, usernames, send_list)
            except Exception:
                log.info(f'Связь с пользователем {message[TO]} прервана')
                clients.remove(usernames[message[TO]])
                del usernames[message[TO]]
        messages.clear()


        # if messages and send_list:
        #     message = {
        #         ACTION: MESSAGE,
        #         TIME: time.time(),
        #         FROM: messages[0][0],
        #         MESSAGE_TEXT: messages[0][1],
        #     }
        #     del messages[0]
        #     for active_client in send_list:
        #         try:
        #             send_message(active_client, message)
        #         except:
        #             log.error(f'Клиент {active_client} отключился')
        #             clients.remove(active_client)


if __name__ == '__main__':
    main()

