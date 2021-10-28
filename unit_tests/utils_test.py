import sys
import os
import json
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))

from common.variables import *
from common.utils import send_message, receive_message, parameters_check


class TestSocket:

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.received_message = None

    def send(self, message):
        json_message = json.dumps(self.test_dict)
        self.encoded_message = json_message.encode(ENCODING)
        self.received_message = message

    def recv(self, max_length):
        json_message = json.dumps(self.test_dict)
        return json_message.encode(ENCODING)


class IncorrectTestSocket(TestSocket):

    '''
    Тестовый класс неверного сокета, с функцией recv,
     возвращающий словарь вместо байтовой строки
    '''

    def recv(self, max_length):
        return self.test_dict


class SendMessageTest(unittest.TestCase):

    correct_test_message = {
            ACTION: PRESENCE,
            TIME: 1,
            USER: {
                ACCOUNT_NAME: 'TestUser1'
            }
        }

    def test_correct_message_send(self):
        test_socket = TestSocket(self.correct_test_message)
        send_message(test_socket, self.correct_test_message)
        self.assertEqual(test_socket.received_message, test_socket.encoded_message)

    def test_incorrect_message_send(self):
        test_socket = TestSocket(self.correct_test_message)
        self.assertRaises(ValueError, send_message, test_socket, 'TestString')


class ReceiveMessageTest(unittest.TestCase):

    correct_response = {RESPONSE: '200'}

    incorrect_response = {
        RESPONSE: '400',
        ERROR: 'Bad request'
    }

    def test_receive_correct_message(self):
        test_socket_correct = TestSocket(self.correct_response)
        test_socket_incorrect = TestSocket(self.incorrect_response)
        self.assertEqual(receive_message(test_socket_correct), self.correct_response)
        self.assertEqual(receive_message(test_socket_incorrect), self.incorrect_response)

    def test_receive_incorrect_message(self):
        '''
        Тестируем возникновение исключения,
        в случае, если сокет вернул не байтовую строку
        '''
        test_socket = IncorrectTestSocket(self.incorrect_response)
        self.assertRaises(ValueError, receive_message, test_socket)
