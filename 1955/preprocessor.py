"""
preprocessor.py

Cleans up 1955 data by attempting to rejoin split lines before
actual parsing begins
"""

import sys
from helpers import build_dictionary, condense_lines 

ntuple = ("Dor", "Mat", "Bline", "Br", "Winthp", "Rox", "W'Town",
          "Alls", "Camb", "Wol", "EB", "CH", "Wash", "Chel", "JP",
          "Arl", "Belmt", "Chsn", "Evrt", "Fairm't", "HP", "Maid",
          "Mald", "Med", "Milt", "Melr", "Newt", "Nvl", "Readv",
          "Revr", "Ros", "SB", "Somv", "WR", "Wlnthp", "Winch",
          "Wellesley", "Wakefield", "Quincy", "do", "Lynn", "Bedford",
          "Box", "Newton")

lnames = build_dictionary("../dict/lastnames.txt", False)

with open(sys.argv[1]) as infile:
    with open(sys.argv[2], 'w') as outfile:
        prev_line = ""
        condense = False
        for line in infile:
            if line.isspace():
                continue
            #stripping whitespace, commas, and periods
            line = line.strip()
            line = line.replace(",","")
            line = line.replace(".","")
            #converting subentries to a consistent start
            if line.startswith("--"):
                line = "\x97%s" %(line[2:])
            elif line.startswith(("_", "-")):
                line = "\x97%s" %(line[1:])
            #condensing entries to one line
            if condense:
                start = line.split()[0]
                if not start in ntuple and (line.startswith("\x97") or start.isupper() or start in lnames):
                    #false alarm, new entry or lname header
                    outfile.write(prev_line + '\n')
                else:
                    line = condense_lines(prev_line, [line])
                condense = False
            #a line needs to be condensed if it doesn't end with a neighborhood
            #XXX this doesn't work with Boston entries, as entries in boston proper
            #don't end with any neighborhood
            if not line.endswith(ntuple):
                prev_line = line
                condense = True
                #wait to write the line until we've condensed it
                continue
            outfile.write(line + '\n')

