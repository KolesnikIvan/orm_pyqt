import unittest
import time
import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
from server import process_client_message
from common.variables import (
    MAX_CONNECTIONS,
    ACTION,
    ACCOUNT_NAME,
    PRESENCE,
    TIME,
    USER,
    RESPONSE,
    ERROR,
    DEFAULT_PORT,
    )


class TestServer(unittest.TestCase):
    
    def test_process_correct_client_message(self):
        self.assertEqual(process_client_message({'action': 'presence', 'user':{'account_name':"Guest"}, 'time': 222}), {RESPONSE: 200})

    def test_process_incmplete_message(self):
        self.assertEqual(process_client_message({'action': 'presence', 'user':{'account_name':"Guest"}}), {RESPONSE: 400, ERROR: 'Bad Request'})

    def test_process_wrong_answer(self):
        self.assertEqual(process_client_message({'action': 'presence', 'user':{'account_name':"Admin"}, 'time': 222}), {RESPONSE: 400, ERROR: 'Bad Request'})

    def test_process_abscence(self):
        self.assertNotEqual(process_client_message({'action': 'abscence', 'user':{'account_name':"Guest"}, 'time': 222}), {RESPONSE: 200})

    def test_process_message_time(self):
        time_now = time.time()
        self.assertEqual(process_client_message({'action': 'presence', 'user':{'account_name':"Guest"}, 'time': time_now}), {RESPONSE: 200})


if __name__ == '__main__':
    unittest.main()