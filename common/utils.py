import json
import sys

from common.variables import ENCODING, MAX_PACKAGE, DEFAULT_PORT, DEFAULT_HOST


def send_message(sock, message):

    if isinstance(message, dict):
        json_message = json.dumps(message)
        bytes_message = json_message.encode(ENCODING)
        sock.send(bytes_message)
    else:
        raise ValueError


def receive_message(client):

    bytes_response = client.recv(MAX_PACKAGE)
    if isinstance(bytes_response, bytes):
        json_response = bytes_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def parameters_check():

    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        print('Некорректное значение параметра -p')
        sys.exit(1)
    except ValueError:
        print(f'Некорректный номер порта ')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            host_number = sys.argv[sys.argv.index('-a') + 1]
        else:
            host_number = DEFAULT_HOST
    except IndexError:
        print('Некорректное значение параметра -a')
        sys.exit(1)

    return listen_port, host_number
