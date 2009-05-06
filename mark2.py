from __future__ import with_statement
"""
preprocessor mark ii.
"""

import re
import sys
from helpers import *

ntuple = tuple(build_dictionary("dict/allnhabbr.txt", True).keys())
stuple = tuple(build_dictionary("dict/allstreets.txt", False))
strsuffix = ('rd','ro','pkwy','ln','ct','pk','st','sq','av','pl','pi','ter','dr','la')
condense_prefixes = ('rd', 'do', 'pkwy', 'ln', 'ct', 'pk', 'st', 'av', 'pl', 'pi',
        'ter', 'dr', 'la', 'co', 'inc', 'ro','r','h')

def process(fromfile):
    processed = []
    with open(fromfile) as infile:
        text = infile.read()
        #remove rooms
        for room in re.findall(r'(?im)(?:\brms\s\d+(?:\s|-)\d+)|(?:\brm\s+\d+)', text):
            text = text.replace(room, "")
        #remove apartments
        for apt in re.findall(r'(?im)\bAPT\s+(?:\d|A)+(?:\b|\n|\r)+', text):
            text = text.replace(apt, "")

        prev_line = ""
        to_append = ""
        condense = False
        count = 0
        for line in text.split('\n'):
            count += 1
            line = line.strip()
            line = line.replace(",","")
            line = line.replace(".","")
            if line.isspace() or line == "" or line.isdigit():
                if condense:
                    condense = False
                continue
            #convert subentries to consistent start
            if line.startswith("--"):
                line = "\x97%s" %(line[2:])
            elif line.startswith(("_", "-")):
                line = "\x97%s" %(line[1:])
            elif line.startswith("-\x97"):
                line = line[1:]
            start = line.split()[0]
            #if this line must be condensed with the last
            #one, condense the lines before any other analysis
            #is done
            if condense:
                #false alarm, don't condense
                if (not line.startswith("\x97")) or (not start.isupper()) or (not start in lnames):
                    line = condense_lines(prev_line, [line])
                condense = False
            #we need to condense this line with the next one
            if line.endswith("-"):
                condense = True
                prev_line = line
                continue
            if (not line.endswith(ntuple)) or (not line.endswith(stuple)) or (not line.endswith(strsuffix)) or (not line.endswith("Mass")):
                condense = True
                prev_line = line
                continue
            #we need to condense it with the previous line
            start = line.split()[0]
            if start.lower() in condense_prefixes:
                prev_line += " " + line
                continue
            processed.append(prev_line + '\n')
            prev_line = line
    if condense:
        processed.append(prev_line)
    return processed
