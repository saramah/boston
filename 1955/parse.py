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
fnames = build_dictionary("../dict/firstnames.txt")
streets = build_dictionary("../dict/streetnames.txt")
nhoods = build_dictionary("../dict/neighborhoods.txt")
nameabbr = build_dictionary("../dict/firstabbr.txt")
strabbr = build_dictionary("../dict/strabbr.txt")
neighabbr = build_dictionary("../dict/neighabbr.txt")

lines, errors, died = [], [], []

#useful constants
pattern = r'\bdied\b'

las = 0 #lastname
fir = 1 #firstname
ini = 2 #initial
spo = 3 #spouse
pro = 4 #profession
mar = 5 #wid
own = 6 #house ownership status
num = 7 #house number
st = 8 #street name
nei = 9 #neighborhood


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
        last_chomp = -1
        lineiter = line.split().__iter__()
        try:
            #first bit in the line.
            #   -uppercased lname header (continuation)
            #   -subline
            #   -singleton/first instance of lname
            #
            #   -continuation of previous line; considered ERROR'D for now
            chomp = lineiter.next() 
            #lastname
            if chomp.capitalize() in lnames:
                last_name = chomp.capitalize()
                #lastname continuation header
                if chomp.isupper():
                    continue
                last_chomp = las
            #firstname
            if chomp.startswith("\x97"):
                first = chomp[1:].capitalize()
                if first in nameabbr:
                    entry["first"] = nameabbr[first]
                else:
                    entry["first"] = first
                entry["last"] = last_name
                last_chomp = fir
            #at the moment, we're not handling continued lines, 
            #which is more than half of the errors list
            if last_chomp is -1:
#DEBUG                lines.append("%d %s" % (line_number, line.strip()))
                errors.append("%d %s UNHANDLED PREFIX" % (line_number, line.strip()))
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
                first = chomp.capitalize()
                if first in nameabbr:
                    entry["first"] = nameabbr[first]
                elif chomp in fnames:
                    entry["first"] = chomp
                else:
                    errors.append("%d %s NO NAME" % (line_number, line.strip()))
                    continue
                last_chomp = fir
            #if the last thing we say was a firstname, 
            #next could be one of five things:
            #   -spouse name
            #   -profession
            #   -initial
            #   -own/rent ('r'enter, 'h'ouseholder)
            #   -"Mrs"
            elif last_chomp is fir:
                #spouse name XXX not showing up
                if chomp.startswith("("):
                    if chomp.strip("()") not in fnames:
                        errors.append("%d %s UNKNOWN SPOUSE NAME" % (line_number, line.strip()))
                        continue
                    if not chomp.endswith(")"):
                        initial = lineiter.next()
                        chomp = chomp + " " + initial
                    entry["spouse"] = chomp.strip("()")
                    last_chomp = spo
                #either profession, marital status, or home status
                elif chomp.islower():
                    if chomp is "r":
                        entry["ownership"] = "renter"
                        last_chomp = own 
                    elif chomp is "h":
                        entry["ownership"] = "owner"
                        last_chomp = own
                    elif chomp is "wid":
                        entry["widowed"] = True
                        last_chomp = wid
                    #initial to tack on to first name
                    elif chomp.isalpha() and len(chomp) is 1:
                        entry["first"] = entry["first"] + " " + chomp
                    else:
                        #TODO: grab professional abbreviations, convert abbr version to
                        #expanded version
                        entry["prof"] = chomp
                        last_chomp = pro
                elif chomp is "Mrs":
                    pass
                else:
                    errors.append("%d %s UNKNOWN 2nd CHOMP" % (line_number, line.strip()))
                    continue

                chomp = lineiter.next()
            #neighborhood
#            try:
 #               entry["nh"] = neighabbr[chomp]
  #          except KeyError:
   #             try:
    #                if nhoods[chomp]:
     #                   entry["nh"] = chomp
                #everything without an explicit neighborhood entry
                #is in Boston proper
     #           except KeyError:
      #              entry["nh"] = "Boston"
        except StopIteration:  
            pass
        lines.append("%d %s" % (line_number, entry))

for good in lines:
    print good

print "ERROR'D"
for xx in errors:
    print xx
#print "DIED"
#for dead in died:
#    print dead
