from cli import *
import unittest, socket, hashlib

class TestClient(unittest.TestCase):

    def test_setUpSock(self):
        self.assertIsInstance(setUpSock()[0],socket.socket)
        self.assertIsInstance(setUpSock()[1],socket.socket)

    def test_encodeCredentials(self):
        hashgen = hashlib.sha512()
        usr='fuck'.encode('utf8')
        psw='you'.encode('utf8')
        hashgen.update(psw)
        self.assertEqual(encodeCredentials('fuck','you'),(usr,hashgen.digest()))

    def test_encodePM(self):
        codedPM=b'!msg-'+'HelloThere'.encode('utf8')+b' -> '+'GeneralKenobi#0212'.encode('utf8')
        self.assertEqual(encodePM('HelloThere','GeneralKenobi#0212'),codedPM)

        

if __name__ == "__main__": 
    unittest.main()