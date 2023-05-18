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

    def test_encodeGrpMsg(self):
        codedMSG=b'!msg-'+'Execute Order 66'.encode('utf8')+b' -> '+'212th'.encode('utf8')
        self.assertEqual(encodeGrpMsg('Execute Order 66','212th'),codedMSG)
        

if __name__ == "__main__": 
    unittest.main()