from cli import *
import unittest, socket

class TestClient(unittest.TestCase):

    def test_setUpSock(self):
        self.assertIsInstance(setUpSock(),socket.socket.__class__)

if __name__ == "__main__": 
    unittest.main()