import socket
import json

from common.utils import send_message, receive_message, parameters_check

from common.variables import *


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

    listen_port, host_number = parameters_check()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host_number, listen_port))
    server_socket.listen(MAX_CONNECTIONS)

    while True:
        client, address = server_socket.accept()
        try:
            message = receive_message(client)
            server_response = process_message(message)
            send_message(client, server_response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            print('Принято некорреткное сообщение!')
            client.close()


if __name__ == '__main__':
    main()
