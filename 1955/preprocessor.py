"""
preprocessor.py

Cleans up 1955 data by attempting to rejoin split lines before
actual parsing begins
"""

import sys
from helpers import * 

ntuple = tuple(build_dictionary("../dict/neighabbr.txt", True).keys())

def process(fromfile):
    processed = []
    with open(fromfile) as infile:
        prev_line = ""
        condense = False
        lastname = ""
        for line in infile:
            #ignore empty lines
            if line.isspace():
                continue
            #stripping whitespace, commas, and periods
            line = line.strip()
            line = line.replace(",","")
            line = line.replace(".","")
            #converting subentries to a consistent start
            if line.capitalize() in neighabbr:
                prev_line += " " + line
                processed.append(prev_line + '\n')
                continue
            if line.startswith("--"):
                line = "\x97%s" %(line[2:])
            elif line.startswith(("_", "-")):
                line = "\x97%s" %(line[1:])
            #condensing entries to one line
            if condense:
                start = line.split()[0]
                if not start in ntuple and (line.startswith("\x97") 
                        or start.isupper() or start in lnames):
                    #false alarm, new entry or lname header
                    processed.append(prev_line + '\n')
                else:
                    line = condense_lines(prev_line, [line])
                condense = False
            if len(line.split()) < 3:
                prev_line = line
                condense = True
                continue
            #a line needs to be condensed if it doesn't end with a neighborhood
            #XXX this doesn't work with Boston entries, as entries in boston proper
            #don't end with any neighborhood
            if not line.endswith(ntuple):
                prev_line = line
                condense = True
                #wait to write the line until we've condensed it
                continue
            processed.append(line + '\n')
    return processed

