import unittest
import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..'))
print('path', os.getcwd())
from client import process_answer, create_presence
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


class TestClient(unittest.TestCase):
    
    def test_process_correct_answer(self):
        self.assertEqual(process_answer({RESPONSE: 200}), '200 : OK')

    def test_process_wrong_argument(self):
        self.assertRaises(ValueError, process_answer, 'foobar')

    def test_proces_wrong_response(self):
        self.assertEqual(process_answer({'response': 1, 'error':'fail!!!'}), '400 : fail!!!')

    def test_proces_insufficient_key(self):
        self.assertRaises(KeyError, process_answer, ({'response': 1}))

    def test_create_presence(self):
        self.assertEqual(create_presence()[ACTION], PRESENCE)
    
    def test_create_presence_with_custom_account_name(self):
        self.assertEqual(create_presence('Peter')[USER][ACCOUNT_NAME], 'Peter')


if __name__ == '__main__':
    unittest.main()