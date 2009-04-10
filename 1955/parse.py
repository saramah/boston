from __future__ import with_statement

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

    addresses = parse_addr(line)
    if addresses is None:
        errors.append("%d %s NO ADDRESS" % (line_no+1, line))
        continue

    entry = {}
    lineiter = line.split().__iter__()
    last_chomp = -1
    try:
        chomp = lineiter.next()
        #if line starts with a last name, then grab the
        #first name after it as well
        if chomp.lower() in lnames:
#            print "%d %s from\n%s" % (line_no+1, chomp, line)
            chomp = chomp.capitalize()
            #if the line was misread by OCR or if the lastname is multiple
            #words not connected by a hyphen, then grab the rest of it
            #XXX this necessarily kills entries with lastnames that are 
            #only the short chomps.
            if chomp == "Co" or chomp == "De" or chomp == "O":
                plname = ""
                for atom in line.split()[1:]:
                    chomp += atom.lower()
                    if plname in lnames:
                        break
                if plname.lower() not in lnames:
                    errors.append("%d %s UNRECOGNIZED LAST NAME" % (line_no+1, line))
                    continue
            if valid_jump(last_name, chomp):
                last_name = chomp
                last_chomp = LAST_NAME 
            else:
                broken.append("%d %s BAD JUMP" % (line_no+1, line))
                continue
            
            chomp = lineiter.next()

            first = chomp.lower()
            if first in nameabbr:
                entry["first"] = nameabbr[first].capitalize()
            elif first in fnames:
                entry["first"] = first.capitalize()
            else:
                errors.append("%d %s UNRECOGNIZED NAME" % (line_no+1, line))
                continue
            entry["last"] = last_name
            last_chomp = LAST_NAME
        #otherwise we've got a subentry, so we should have the
        #last name from the last line
        elif chomp.startswith("\x97"):
            first = chomp[1:].lower()
            if first in nameabbr:
                first = nameabbr[first]
            entry["first"] = first.capitalize()
            entry["last"] = last_name
            last_chomp = FIRST_NAME
        #if it's not a lastname or a subentry, then it's a line
        #we should have handled in our preprocessor; mark it.
        if last_chomp == -1:
            errors.append("%d %s BAD PREFIX" % (line_no+1, line))
            continue

        chomp = lineiter.next()
    
        entry["nh"] = "Boston"
        entry["strsuffix"] = "St"

        entry.update(addresses)

        #handling everything else.
        while True:
            tup = recognize(chomp)
            if tup is None:
                if chomp.lower() in streets:
                    break             
                if "prof" in entry:
                    entry["prof"] += " " + chomp
                else:
                    entry["prof"] = chomp
            #first name initial
            elif tup[2] == INITIAL:
                entry[tup[0]] += " " + tup[1]
            #spousal entry
            elif tup[2] == SPOUSE:
                while not chomp.endswith(")"):
                    chomp += " " + lineiter.next()
                chomp = tup[1].capitalize()
                if chomp.lower() in nameabbr:
                    chomp = nameabbr[chomp.lower()].capitalize()
                elif chomp.lower() in fnames:
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
                    continue
            #widowed entry; deceased's name optionally follows
            #XXX still not working quite right
            elif tup[2] == WIDOWED:
                entry[tup[0]] = tup[1]
                chomp = lineiter.next()
                if chomp.lower() in nameabbr:
                    chomp = nameabbr[chomp.lower()]
                if chomp.lower() in fnames:
                    entry["spouse"] = chomp.capitalize()
                else: continue
            #we've hit the address section, finish up with everything in
            #parse_addr
            elif tup[2] == HOUSE_NUM:
                break
            else:
                entry[tup[0]] = tup[1]
                last_chomp = tup[2]
            chomp = lineiter.next()
    except StopIteration:
        pass

    if "first" not in entry or "last" not in entry or "street" not in entry:
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
