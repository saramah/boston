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
lnames = build_dictionary("../dict/alllnames.txt", False)
fnames = build_dictionary("../dict/firstnames.txt", False)
streets = build_dictionary("../dict/allstreets.txt", False)
nhoods = build_dictionary("../dict/neighborhoods.txt", False)
nameabbr = build_dictionary("../dict/firstabbr.txt", True)
strabbr = build_dictionary("../dict/strabbr.txt", True)
nhabbr = build_dictionary("../dict/neighabbr.txt", True)
suffixes = ['st', 'pk', 'rd', 'ct', 'av', 'la', 'dr', 'ter','pl','pi','hway']
 
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
    if dist_firstletter < 0 or dist_firstletter > 1:
        return False
    else:
        if len(second) < 2 or len(first) < 2:
            return True
        dist_secondletter = ord(second[1].lower()) - ord(first[1].lower())
        if dist_secondletter < 0:
            return False
        return True

#lname_marker - list of all lastnames
lname_marker = build_list("../dict/alllnames.txt")
#window - the tolerance for jumping lastnames. with some
#loose initial analysis, it seems the jumps between lastnames
#in the directory range from 1 to 40; setting a low tolerance
#should result in relatively accurate last name progression
WINDOW = 100

def distance(index, lastname):
    """
    Determines the distance to lastname in lname_marker from the
    current last name. If lastname isn't in the dictionary, distance
    returns -1. distance does not look beyond window, currently 
    defined as %s.
    """ % (WINDOW)
    if not lastname in lnames:
        return -1
    point = lname_marker[index] 
    point_index = index
    diff = 0
    while point != lastname:
        if diff > WINDOW:
            return -1
        point = lname_marker[point_index]
        point_index += 1
        diff = point_index - index
    return diff

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
    elif atom == "h" or atom == "b" or atom == "n":
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
    elif atom == "ii" or atom == "iii":
        return ("first", atom.capitalize(), INITIAL)
    elif atom =="jr":
        return ("first", atom.capitalize(), INITIAL)
    elif atom.isdigit():
        return ("number", atom, HOUSE_NUM)
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
    words = map(str.lower, line.split())
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
        #print 'w [%s] pos [%s] res [%s]' % (word, pos, result)
        if word in nhabbr:
            # If we find a NH before a street address,
            # it belongs to the business street.
            if 'street' in result:
                prefix = 'b_'
            result[prefix+'nh'] = nhabbr[words[pos]]
        elif word in suffixes:
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
                if cur_match in streets or cur_match in strabbr:
                    if not prefix and not 'street' in result:
                        key = 'street'
                    elif 'b_street' not in result:
                        key = 'b_street'
                    else:
                        continue
                    pos = i
                    if cur_match in strabbr:
                        cur_match = strabbr[cur_match]
                    if words[i-1] in ('n', 's', 'e', 'w'):
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
