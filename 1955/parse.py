import re
import sys
import preprocessor

from helpers import *


lines, errors, broken, died = [], [], [], []
last_name = ""
last_entry = {}

#preprocess the file before we start parsing it
preprocessed = preprocessor.process(sys.argv[1])

for line_no, line in enumerate(preprocessed):
    line = line.strip()
    num_addr = num_addresses(line)
    if re.search(r'\bdied\b', line):
        died.append("%d %s lastname: %s" % (line_no+1, line, last_name))
        continue
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
    if find_errors(line):
        broken.append("%d %s INVALID CHARS" % (line_no+1, line))
        continue
    if len(num_addr) > 2:
        errors.append("%d %s EXCESS NUMBERS" % (line_no+1, line))

    entry = {}
    lineiter = line.split().__iter__()
    last_chomp = -1
    try:
        chomp = lineiter.next()
        #if line starts with a last name, then grab the
        #first name after it as well
        if chomp.capitalize() in lnames:
            chomp = chomp.capitalize()
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
            if len(first) is 1:
                last_chomp = ini
            else:
                last_chomp = fir
        #if it's not a lastname or a subentry, then it's a line
        #we should have handled in our preprocessor; mark it.
        if last_chomp is -1:
            errors.append("%d %s BAD PREFIX" % (line_no+1, line))
            continue

        chomp = lineiter.next()
        entry["nh"] = "Boston"
        entry["street"] = "St"
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
                if tup[2] is ini:
                    entry[tup[0]] += " " + tup[1]
                    last_chomp = ini
                #spousal entry
                elif tup[2] is spo:
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
                elif tup[2] is wid:
                    entry[tup[0]] = tup[1]
                    chomp = lineiter.next().capitalize()
                    if chomp in nameabbr:
                        chomp = nameabbr[chomp]
                    if chomp in fnames:
                        entry["spouse"] = chomp
                    else: continue
                    last_chomp = wid
                #we hit a street address
                elif tup[2] is num:
                    street = "street"
                    strsuffix = "strsuffix"
                    if tup[1] in num_addr and len(num_addr) is 2 and num_addr.index(tup[1]) is 0:
                        entry["b_number"] = tup[1]
                        entry["b_strsuffix"] = "St"
                        street = "b_street"
                        strsuffix = "b_strsuffix"
                    else:
                        entry["number"] = tup[1]
                    #grab the street name
                    chomp = lineiter.next()
                    if chomp.capitalize() in strabbr:
                        chomp = strabbr[chomp.capitalize()]
                    entry[street] = chomp
                    if chomp not in streets:
                        while entry[street] not in streets:
                            chomp = lineiter.next()
                            tup = recognize(chomp)
                            if tup is not None:
                                entry[tup[0]] = tup[1]
                                last_chomp = tup[2]
                                break
                            entry[street] += " " + chomp
                    chomp = lineiter.next()
                    tup = recognize(chomp)
                    if tup is not None and tup[2] is suf:
                        entry[strsuffix] = tup[1]
                    else: continue
                else:
                    entry[tup[0]] = tup[1]
                    last_chomp = tup[2]
            chomp = lineiter.next()
    except StopIteration:
        pass

    if "first" not in entry or "last" not in entry or "street" not in entry:
        errors.append("%d %s INCOMPLETE \n%d %s" % (line_no+1, line, line_no+1, entry))
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
