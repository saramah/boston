import helpers
import unittest

class TestValidJump(unittest.TestCase):
    def testSanityTrue(self):
        """names should always move forward in alphabet"""
        self.assertTrue(helpers.valid_jump("John", "John"))
        self.assertTrue(helpers.valid_jump("John", "Joan"))
        self.assertTrue(helpers.valid_jump("Joan", "Kyle"))

    def testSanityFalse(self):
        """if names move backwards, we should complain"""
        self.assertFalse(helpers.valid_jump("Kyle", "Joan"))

class TestFindErrors(unittest.TestCase):
    def testValid(self):
        self.assertFalse(helpers.find_errors("No problems."))

    def testInvalid(self):
        self.assertTrue(helpers.find_errors("$o many pro3$#blems"))

if __name__ == '__main__':
    unittest.main()
