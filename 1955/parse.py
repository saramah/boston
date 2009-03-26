# at most 1 name per line
# <97> at beginning of line, though not always
# [lastname] firstname [initial] [(wifename)] [profession] [marital status] number streetname [neighborhood]
# 

import re
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

lines, errors, died = {}, [], []

#useful constants
pattern = r'\bdied\b'

las = 0 #lastname
fir = 1 #firstname
ini = 2 #initial
spo = 3 #spouse
pro = 4 #profession
mar = 5 #marital status: r, h, wid
num = 6 #house number
st = 7 #street name
nei = 8 #neighborhood


with open("sample_1955.txt") as infile:
    last_name = ""
    last_line_chomp = ""
    for line_number, line in enumerate(infile):
        if line_number % 1000 is 0:
            print line_number
        #skip lines of people who died, they lack address information
        #and so aren't useful for what we want. we'll hold onto them
        #anyway in died, just in case this info comes in handy later
        if re.search(pattern, line):
            died.append("%d %s lastname: %s" % (line_number, line.strip(), last_name))
            continue
        entry = {}
        last_chomp = ""
        line = line.split().__iter__()
        try:
            #first bit in the line.
            #   -uppercased lname header (continuation)
            #   -subline
            #   -singleton/first instance of lname
            #   -continuation of previous line
            chomp = line.next() 
            #last name
            if chomp.isupper():
                last_name = chomp.capitalize()
                continue
            try:
                if lnames[chomp.capitalize()]:
                    try:
                        #if we already have a last name, for
                        #the case when street or first name
                        #collides with last name
                        if entry["last"]:
                            break
                    except KeyError:
                        last_name = chomp
                        last_chomp = las
                        #if it's the only thing on the line,
                        #we don't set the entry lastname because
                        #we don't want to make it an entry
                        continue
            except KeyError: pass
            #firstname
            if chomp.startswith("\x97"):
                first = chomp[4:].capitalize()
                try:
                    entry["first"] = nameabbr[first]
                except KeyError:
                    entry["first"] = first
                entry["last"] = last_name
                last_chomp = fir

            #2nd bit on line
            #   -first name
            #   -initial, part of first name
            #   -spouse name
            #   -profession
            #   -marital status
            #   
            chomp = line.next()

            #last thing we saw was a last name
            if last_chomp is las:
                first = chomp.capitalize()
                try:
                    entry["first"] = nameabbr[first]
                except KeyError:
                    entry["first"] = first
                last_chomp = fir
            #neighborhood
            try:
                entry["nh"] = neighabbr[chomp]
            except KeyError:
                try:
                    if nhoods[chomp]:
                        entry["nh"] = chomp
                #everything without an explicit neighborhood entry
                #is in Boston proper
                except KeyError:
                    entry["nh"] = "Boston"
        except StopIteration: pass 
print lines
print "ERROR'D"
for xx in errors:
    print xx
#print "DIED"
#for dead in died:
#    print dead
