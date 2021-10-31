import socket
import json
import sys
import logging
import logs.server_log_config

from common.decorators import log_it

from common.utils import send_message, receive_message, parameters_check

from common.variables import *


log = logging.getLogger('server_log')


@log_it
def process_message(message):
    if ACTION in message and\
            message[ACTION] == PRESENCE and\
            TIME in message and\
            USER in message:
        print(f'{message[TIME]} Получено сообщение о присутствии '
              f' от пользователя {message[USER][ACCOUNT_NAME]}')
        return {RESPONSE: '200'}
    elif ACTION in message and\
            message[ACTION] == MESSAGE and\
            TIME in message and\
            FROM in message and\
            TO in message and\
            MESSAGE_TEXT in message:
        print(f'{message[TIME]} Получено сообщение\n'
              f'от пользователя {message[FROM]}\n'
              f'пользователю {message[TO]}\n'
              f'с текстом {message[MESSAGE_TEXT]}')
        return {RESPONSE: '200'}
    return {
        RESPONSE: '400',
        ERROR: 'Bad request'
    }


def main():

    listen_port, host_number = parameters_check(sys.argv)
    log.info(f'Запущен сервер. Адрес {host_number}, порт для подключения {listen_port}')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host_number, listen_port))
    server_socket.listen(MAX_CONNECTIONS)

    while True:
        client, address = server_socket.accept()
        log.info(f'Установлено соединение с клиентом по адресу {address}')
        try:
            message = receive_message(client)
            log.info(f'Получено сообщение {message}')
            server_response = process_message(message)
            log.info(f'сформирован ответ {server_response}')
            send_message(client, server_response)
            client.close()
            log.info('Соединение закрыто')
        except (ValueError, json.JSONDecodeError):
            log.error('Принято некорректное сообщение!')
            client.close()


if __name__ == '__main__':
    main()

