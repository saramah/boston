from __future__ import with_statement
"""
helpers.py

Helper functions for parse.py and preprocessor.py, 1955.
"""
import re
import sys

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
    builds a dictionary of key-value pairs, normalizing everything
    to lowercase.

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
                line = line.split(",")
                key = line[0].strip().lower()
                val = line[1].strip()
            if key not in build:
                build[key] = val
    return build

#####build dictionaries
#last names, male/female first names, streets, neighborhoods
#neighborhood abbreviations, name abbreviations
lnames = build_dictionary("dict/alllnames.txt", False)
fnames = build_dictionary("dict/firstnames.txt", False)
streets = build_dictionary("dict/allstreets.txt", False)
states = build_dictionary("dict/states.txt", True)
nameabbr = build_dictionary("dict/firstabbr.txt", True)
strabbr = build_dictionary("dict/strabbr.txt", True)
nhoods = build_dictionary("dict/allnhabbr.txt", True)
boston_nh = build_dictionary("dict/boston.txt", False)
nonboston_nh = build_dictionary("dict/nonboston.txt", True)
suffixes = ['st', 'pk', 'rd', 'ct', 'av', 'la', 'dr', 'ter','pl','pi','hway', 'way', 'blvd']
 
def build_list(path):
    """
    build_list: takes a path and returns a list of every
    line in the file, stripped of newlines and normalized to
    lowercase.

    currently used for the keeping track of lastnames throughout
    the directory
    """
    build = []
    with open(path) as infile:
        for line in infile:
            build.append(line.strip().lower())
    return build


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
    except IndexError: 
        pass
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
    if dist_firstletter < -1:
        return False
    return True

#lname_marker - list of all lastnames
lname_marker = build_list("dict/alllnames.txt")
#window - the tolerance for jumping lastnames. with some
#loose initial analysis, it seems the jumps between lastnames
#in the directory range from 1 to 40; setting a low tolerance
#should result in relatively accurate last name progression
WINDOW = 300
BACK_WINDOW = 300 

def distance(index, lastname):
    """
    Determines the distance to lastname in lname_marker from the
    current last name. If lastname isn't in the dictionary, distance
    returns 0. distance starts at back_window (currently %s) and stops 
    looking at window (currently %s). 
    """ % (BACK_WINDOW, WINDOW)
    if (not lastname in lnames) or (lastname in suffixes):
        return 0
    lower_bound = 0
    if index < BACK_WINDOW:
        lower_bound = 0
    else:
        lower_bound = index - BACK_WINDOW
    point = lname_marker[lower_bound] 
    point_index = lower_bound
    diff = 0
    while not (diff > WINDOW):
        diff = point_index - index
        point_index += 1
        try:
            point = lname_marker[point_index]
            if point == lastname:
                return diff
        except IndexError:
            break
    return 0

def recognize(atom):
    """
    Recognizes the meaning of the atom passed in and returns
    a tuple; the first bit of the tuple is the key for the
    entry, while the second is the value, and the third is the
    value for last_chomp.
    """
    if atom == "r":
        return ("owner", "renter", OWNER)
    elif atom == "h" or atom == "b" or atom == "n":
        return ("owner", "owner", OWNER)
    atom = atom.lower()
    if atom == "wid" or atom == "wio":
        return ("widowed", True, WIDOWED)
    elif atom == "mrs":
        return ("married", True, MRS)
    elif atom.startswith("(") or atom.endswith(")"):
        atom = atom.strip("()")
        return ("spouse", atom.title(), SPOUSE)
    elif atom.isalpha() and len(atom) == 1:
        return ("first", atom.capitalize(), INITIAL)
    elif atom == "ii" or atom == "iii":
        return ("first", atom.capitalize(), INITIAL)
    elif atom =="jr":
        return ("first", atom.capitalize(), INITIAL)
    elif atom.isdigit():
        return ("number", atom, HOUSE_NUM)
    elif atom in suffixes:
        remap = {'av': 'Ave', 'la': 'Ln', 'pi': 'Pl','ro':'Rd'}
        if atom in remap:
            atom = remap[atom]
        else:
            atom = atom.capitalize()
        return ("strsuffix", atom, STREET_SUFFIX)
    elif atom in nhoods:
        return ("nh", nhoods[atom], NH)
    else:
        return None

def translate(number):
    """
    Converts letters into digits.
    """
    number = number.replace("O","0")
    number = number.replace("l","1")
    number = number.replace("I","1")
    number = number.replace("S","5")
    number = number.replace("B","8")
    return number


def parse_addr(line):
    """
    Locates addresses in the given line, and returns a dict
    with addresses split up into composite parts. At most,
    this function will return two addresses: a business address
    and a residential address.
    """
    words = line.split()
    pos = len(words) - 1
    prefix = ''
    lookbehind = ('', 0)
    repeat_street = False
    result = {'strsuffix': 'St', 'nh': 'Boston',
              'b_strsuffix': 'St', 'b_nh': 'Boston'}

    # Note we will *skip* the first word entirely.
    while pos>0:
        word = words[pos]
        word_prev = words[pos-1]
        print 'w [%s] pos [%s] res [%s]' % (word, pos, result)

        if word.lower() in states:
            if len(result.keys()) == 0:
                result['street'] = word
        if word.lower() in nhoods:
            # If we find a NH before a street address,
            # it belongs to the business street.
            if 'street' in result:
                prefix = 'b_'
            result[prefix+'nh'] = nhoods[words[pos].lower()]
        elif word.lower() in suffixes:
            # If we find a suffix before a street address,
            # it belongs to the business street.
            if 'street' in result:
                prefix = 'b_'
            result[prefix+'strsuffix'] = word.capitalize()
        elif word in ('h', 'r', 'b', 'n'):
            result['owner'] = False if word=='r' else True 
        elif word == 'do':
            repeat_street = True
        elif word.isdigit():
            result[prefix+'number'] = word
            prefix = 'b_'
        else:
            # Try to greedy-match a street name up to 5 words long (incl. this)
            # Note we're still not looking at the first two words of the line.
            start = 2 if (pos-4)<2 else pos-4
            for i in range(start, pos+1):
                cur_match = ' '.join(words[i:pos+1])
                if cur_match.lower() in streets or cur_match.lower() in strabbr:
                    if not prefix and not 'street' in result:
                        key = 'street'
                    elif 'b_street' not in result:
                        key = 'b_street'
                    else:
                        continue
                    pos = i
                    if cur_match.lower() in strabbr:
                        cur_match = strabbr[cur_match.lower()]
                    if words[i-1].lower() in ('n', 's', 'e', 'w'):
                        cur_match = "%s %s" % (words[i-1].capitalize(),
                                               cur_match)
                        pos -= 1
                    result[key] = ' '.join(map(str.capitalize, cur_match.split()))
                    break
        pos -= 1

    if repeat_street:
        # blah blah blah 350 Hanover do
        # Copy street, (number), nh to b_
        if not 'b_street' in result:
            #if we encounter a ditto when we don't have any address
            #we can't do anything, so just return None
            if not 'street' in result:
                return None
            result['b_street'] = result['street']
            result['b_nh'] = result['nh']
            if 'number' in result:
                result['b_number'] = result['number']
        # 350 Hanover Rox 352 do
        # copy (b_street), nh to street
        else:
            if not 'street' in result:
                result['street'] = result['b_street']
            result['nh'] = result['b_nh']
    if 'b_street' not in result:
        del result['b_nh']
        del result['b_strsuffix']
    return result

if __name__ == '__main__':
    line = "\x97Wm (Marie A) dept store 352 Hanover Rox h 350 do"
    print line
    print parse_addr(line)
