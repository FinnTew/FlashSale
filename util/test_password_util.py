import unittest
from util.password_util import PasswordUtil

class TestPasswordUtils(unittest.TestCase):
    def test_hash_password(self):
        password = "my_secure_password"
        hashed_password = PasswordUtil.hash_password(password)
        self.assertNotEqual(password, hashed_password)
        self.assertTrue(PasswordUtil.check_password(password, hashed_password))

    def test_check_password_with_wrong_password(self):
        password = "my_secure_password"
        hashed_password = PasswordUtil.hash_password(password)
        self.assertFalse(PasswordUtil.check_password("wrong_password", hashed_password))

if __name__ == "__main__":
    unittest.main()