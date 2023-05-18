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
        self.assertEqual(encodeCredentials('fuck','you'),(usr+b' '+hashgen.digest()))

    def test_encodeMsg(self):
        codedPM=b'!msg-'+'HelloThere'.encode('utf8')+b' -> '+'GeneralKenobi#0212'.encode('utf8')
        self.assertEqual(encodeMsg('HelloThere','GeneralKenobi#0212'),codedPM)

    def test_encodeCreatGrp(self):
        codedPM=b'!create -> '+'212th'.encode('utf8')
        self.assertEqual(encodeCreatGrp('212th'),codedPM)
        

if __name__ == "__main__": 
    unittest.main()