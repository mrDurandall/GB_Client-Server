import json
import sys

from common.variables import ENCODING, MAX_PACKAGE, DEFAULT_PORT, DEFAULT_HOST

from common.decorators import log_it


@log_it
def send_message(sock, message):

    if isinstance(message, dict):
        json_message = json.dumps(message)
        bytes_message = json_message.encode(ENCODING)
        sock.send(bytes_message)
    else:
        raise ValueError


@log_it
def receive_message(client):

    bytes_response = client.recv(MAX_PACKAGE)
    if isinstance(bytes_response, bytes):
        json_response = bytes_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


# @log_it
# def parameters_check(args):
#
#     try:
#         if '-p' in args:
#             listen_port = int(args[args.index('-p') + 1])
#         else:
#             listen_port = DEFAULT_PORT
#         if listen_port < 1024 or listen_port > 65535:
#             raise ValueError
#     except IndexError:
#         print('Некорректное значение параметра -p')
#         sys.exit(1)
#     except ValueError:
#         print(f'Некорректный номер порта ')
#         sys.exit(1)
#
#     try:
#         if '-a' in args:
#             host_number = args[args.index('-a') + 1]
#         else:
#             host_number = DEFAULT_HOST
#     except IndexError:
#         print('Некорректное значение параметра -a')
#         sys.exit(1)
#
#     return listen_port, host_number
