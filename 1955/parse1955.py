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
            try:
                #ignore multiple keys, we only need one
                if build[line[0].strip()]:
                    continue
            except KeyError:
                build[line[0].strip()] = val
    return build
    


las = 0 #lastname
fir = 1 #firstname
ini = 2 #initial
spo = 3 #spouse
pro = 4 #profession
mar = 5 #marital status: r, h, wid
num = 6 #house number
st = 7 #street name
nei = 8 #neighborhood


#####build dictionaries
#last names, male/female first names, streets, neighborhoods
#neighborhood abbreviations, name abbreviations
lnames = build_dictionary("../dict/lastnames.txt")
mnames = build_dictionary("../dict/mfirst.txt")
fnames = build_dictionary("../dict/ffirst.txt")
streets = build_dictionary("../dict/streetnames.txt")
nhoods = build_dictionary("../dict/neighborhoods.txt")
nameabbr = build_dictionary("../dict/firstabbr.txt")
strabbr = build_dictionary("../dict/strabbr.txt")
neighabbr = build_dictionary("../dict/neighabbr.txt")

lines, errors = [], []

with open("sample_1955.txt") as infile:
    last_name = ""
    last_entry = {}
    last_chomp = ""
    for line_number, line in enumerate(infile):
        entry = {}
        skip = False
        line = line.split()
        length = len(line)
        for index, chomp in enumerate(line):
            if skip is True:
                skip = False
                continue
            #last name
            if chomp.isupper():
                last_name = chomp.capitalize()
                break
            try:
                if lnames[chomp.capitalize()]:
                    if
                    try:
                        #if we already have a last name, for
                        #the case when street or first name
                        #collides with last name
                        if entry["last"]:
                            break
                    except KeyError:
                        last_name = chomp
                        #if it's the only thing on the line,
                        #we don't set the entry lastname because
                        #we don't want to make it an entry
                        continue
            except KeyError: pass
            #first name
            if chomp.startswith("\x97"):
                entry["first"] = chomp[4:].capitalize()
                try:
                    entry["first"] = nameabbr[entry["first"]]
                except KeyError: pass
                entry["last"] = last_name
                #extra initial
                last_chomp = fir
            #spouse
            if chomp.startswith("("):
                entry["spouse"] = chomp.strip("()")
                try:
                    entry["spouse"] = nameabbr[entry["spouse"]]
                except KeyError: pass
                last_chomp = spo
            #profession

            #house number
            if chomp.isdigit():
                entry["number"] = chomp
                last_chomp = num
            #street
            try:
                if streets[chomp]:
                    
                last_chomp = st
                skip = True
            except KeyError: pass
            #neighborhood
            try:
                last_chomp = nei
        last_entry = entry

print lines
print "ERROR'D"
for xx in errors:
    print xx
