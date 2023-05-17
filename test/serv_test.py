from srv import *
import unittest

class TestServer(unittest.TestCase):
    
    def test_setUpSock(self):
        self.assertEqual(1,2)

if __name__ == "__main__": 
    unittest.main()