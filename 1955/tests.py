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


class TestAddresses(unittest.TestCase):
    def testBase(self):
        self.assertEqual(helpers.parse_addr("<97>Frank (Grace) carp h 70 Woodbole av Mat"), {'owner': True, 'number': 70, 'street':'Woodbole','strsuffix':'Ave', 'nh':'Mattapan'})

    def testNoNumber(self):
        self.assertEqual(helpers.parse_addr("<97>Judith r S Bean ct Rox"), {'owner': False, 'street':'S Bean', 'strsuffix':'Ct', 'nh':'Roxbury'})

    def testNoNHorSuffix(self):
        self.assertEqual(helpers.parse_addr("<97>Lawrence lab r  56  Snowhill"), {'owner':False, 'number':56, 'street':'Snowhill', 'strsuffix':'St', 'nh':'Boston'})

    def testNuminStreetName(self):
        self.assertEqual(helpers.parse_addr("<97>Rosanna F analysis dept First Natl Bank r 707 E 7th SB"), {'owner':False, 'number':707, 'street':'E 7th', 'strsuffix':'St','nh':'South Boston'})

    def testAddrwithRooms(self):
        self.assertEqual(helpers.parse_addr("<97>A Paul lawyer 31 Milk rms 30S-313"), {'number':31, 'street':'Milk', 'strsuffix':'St', 'nh':'Boston'})

    def testBaseDoubleAddr(self):
        self.assertEqual(helpers.parse_addr("<97>A Benj lawyer 11 Beacon  h 1726 Comlth av Br"), {'b_number':11, 'b_street':'Beacon', 'b_strsuffix':'St','b_nh':'Boston', 'owner':True, 'number':1726, 'street':'Commonwealth','strsuffix':'Ave', 'nh':'Brighton'})

    def testDitto(self):
        self.assertEqual(helpers.parse_addr("<97>Wm (Marie A) dept store 352 Hanover h 350 do"), {'b_number':352, 'b_street':'Hanover', 'b_strsuffix':'St', 'b_nh':'Boston', 'owner':True, 'number':350, 'street':'Hanover', 'strsuffix':'St', 'nh':'Boston'})

if __name__ == '__main__':
    unittest.main()
