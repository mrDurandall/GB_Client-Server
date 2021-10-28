import socket
import json
import time
import sys

from common.utils import send_message, receive_message, parameters_check

from common.variables import *


def process_server_response(message):
    if RESPONSE in message:
        if message[RESPONSE] == '200':
            return 'response 200: OK'
        return f'response 400. ERROR - {message[ERROR]}'
    raise ValueError


def create_message(account_name='Guest', message_type=PRESENCE, to_user='', message_text=''):
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


def main():

    server_port, host_number = parameters_check(sys.argv)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host_number, server_port))

    while True:
        message_type = input('Введите тип вообщени\n'
                             'p - сообщение о присутствии\n'
                             'm - текстовое сообщение)\n')
        if message_type == 'p':
            message = create_message()
        elif message_type == 'm':
            to_user = input('Введите имя получателя: ')
            message_text = input('Введите текст сообщения: ')
            message = create_message(message_type=MESSAGE,
                                     message_text=message_text,
                                     to_user=to_user)
        else:
            print('Некорректный тип сообщения!')
            continue
        send_message(client_socket, message)
        try:
            answer = process_server_response(receive_message(client_socket))
            print(answer)
        except (ValueError, json.JSONDecodeError):
            print('Некорректное сообщение сервера')


if __name__ == '__main__':
    main()
