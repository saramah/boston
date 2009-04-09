import re
import sys
import preprocessor

from helpers import *


lines, errors, broken, died = [], [], [], []
last_name = ""
last_entry = {}

#preprocess the file before we start parsing it
preprocessed = preprocessor.process(sys.argv[1])

with open("out", 'w') as outfile:
    for x in preprocessed:
        outfile.write(x)

#getting down to the actual parsing
for line_no, line in enumerate(preprocessed):
    line = line.strip()
    #if a line has invalid characters in it, we're not dealing with it.
    #XXX wishlist: hook in a levenshtein distance calculator to fix
    #words with invalid characters.
    if find_errors(line):
        broken.append("%d %s INVALID CHARS" % (line_no+1, line))
        continue
    #stripping out death lines, these don't contain addresses
    if re.search(r'\bdied\b', line):
        died.append("%d %s lastname: %s" % (line_no+1, line, last_name))
        continue
    #some lastname headers have form "Cohig see Cohen, Cofen" etc
    #this just takes the first part of that line.
    if re.search(r'\bsee\b', line):
        line = line.split()
        potential_lname = ""
        for bit in line:
            if bit == "see":
                break
            potential_lname += bit.lower()
        potential_lname = potential_lname.capitalize()
        if valid_jump(last_name, potential_lname):
            last_name = potential_lname
        else:
            broken.append("%d %s BAD JUMP" % (line_no+1, line))
        continue

    print "%d %s" % (line_no+1, line)
    addresses = parse_addr(line)
    print "%d %s" % (line_no+1, addresses)
    continue
#    print "%d %s" % (line_no+1, num_addr)
    entry = {}
    lineiter = line.split().__iter__()
    last_chomp = -1
    try:
        chomp = lineiter.next()
        #if line starts with a last name, then grab the
        #first name after it as well
        if chomp.capitalize() in lnames:
            print "%d %s from\n%s" % (line_no+1, chomp, line)
            chomp = chomp.capitalize()
            #if the line was misread by OCR or if the lastname is multiple
            #words not connected by a hyphen, then grab the rest of it
            #XXX this necessarily kills entries with lastnames that are 
            #only the short chomps.
            if chomp == "Co" or chomp == "De":
                plname = ""
                for atom in line.split()[1:]:
                    chomp += atom.lower()
                    if plname in lnames:
                        break
                if plname not in lnames:
                    errors.append("%d %s UNRECOGNIZED LAST NAME" % (line_no+1, line))
                    continue
            if valid_jump(last_name, chomp):
                last_name = chomp
                last_chomp = las
            else:
                broken.append("%d %s BAD JUMP" % (line_no+1, line))
                continue
            
            chomp = lineiter.next()

            first = chomp.capitalize()
            if first in nameabbr:
                entry["first"] = nameabbr[first]
            elif first in fnames:
                entry["first"] = first
            else:
                errors.append("%d %s UNRECOGNIZED NAME" % (line_no+1, line))
                continue
            entry["last"] = last_name
            last_chomp = fir
        #otherwise we've got a subentry, so we should have the
        #last name from the last line
        elif chomp.startswith("\x97"):
            first = chomp[1:].capitalize()
            if first in nameabbr:
                first = nameabbr[first]
            entry["first"] = first
            entry["last"] = last_name
            if len(first) == 1:
                last_chomp = ini
            else:
                last_chomp = fir
        #if it's not a lastname or a subentry, then it's a line
        #we should have handled in our preprocessor; mark it.
        if last_chomp == -1:
            errors.append("%d %s BAD PREFIX" % (line_no+1, line))
            continue

        chomp = lineiter.next()
    
        entry["nh"] = "Boston"
        entry["strsuffix"] = "St"
        #handling everything else.
        while True:
            tup = recognize(chomp)
            if tup is None:
                if "prof" in entry:
                    entry["prof"] += " " + chomp
                else:
                    entry["prof"] = chomp
                last_chomp = pro
            else:
                #first name initial
                if tup[2] == ini:
                    entry[tup[0]] += " " + tup[1]
                    last_chomp = ini
                #spousal entry
                elif tup[2] == spo:
                    while not chomp.endswith(")"):
                        chomp += " " + lineiter.next()
                    chomp = tup[1].capitalize()
                    if chomp in nameabbr:
                        chomp = nameabbr[chomp]
                    elif chomp in fnames:
                        if "spouse" in entry:
                            entry["spouse"] += " " + chomp
                        else:
                            entry["spouse"] = chomp
                    else:
                        business = chomp.strip("()")
                        while not chomp.endswith(")"):
                            chomp = lineiter.next()
                            if chomp.endswith(")"):
                                business += " " + chomp.strip(")")
                        entry["business"] = business
                        last_chomp = bus
                        continue
                    last_chomp = spo
                #widowed entry; deceased's name optionally follows
                #XXX still not working quite right
                elif tup[2] == wid:
                    entry[tup[0]] = tup[1]
                    chomp = lineiter.next().capitalize()
                    if chomp in nameabbr:
                        chomp = nameabbr[chomp]
                    if chomp in fnames:
                        entry["spouse"] = chomp
                    else: continue
                    last_chomp = wid
                #we hit a street address
                elif tup[2] == num:
                    pass
#                    consume = 0
#                    number = tup[1]
#                    entry["strsuffix"] = "St"
                    #if we didn't recognize this address with the regex, then
                    #it's very likely not actually part of an address.
#                    if number not in addresses:
#                        errors.append("%d %s STRAY NUMBER" % (line_no+1, line))
#                        break
#
#                    address = addresses[number]
#                    if "street" in entry:
#                        entry["b_street"] = entry["street"]
#                        entry["b_number"] = entry["number"]
#                        entry["b_strsuffix"] = entry["strsuffix"]
#                    entry["number"] = number
#                    consume += 1
#                    if address[1] in strabbr:
#                        entry["street"] = strabbr[address[1]]
#                        consume += 1
#                    elif address[1] in streets:
#                        entry["street"] = address[1]
#                        consume += 1
#                    else:
#                        potential_street = ""
#                        for x in address[1].split():
#                            if x.capitalize() in neighabbr or x.capitalize() in nhoods or x == "h" or x == "r":
#                                break
#                            potential_street += " " + x
#                            if potential_street.strip() in strabbr:
#                                entry["street"] = strabbr[x]
#                            elif potential_street.strip() in streets:
#                                entry["street"] = potential_street.strip()
#                            consume += 1
#                        entry["street"] = potential_street
#                    if address[2] != "":
#                        entry["strsuffix"] = address[2]
#                        consume += 1
#                    for x in range(consume):
#                        chomp = lineiter.next()
#                    last_chomp = suf
#                    continue
                else:
                    entry[tup[0]] = tup[1]
                    last_chomp = tup[2]
            chomp = lineiter.next()
    except StopIteration:
        pass

    if "first" not in entry or "last" not in entry:
        errors.append("%d %s INCOMPLETE \n%d %s\n%s" % (line_no+1, line, line_no+1, entry, addresses))
        continue
    lines.append("%d %s" % (line_no+1, entry))

for good in lines:
    print good

print "ERROR'D"
for error in errors:
    print error

llength = len(lines)
elength = len(errors)
blength = len(broken)
total = llength + elength + blength

print "good: %d" % (llength)
print "fixable: %d" % (elength)
print "broken: %d" % (blength)
print total
print "error rate: %f" % (float(blength+elength)/total)
