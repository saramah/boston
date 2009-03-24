# at most 1 name per line
# <97> at beginning of line, though not always
# [lastname] firstname [initial] [(wifename)] [profession] [marital status] number streetname [neighborhood]
# 

import sys

def build_dictionary(path):
    build = {}
    with open(path) as infile:
        for line in infile:
            line = line.split()
            val = True
            if len(line) > 1:
                val = " ".join(line[1:]).strip()
            build[line[0].strip()] = val
    return build
    

lines, errors = [], []
last, prev_line = "", ""
line_number = 0

#####build dictionaries
#last names, male/female first names, streets, neighborhoods
#neighborhood abbreviations, name abbreviations
lnames = build_dictionary("../dict/lastnames.txt")
mnames = build_dictionary("../dict/mfirst.txt")
fnames = build_dictionary("../dict/ffirst.txt")
streets = build_dictionary("../dict/boston-streets.txt")
nhoods = build_dictionary("../dict/neighborhoods.txt")
nameabbr = build_dictionary("../dict/firstabbr.txt")
neighabbr = build_dictionary("../dict/neighabbr.txt")

print neighabbr
sys.exit()

with open("sample_1955.txt") as infile:
    for line_number, line in enumerate(infile):
        for chomp in line.split():
            if chomp.startswith("\x97"):
                first = chomp[4:].capitalize()
                



#####the actual parsing
with open("sample_1955.txt") as infile:
    for line_number, line in enumerate(infile):
        line = line.split()
        if len(line) < 1:
            continue
        #normal line, start of entry (last name header)
        if line[0].startswith("\x97"):
            first = line[0][4:].capitalize()
            #expand abbreviations
            try:
                if nameabbr[first]:
                    first = nameabbr[first]
            except KeyError:
                pass
            lines.append(first + " " + last)
        #last name header
        elif line[0].isupper():
            last = line[0].strip().capitalize()
        #singleton last name/alt multiple lastname, first entry
        elif lnames[line[0]]:
            last = line[0]
            first = nameabbr[line[1]] or line[1]
            if len(first) is 1 or len(line[2]) is 1:
                first = first + " " + line[2]
            lines.append(first + " " + last)
        #error'd line
        else:
            errors.append(str(line_number) + " " + line[0])
        prev_line = line

print lines
print "ERROR'D"
for xx in errors:
    print xx
