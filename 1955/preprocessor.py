import sys
from helpers import build_dictionary

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

ntuple = ("Dor", "Mat", "Bline", "Br", "Winthp", "Rox", "W'Town",
          "Alls", "Camb", "Wol", "EB", "CH", "Wash", "Chel", "JP",
          "Arl", "Belmt", "Chsn", "Evrt", "Fairm't", "HP", "Maid",
          "Mald", "Med", "Milt", "Melr", "Newt", "Nvl", "Readv",
          "Revr", "Ros", "SB", "Somv", "WR", "Wlnthp", "Winch",
          "Wellesley", "Wakefield", "Quincy", "do")

lnames = build_dictionary("../dict/lastnames.txt", False)

with open(sys.argv[1]) as infile:
    with open(sys.argv[2], 'w') as outfile:
        prev_line = ""
        condense = False
        for line in infile:
            line = line.strip()
            if condense:
                start = line.split()[0]
                if line.startswith("\x97") or start.isupper() or start in lnames:
                    #false alarm, new entry or lname header
                    outfile.write(prev_line + '\n')
                else:
                    line = condense_lines(prev_line, [line])
                condense = False
            if not line.endswith(ntuple):
                prev_line = line
                condense = True
                #wait to write the line until we've condensed it
                continue
            outfile.write(line + '\n')
