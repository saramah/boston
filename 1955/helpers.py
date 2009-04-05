"""
helpers.py

Helper functions for parse.py and preprocessor.py, 1955.
"""
import re

#copied constants
las = 0 #lastname
fir = 1 #firstname
ini = 2 #initial
spo = 3 #spouse
pro = 4 #profession
mar = 5 #Mrs
wid = 6 #widowed
own = 7 #house ownership status
num = 8 #house number
st = 9 #street name
suf = 10 #street suffix
nei = 11 #neighborhood
bus = 12 #business name

def build_dictionary(path, kv):
    """
    build_dictionary(path, kv)
        -path is path to dictionary we want to parse
        -kv is whether or not the dictionary is key-value pairs

    note: this doesn't cover the case when you have both variable
    length keys and values, only variable length values for kv pairs,
    and variable length keys with no values
    """
    build = {}
    with open(path) as infile:
        for line in infile:
            val = True
            if kv is False:
                key = line.strip().title()
            else:
                line = line.split()
                key = line[0].strip().capitalize()
                if len(line) > 1:
                    val = " ".join(line[1:]).strip()
            if key not in build:
                build[key] = val
    return build

#####build dictionaries
#last names, male/female first names, streets, neighborhoods
#neighborhood abbreviations, name abbreviations
lnames = build_dictionary("../dict/lastnames.txt", False)
fnames = build_dictionary("../dict/firstnames.txt", False)
streets = build_dictionary("../dict/streetnames.txt", False)
nhoods = build_dictionary("../dict/neighborhoods.txt", False)
nameabbr = build_dictionary("../dict/firstabbr.txt", True)
strabbr = build_dictionary("../dict/strabbr.txt", True)
neighabbr = build_dictionary("../dict/neighabbr.txt", True)

def condense_lines(line, linelist):
    """
    Condenses a list of lines into one line. Strips hyphens
    and recondenses words, if split between lines. Otherwise
    simply appends the next line, inserting space.
    """
    try:
        line2 = linelist.pop(0)
        space = " "
        if line.endswith("-"):
            line = line[:len(line)-1]
            space = ""
        line = "%s%s%s" % (line, space, line2)
        condense_lines(line, linelist)
    except IndexError: pass
    return line

def find_errors(line):
    """
    Looks for invalid characters in a line. If it finds one,
    then it returns True; otherwise, it returns False
    """
    invalid = "`~!@#$%^*_=+{}<>?/\|"
    for char in invalid:
        if char in line:
            return True
    return False

def valid_jump(first, second):
    """
    Making sure that we're a) only moving forward in the
    alphabet and b) we're not jumping more than distance one
    at a time. ie, only Button -> Callahan, not Thomas ->
    Abington.

    first and second should be full words or names, not just
    the first letters. We're assuming that they have at least
    two characters.
    """
    if first == "":
        return True
    dist_firstletter = ord(second[0].lower()) - ord(first[0].lower())
    if dist_firstletter < 0 or dist_firstletter > 1:
        return False
    else:
        dist_secondletter = ord(second[1].lower()) - ord(first[1].lower())
        if dist_secondletter < 0:
            return False
        return True


def recognize(bit):
    """
    Recognizes the meaning of the bit passed in and returns
    a tuple; the first bit of the tuple is the key for the
    entry, while the second is the value, and the third is the
    value for last_chomp.
    """
    if bit == "r":
        return ("ownership", "renter", own)
    elif bit == "h":
        return ("ownership", "owner", own)
    elif bit == "b":
        return ("ownership", "owner", own)
    elif bit == "wid":
        return ("widowed", True, wid)
    elif bit == "Mrs":
        return ("married", True, mar)
    elif bit.startswith("(") or bit.endswith(")"):
        bit = bit.strip("()")
        return ("spouse", bit, spo)
    elif bit.isalpha() and len(bit) is 1:
        return ("first", bit, ini)
    elif bit == "II" or bit == "III":
        return ("first", bit, ini)
    elif bit.isdigit():
        return ("number", bit, num)
    elif bit.lower() == "rd":
        bit = "Rd"
        return ("strsuffix", bit, suf)
    elif bit.lower() == "ct":
        bit = "Ct"
        return ("strsuffix", bit, suf)
    elif bit.lower() == "st":
        bit = "St"
        return ("strsuffix", bit, suf)
    elif bit.lower() == "pk":
        bit = "Pk"
        return ("strsuffix", bit, suf)
    elif bit.lower() == "av":
        bit = "Ave"
        return ("strsuffix", bit, suf)
    elif bit.lower() == "pi":
        bit = "Pl"
        return ("strsuffix", bit, suf)
    elif bit.lower() == "sq":
        bit = "Sq"
        return ("strsuffix", bit, suf)
    elif bit.lower() == "ter":
        bit = "Ter"
        return ("strsuffix", bit, suf)
    elif bit.lower() == "dr":
        bit = "Dr"
        return ("strsuffix", bit, suf)
    elif bit.lower() == "la":
        bit = "Ln"
        return ("strsuffix", bit, suf)
    elif bit.capitalize() in neighabbr:
        return ("nh", neighabbr[bit.capitalize()], nei)
    else:
        return None

def num_addresses(line):
    addr_pattern = r"\b\d+\b"
    return re.findall(addr_pattern, line)
