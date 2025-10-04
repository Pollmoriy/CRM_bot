import unittest
from database.db import db

class MyTestCase(unittest.TestCase):
    def test_connection(self):
        try:
            db.connect(reuse_if_open=True)
            self.assertTrue(db.is_connection_usable())
        finally:
            db.close()

if __name__ == '__main__':
    unittest.main()
