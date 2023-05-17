from cli import *
import unittest

class TestClient(unittest.TestCase):

    def test_fuck(self):
        self.assertEqual('shiet','?')

if __name__ == "__main__": 
    unittest.main()