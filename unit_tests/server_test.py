import sys
import os
import unittest
sys.path.append(os.path.join(os.getcwd(), '..'))

from common.variables import *

from server import process_message


class TestProcessMessageClass(unittest.TestCase):

    correct_response = {RESPONSE: '200'}
    incorrect_response = {RESPONSE: '400', ERROR: 'Bad request'}

    def test_correct_presence_message(self):
        self.assertEqual(process_message({ACTION: PRESENCE,
                                          TIME: 1,
                                          USER: {ACCOUNT_NAME: 'TestUser'}
                                          }),
                         self.correct_response)

    def test_correct_message(self):
        self.assertEqual(process_message({ACTION: MESSAGE,
                                          TIME: 1,
                                          FROM: 'TestUser1',
                                          TO: 'TestUser2',
                                          MESSAGE_TEXT: 'TestText'}),
                         self.correct_response)

    def test_incorrect_action(self):
        self.assertEqual(
            process_message({ACTION: MESSAGE_TEXT,
                             TIME: 1,
                             FROM: 'TestUser1',
                             TO: 'TestUser2',
                             MESSAGE_TEXT: 'TestText'}),
            self.incorrect_response
        )

    def test_no_action(self):
        self.assertEqual(
            process_message({TIME: 1,
                             FROM: 'TestUser1',
                             TO: 'TestUser2',
                             MESSAGE_TEXT: 'TestText'}),
            self.incorrect_response
        )

    def test_no_time(self):
        self.assertEqual(
            process_message({ACTION: MESSAGE,
                             FROM: 'TestUser1',
                             TO: 'TestUser2',
                             MESSAGE_TEXT: 'TestText'}),
            self.incorrect_response
        )

#     Аналогичным образом можно проверить поведение функции при отсуствии каждого элемента сообщения


if __name__ == '__main__':
    unittest.main()
