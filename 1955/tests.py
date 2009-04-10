import helpers
import unittest

def dict_diff(have, want):
    result = []
    for key in sorted(want.keys()):
        if not key in have:
            result.append("{%s} want [%s] but MISSING" % (key, want[key]))
        elif want[key] != have[key]:
            result.append("{%s} want [%s] but have [%s]" % (key, want[key], have[key]))
    for key in sorted(have.keys()):
        if not key in want:
            result.append("{%s} have [%s] but DO NOT WANT" % (key, have[key]))
    if not result:
        return None
    else:
        return '; '.join(result)

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

class TestBuildDictionary(unittest.TestCase):
    pass

class TestCondenseLines(unittest.TestCase):
    def testBase(self):
        self.assertEqual(helpers.condense_lines("The", ["whale"]), "The whale")

    def testHyphen(self):
        self.assertEqual(helpers.condense_lines("Win-", ["chester"]), "Winchester")


class TestRecognize(unittest.TestCase):
    def testSuffix(self):
        sufs = {"la":"Ln", "ct":"Ct", "st":"St", "rd":"Rd", "ter":"Ter", "dr":"Dr", "hway":"Hway", "sq":"Sq", "pl":"Pl", "pi":"Pl", "pk":"Pk"}
        for suffix in sufs:
            self.assertEqual(helpers.recognize(suffix), ("strsuffix", sufs[suffix], 10))
    
    def testOwner(self):
        owners = {"h":"owner", "r":"renter", "b":"owner"}
        for atom in owners:
            self.assertEqual(helpers.recognize(atom), ("ownership", owners[atom], 7))

    def testWidowed(self):
        self.assertEqual(helpers.recognize("wid"), ("widowed", True, 6))

    def testMarried(self):
        self.assertEqual(helpers.recognize("Mrs"), ("married", True, 5))

    def testSpouse(self):
        self.assertEqual(helpers.recognize("(Marie)"), ("spouse", "Marie", 3))
        self.assertEqual(helpers.recognize("(Anne S)"), ("spouse", "Anne S", 3))


class TestAddresses(unittest.TestCase):
    def testBase(self):
        self.assertEqual(dict_diff(helpers.parse_addr("\x97Frank (Grace) carp h 70 Woodbole av Mat"), {'owner': True, 'number': '70', 'street':'Woodbole','strsuffix':'Av', 'nh':'Mattapan'}), None)

    def testNoNumber(self):
        self.assertEqual(dict_diff(helpers.parse_addr("\x97Judith r S 8th ct Rox"), {'owner': False, 'street':'S 8th', 'strsuffix':'Ct', 'nh':'Roxbury'}), None)
        self.assertEqual(dict_diff(helpers.parse_addr("\x97Judith r 1F0 Seaver 2F0 S 8th ct Rox"), {'owner': False, 'b_nh': 'Boston', 'street':'S 8th', 'strsuffix':'Ct', 'nh':'Roxbury', 'b_street': 'Seaver', 'b_strsuffix':'St'}), None)

    def testLongStreetName(self):
        self.assertEqual(dict_diff(helpers.parse_addr("\x97Judith r S Blue Hill ct Rox"), {'owner': False, 'street':'S Blue Hill', 'strsuffix':'Ct', 'nh':'Roxbury'}), None)

    def testNoNHorSuffix(self):
        self.assertEqual(dict_diff(helpers.parse_addr("\x97Lawrence lab r  56  Ziegler"), {'owner':False, 'number':'56', 'street':'Ziegler', 'strsuffix':'St', 'nh':'Boston'}), None)

    def testNuminStreetName(self):
        self.assertEqual(dict_diff(helpers.parse_addr("\x97Rosanna F analysis dept First Natl Bank r 707 E 7th SB"), {'owner':False, 'number':'707', 'street':'E 7th', 'strsuffix':'St','nh':'South Boston'}), None)

    def testAddrwithRooms(self):
        self.assertEqual(dict_diff(helpers.parse_addr("\x97A Paul lawyer 31 Milk rms 30S-313"), {'number':'31', 'street':'Milk', 'strsuffix':'St', 'nh':'Boston'}), None)

    def testBaseDoubleAddr(self):
        self.assertEqual(dict_diff(helpers.parse_addr("\x97A Benj lawyer 11 Beacon  h 1726 Comlth av Br"), {'b_number':'11', 'b_street':'Beacon', 'b_strsuffix':'St','b_nh':'Boston', 'owner':True, 'number':'1726', 'street':'Commonwealth','strsuffix':'Av', 'nh':'Brighton'}), None)

    def testDitto(self):
        self.assertEqual(dict_diff(helpers.parse_addr("\x97Wm (Marie A) dept store 352 Hanover Rox h 350 do"), {'b_number':'352', 'b_street':'Hanover', 'b_strsuffix':'St', 'b_nh':'Roxbury', 'owner':True, 'number':'350', 'street':'Hanover', 'strsuffix':'St', 'nh':'Roxbury'}), None)
        self.assertEqual(dict_diff(helpers.parse_addr("\x97Wm (Marie A) dept store h 350 Hanover do"), {'b_number':'350', 'b_street':'Hanover', 'b_strsuffix':'St', 'b_nh':'Boston', 'owner':True, 'number':'350', 'street':'Hanover', 'strsuffix':'St', 'nh':'Boston'}), None)
        self.assertEqual(dict_diff(helpers.parse_addr("\x97Wm (Marie A) dept store h Hanover do"), {'b_street':'Hanover', 'b_strsuffix':'St', 'b_nh':'Boston', 'owner':True, 'street':'Hanover', 'strsuffix':'St', 'nh':'Boston'}), None)
        self.assertEqual(dict_diff(helpers.parse_addr("\x97Wm (Marie A) dept store 173 Blue Hill av Rox h 250 Seaver do"), {'b_number':'173', 'b_street':'Blue Hill', 'b_strsuffix':'Av', 'b_nh':'Roxbury', 'owner':True, 'number':'250', 'street':'Seaver', 'strsuffix':'St', 'nh':'Roxbury'}), None)

    def testInitialEntry(self):
        self.assertEqual(dict_diff(helpers.parse_addr("Coglin Edw J emp United Farmers r 16 White cir st Wakefield"), {'owner':False, 'number':'16', 'street':'White Cir', 'strsuffix':'St', 'nh':'Wakefield'}), None)

    def testWithCompany(self):
        self.assertEqual(dict_diff(helpers.parse_addr("\x97Sidney (Tots N Teens) children's clo r 25 Lucille"), {'owner':False, 'number':'25', 'street':'Lucille', 'strsuffix':'St', 'nh':'Boston'}), None)

    
if __name__ == '__main__':
    unittest.main()
