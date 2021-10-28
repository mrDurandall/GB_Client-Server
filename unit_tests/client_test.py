import sys
import os
import unittest
sys.path.append(os.path.join(os.getcwd(), '..'))

from common.variables import ERROR, RESPONSE, MESSAGE, MESSAGE_TEXT, TIME, PRESENCE, ACTION, USER, ACCOUNT_NAME
from common.variables import FROM, TO

from client import process_server_response, create_message


class TestProcessResponseClass(unittest.TestCase):

    def test_incorrect_response(self):
        self.assertRaises(ValueError, process_server_response, {ERROR: '400'})

    def test_correct_200_response(self):
        self.assertEqual(process_server_response({RESPONSE: '200'}), 'response 200: OK')

    def test_correct_400_response(self):
        self.assertEqual(process_server_response({RESPONSE: '400', ERROR: 'Bad request'}),
                         'response 400. ERROR - Bad request')


class TestCreateMessageClass(unittest.TestCase):

    def test_incorrect_message_type(self):
        self.assertRaises(ValueError, create_message, message_type=MESSAGE_TEXT)

    def test_send_presence(self):
        test_message = create_message(message_type=PRESENCE)
        test_message[TIME] = 1
        self.assertEqual(test_message, {ACTION: PRESENCE, TIME: 1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_send_message(self):
        test_message = create_message(account_name='TestUser1',
                                      message_type=MESSAGE,
                                      to_user='TestUser2',
                                      message_text='TestText')
        test_message[TIME] = 1
        self.assertEqual(test_message, {
            ACTION: MESSAGE,
            TIME: 1,
            FROM: 'TestUser1',
            TO: 'TestUser2',
            MESSAGE_TEXT: 'TestText'
        })


if __name__ == '__main__':
    unittest.main()
