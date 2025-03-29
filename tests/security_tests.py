import unittest

from flaskr.security import check_password_hash, generate_password


class TestPasswordGeneration(unittest.TestCase):

    def test_generate_valid_length(self):
        hash_value = generate_password("password123")
        self.assertTrue(hash_value is not None, 'Generated password is none')

    def test_generate_too_short(self):
        with self.assertRaises(AttributeError):
            generate_password("pass")

    def test_generate_too_long(self):
        with self.assertRaises(AttributeError):
            generate_password("passwordpassword", 4, 12)

    def test_check_password_hash_matches(self):
        hash_value = generate_password("password123")

        self.assertTrue(check_password_hash(hash_value, "password123"), 'Generated password hashes do not match')
