"""
parse.py

Putting data from the 1955 Boston Directory into a useful format. Run
preprocessor.py first, as it will increase the accuracy with which we
can pull useful information from the OCR'd text.

Invariants of data:
    - at most 1 name per line
    - every line has a firstname, a number, and a streetname
    - if neighborhood is not given, address is in Boston proper

"""

# at most 1 name per line
# [lastname] firstname [initial] [Mrs] [(wifename)] [profession] [wid] [homeowner status] number streetname [neighborhood]

import re
import sys
from helpers import * 
    
#####build dictionaries
#last names, male/female first names, streets, neighborhoods
#neighborhood abbreviations, name abbreviations
lnames = build_dictionary("../dict/lastnames.txt", False)
fnames = build_dictionary("../dict/firstnames.txt", False)
streets = build_dictionary("../dict/streetnames.txt", False)
nhoods = build_dictionary("../dict/neighborhoods.txt", False)
nameabbr = build_dictionary("../dict/firstabbr.txt", True)
strabbr = build_dictionary("../dict/strabbr.txt", True)
neighabbr = build_dictionary("../dict/neighabbr.txt", True)

lines, errors, broken, died = [], [], [], []


with open(sys.argv[1]) as infile:
    last_name = ""
    for line_number, line in enumerate(infile):
        if line_number % 1000 is 0:
            print line_number
        #skip lines of people who died, they lack address information
        #and so aren't useful for what we want. we'll hold onto them
        #anyway in died, just in case this info comes in handy later
        if re.search(r'\bdied\b', line):
            died.append("%d %s lastname: %s" % (line_number, line.strip(), last_name))
            continue
        #if the line contains one of the invalid characters, error the line.
        if find_errors(line):
            broken.append("%d %s CONTAINS INVALID CHARS" % (line_number, line.strip()))
            continue

        entry = {}
        last_chomp = -1
        last_entry = {}
        lineiter = line.split().__iter__()
        try:
            #first bit in the line.
            #   -uppercased lname header (continuation)
            #   -subline
            #   -singleton/first instance of lname
            chomp = lineiter.next() 
            #lastname
            #XXX Co H en vs Cohig see Cohen, Cohane only grabs Co from
            #the first one, we'd like Cohen if possible
            if chomp.capitalize() in lnames:
                chomp = chomp.capitalize()
                if valid_jump(last_name, chomp):
                    last_name = chomp
                    last_chomp = las
                else:
                    broken.append("%d %s BAD JUMP" % (line_number+1, line.strip()))
                    continue
            #firstname
            if chomp.startswith("\x97"):
                first = chomp[1:].capitalize()
                if first.capitalize() in nameabbr:
                    entry["first"] = nameabbr[first]
                else:
                    entry["first"] = first
                entry["last"] = last_name
                if len(first) is 1:
                    last_chomp = ini
                else:
                    last_chomp = fir
            #at the moment, we're not handling continued lines, 
            #which is more than half of the errors list
            if last_chomp is -1:
#DEBUG                lines.append("%d %s" % (line_number, line.strip()))
                errors.append("%d %s UNHANDLED PREFIX" % (line_number+1, line.strip()))
                continue
            #2nd bit on line
            #   -first name
            #   -initial, part of first name
            #   -spouse name
            #   -profession
            #   -marital status
            #   
            chomp = lineiter.next()

            #if the last thing we saw was a lastname,
            #then the next thing must be a firstname
            if last_chomp is las:
                first = chomp.capitalize().strip(",")
                if first in nameabbr:
                    entry["first"] = nameabbr[first]
                elif first in fnames:
                    entry["first"] = first
                else:
                    errors.append("%d %s NO NAME" % (line_number+1, line.strip()))
                    continue
                entry["last"] = last_name
                last_chomp = fir
                chomp = lineiter.next()
            #if the last thing we say was a firstname, 
            #next could be one of five things:
            #   -spouse name
            #   -profession
            #   -initial
            #   -own/rent ('r'enter, 'h'ouseholder)
            #   -"Mrs"
            broke = False
            #XXX this misses the case when there is no street number, just
            # a street.
            while(not chomp.isdigit()):
                tup = recognize(chomp)
                if tup is None:
                    if "prof" in entry:
                        entry["prof"] = entry["prof"] + " " + chomp
                    else:
                        entry["prof"] = chomp
                    last_chomp = pro
                else:
                    #initial is special case; need to tack it onto entry["first"]
                    if tup[2] is ini:
                        entry["first"] = entry["first"] + " " + chomp
                    elif tup[2] is spo:
                        chomp = tup[1]
                        if chomp.capitalize() in nameabbr:
                            chomp = nameabbr[chomp.capitalize()]
                        if chomp.capitalize() in fnames:
                            if "spouse" in entry:
                                entry["spouse"] = entry["spouse"] + " " + chomp
                            else:
                                entry["spouse"] = chomp
                        else:
                            errors.append("%d %s INVALID SPOUSENAME" % (line_number+1, line.strip()))
                            broke = True
                            break
                    #XXX widowed is also a special case, deceased husband's name might
                    #appear directly after this
                    else:
                        entry[tup[0]] = tup[1]
                    last_chomp = tup[2]
                chomp = lineiter.next()

            if broke:
                continue
            entry["number"] = chomp

            chomp = lineiter.next()
            #expanding direction names for streets
            if chomp == "E":
                chomp = "East " + lineiter.next().strip()
            elif chomp == "S":
                chomp = "South " + lineiter.next().strip()
            elif chomp == "W":
                chomp = "West " + lineiter.next().strip()
            elif chomp == "N":
                chomp = "North " + lineiter.next().strip()
            
            #picking out the street name
            if chomp.capitalize() in strabbr:
                entry["street"] = strabbr[chomp.capitalize()]
            entry["street"] = chomp
            last_chomp = str
            #default street suffix of St
            entry["strsuffix"] = "St"

            chomp = lineiter.next()

            tup = recognize(chomp)
            if tup is None:
                #second half of streetname?
                if "street" in entry:
                    whole = entry["street"] + " " + chomp
                    if whole.title() in strabbr:
                        entry["street"] = whole
                    elif whole.title() in streets:
                        entry["street"] = whole
                    last_chomp = str
                elif chomp.capitalize() in neighabbr:
                    entry["nh"] = neighabbr[chomp.capitalize()]
                    last_chomp = nei
                else:
                    errors.append("%d %s UNKNOWN CHOMP" % (line_number+1, line.strip()))
                    continue
            else:
                entry[tup[0]] = tup[1]                
                last_chomp = tup[2]

            #default neighborhood
            entry["nh"] = "Boston"

            #keep going until we hit an exception
            while True:
                chomp = lineiter.next()
                tup = recognize(chomp)
                if tup is None:
                    if chomp.capitalize() in neighabbr:
                        entry["nh"] = neighabbr[chomp.capitalize()]
                        last_chomp = nei
                    else:
                        errors.append("%d %s NOT THE END?\n%d %s" % 
                                (line_number+1, line.strip(), line_number+1, entry))
                        break
                else:
                    entry[tup[0]] = tup[1]
                    last_chomp = tup[2]

        except StopIteration:  
            pass
        #if an entry doesn't have at least a firstname, a lastname, and an address,
        #error it so we can figure out why.
        if "first" not in entry or "last" not in entry or "street" not in entry:
            errors.append("%d %s INCOMPLETE ENTRY\n%d %s" % 
                    (line_number+1, line.strip(), line_number+1, entry))
            continue

        lines.append("%d %s" % (line_number+1, entry))

for good in lines:
    print good

print "ERROR'D"
for xx in errors:
    print xx

#print "BROKEN"
#for x in broken:
#    print x

llength = len(lines)
elength = len(errors)
blength = len(broken)
total = llength + elength + blength

print "good lines: %d" % (llength)
print "fixable lines: %d" % (elength)
print "broken lines: %d" % (blength)
print total
print "error rate: %f" % (float(blength + elength)/total)
#print "DIED"
#for dead in died:
#    print dead
