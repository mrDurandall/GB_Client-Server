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

from common.descriptors import CorrectPort


log = logging.getLogger('server_log')


class Server:

    listen_port = CorrectPort()

    def __init__(self, listen_port, listen_host):
        self.port = listen_port
        self.host = listen_host

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(0.2)

        self.clients = []
        self.usernames = dict()
        self.messages = []
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
        if self.is_presence(message):
            if message[USER][ACCOUNT_NAME] not in self.usernames:
                print(f'{message[TIME]} Получено сообщение о присутствии '
                      f' от пользователя {message[USER][ACCOUNT_NAME]}')
                self.usernames[message[USER][ACCOUNT_NAME]] = client
                send_message(client, {RESPONSE: '200'})
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
            self.clients.remove(self.usernames[message[FROM]])
            self.usernames[message[FROM]].close()
            del self.usernames[message[FROM]]
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

    listen_port, listen_host = server_args()
    log.info(f'Запущен сервер. Принимаем сообщения от: {listen_host}, порт для подключения: {listen_port}')

    current_server = Server(listen_port, listen_host)

    current_server.mainloop()


if __name__ == '__main__':
    main()

