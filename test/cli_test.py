from cli import *
import unittest, socket, hashlib

class TestClient(unittest.TestCase):

    def test_setUpSock(self):
        self.assertIsInstance(setUpSock()[0],socket.socket)
        self.assertIsInstance(setUpSock()[1],socket.socket)

    def test_logIn(self):
        hashgen = hashlib.sha512()
        usr=b'fuck'
        psw=b'you'
        hashgen.update(psw)
        self.assertEqual(logIn(usr,psw),(usr,hashgen.digest()))

if __name__ == "__main__": 
    unittest.main()