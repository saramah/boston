from __future__ import with_statement
"""
helpers.py

Helper functions for parse.py and preprocessor.py, 1955.
"""
import re

#copied constants
LAST_NAME = 0
FIRST_NAME = 1
INITIAL = 2
SPOUSE = 3
PROFESSION = 4
MRS = 5
WIDOWED = 6
OWNER = 7
HOUSE_NUM = 8
STREET = 9
STREET_SUFFIX = 10
NH = 11
BUSINESS_NAME = 12

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
            if not kv:
                key = line.strip().lower()
            else:
                line = line.split()
                key = line[0].strip().lower()
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
nhabbr = build_dictionary("../dict/neighabbr.txt", True)
suffixes = ['st', 'pk', 'rd', 'ct', 'av', 'la', 'dr', 'ter','pl','pi','hway']
 
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


def recognize(atom):
    """
    Recognizes the meaning of the atom passed in and returns
    a tuple; the first bit of the tuple is the key for the
    entry, while the second is the value, and the third is the
    value for last_chomp.
    """
    atom = atom.lower()
    if atom == "r":
        return ("ownership", "renter", OWNER)
    elif atom == "h":
        return ("ownership", "owner", OWNER)
    elif atom == "b":
        return ("ownership", "owner", OWNER)
    elif atom == "wid":
        return ("widowed", True, WIDOWED)
    elif atom == "mrs":
        return ("married", True, MRS)
    elif atom.startswith("(") or atom.endswith(")"):
        atom = atom.strip("()")
        return ("spouse", atom.title(), SPOUSE)
    elif atom.isalpha() and len(atom) == 1:
        return ("first", atom.capitalize(), INITIAL)
    elif atom == "II" or atom == "III":
        return ("first", atom.capitalize(), INITIAL)
    elif atom =="jr":
        return ("first", atom.capitalize(), INITIAL)
    elif atom.isdigit():
        return ("number", bit, HOUSE_NUM)
    elif atom in ('rd', 'ct', 'st', 'pk', 'av', 'ave', 'pl', 'pi', 'sq',
                  'ter', 'dr', 'la', 'ln', 'hway'):
        remap = {'av': 'Ave', 'la': 'Ln', 'pi': 'Pl'}
        if atom in remap:
            atom = remap[atom]
        else:
            atom = atom.capitalize()
        return ("strsuffix", atom, STREET_SUFFIX)
    elif atom in nhabbr:
        return ("nh", nhabbr[atom], NH)
    else:
        return None

def parse_addr(line):
    if not line.startswith('\x97'):
        return None
    words = map(str.lower, line.split())
    pos = len(words) - 1
    prefix = ''
    repeat_street = False
    result = {'strsuffix': 'St', 'nh': 'Boston',
              'b_strsuffix': 'St', 'b_nh': 'Boston'}

    # Note we will *skip* the first word entirely.
    while pos>0:
        word = words[pos]
        word_prev = words[pos-1]

        if word in nhabbr:
            result[prefix+'nh'] = nhabbr[words[pos]]
        if word in suffixes:
            result[prefix+'strsuffix'] = word.capitalize()
        elif word in ('h', 'r'):
            result['owner'] = True if word=='h' else False
        elif word == 'do':
            repeat_street = True
        elif word in streets or word in strabbr:
            if word in strabbr:
                street = strabbr[word].capitalize()
            else:
                street = word.capitalize()
            if word_prev in ('n', 's', 'e', 'w'):
                street = "%s %s" % (word_prev.capitalize(), street)
                pos -= 1
            result[prefix+'street'] = street
        elif word.isdigit():
            result[prefix+'number'] = word
            prefix = 'b_'       
        pos -= 1

    if repeat_street:
        result['street'] = result['b_street']
    if 'b_street' in result and 'b_number' not in result:
        del result['b_street']
    if 'b_street' not in result:
        del result['b_nh']
        del result['b_strsuffix']
    return result
