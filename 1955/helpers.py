"""
helpers.py

Helper functions for parse.py and preprocessor.py, 1955.
"""


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
#    if not line.strip()[1:].isalnum():
#        return True
    invalid = "`~!@#$%^*_=+{}<>?/\|"
    for char in invalid:
        if char in line:
            return True
    return False
