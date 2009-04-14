from __future__ import with_statement
"""
preprocessor.py

Cleans up 1955 data by attempting to rejoin split lines before
actual parsing begins
"""
import re
import sys
from helpers import * 

ntuple = tuple(build_dictionary("../dict/neighabbr.txt", True).keys())
stuple = tuple(build_dictionary("../dict/streetnames.txt", False))


def process(fromfile):
    processed = []
    with open(fromfile) as infile:
        prev_line = ""
        condense = False
        lastname = ""
        count = 0
        for line in infile:
            count += 1
            #ignore died lines and empty lines
            if re.search(r'\bdied\b', line):
                continue
            #purging room numbers
            for room in re.findall(r'(?:\brms\s\d+(?:\s|-)\d+)|(?:\brm\s+\d+)', line):
                line = line.replace(room, "")
            #stripping leading/trailing whitespace, commas, and periods
            line = line.strip()
            line = line.replace(",","")
            line = line.replace(".","")
            if line.isspace() or line == "":
                continue
            #hackish; do doesn't get caught by the preprocessor as being
            #something that should be condensed
            if line == "do":
                continue
            #converting subentries to a consistent start
            if line.startswith("--"):
                line = "\x97%s" %(line[2:])
            elif line.startswith(("_", "-")):
                line = "\x97%s" %(line[1:])
            elif line.startswith("-\x97"):
                line = line[1:]
            if line.lower() in nhabbr:
                prev_line += " " + line
                processed.append(prev_line + '\n')
                #we already condensed the lines right here, so we don't
                #need to recondense them again
                condense = False
                continue
            if line.split()[-1].isdigit():
                prev_line = line
                condense = True
                continue
            #condensing entries to one line
            if condense:
                start = line.split()[0]
                end = prev_line.split()[-1]
                definite = prev_line.endswith("-") or end.isdigit()
                no_condense = line.startswith("\x97") or start.isupper() or (start.lower() in lnames)
#                print "definite: %s nocondense: %d" % (definite, no_condense)
#                print "neigh?: %s street?: %s" % (start in ntuple, start in stuple)
                if not (start in ntuple) and not (start in stuple) and not definite and no_condense:
                    #false alarm, new entry or lname header
                    processed.append(prev_line + '\n')
                else:
                    line = condense_lines(prev_line, [line])
                    processed.append(line + '\n')
                condense = False
                continue
            if len(line.split()) < 3:
                prev_line = line
                condense = True
                continue
            #a line needs to be condensed if it doesn't end with a neighborhood
            if not line.lower().endswith(ntuple) or not line.lower().endswith(stuple):
                prev_line = line
                condense = True
                #wait to write the line until we've condensed it
                continue
            processed.append(line + '\n')
    #if we hit EOF on a condensed line, write out the line anyway
    if condense:
        processed.append(prev_line)
    return processed

