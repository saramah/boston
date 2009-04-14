from __future__ import with_statement

import os, os.path
import re
import sys
import preprocessor

from helpers import *

def parse(directory):
    """
    Takes a directory of Boston Directory files (1955) and returns a
    4-tuple composed of fully parsed lines, partially parsed lines, 
    unparsed errored lines, and unparsed death lines.

    (lines, errors, broken, died)
    """
    #lines - parsed without errors
    #errors - partially parsed with fixable errors
    #broken - unparsed with known dirty data
    #died - unparsed, names of deceased with dates
    lines, errors, broken, died = [], [], [], []
    last_name = lname_marker[0] 
    #lname_index - keeps track of the index of the lastname
    #we're currently on so we don't have to recalculate it
    #every time
    lname_index = 0
    filepaths = []

    if os.path.isdir(directory):
        filepaths = os.listdir(directory)
        filepaths = sorted(map((lambda x: directory+ "/" + x), filepaths))
    elif os.path.isfile(directory):
        filepaths.append(directory)
    else:
        raise NotImplementedError

    for infile in filepaths:
        #preprocess the file before we start parsing it
        preprocessed = preprocessor.process(infile)

        with open("out", 'a') as outfile:
            for x in preprocessed:
                outfile.write(x)

        #getting down to the actual parsing
        for line_no, line in enumerate(preprocessed):
            line = line.strip()
            count = -1
            #if a line has invalid characters in it, we're not dealing with it.
            #XXX wishlist: hook in a levenshtein distance calculator to fix
            #words with invalid characters.
            if find_errors(line):
                broken.append({'filepath':infile, 'line_no':line_no, 'line':line.strip()})
                continue
            #stripping out death lines, these don't contain addresses
            if re.search(r'\bdied\b', line):
                died.append({'filepath':infile, 'line_no':line_no, 'line':line.strip()})
                continue
            #some lastname headers have form "Cohig see Cohen, Cofen" etc
            #this just takes the first part of that line.
            if re.search(r'\bsee\b', line):
                split_line = line.split()
                potential_lname = ""
                for bit in split_line:
                    if bit == "see":
                        break
                    potential_lname += bit.lower()
                potential_lname = potential_lname.capitalize()
                if potential_lname.lower() not in lnames:
                    broken.append({'filepath':infile, 'line_no':line_no, 'line':line.strip(), 'reason':'bad jump'})
                    continue
                if valid_jump(last_name, potential_lname):
                    dist = distance(lname_index, potential_lname.lower())
                    if dist != -1:
                        last_name = potential_lname
                        lname_index += dist
                    else:
                        broken.append({'filepath':infile, 'line_no':line_no, 'line':line.strip(), 'reason':'bad jump'})
                else:
                    broken.append({'filepath':infile, 'line_no':line_no, 'line':line.strip(), 'reason':'bad jump'})
                continue

            entry = {}
            entry['filepath'] = infile
            entry['line_no'] = line_no
            lineiter = line.split().__iter__()
            last_chomp = -1
            try:
                chomp = lineiter.next()
                count += 1
                #we've got a subentry, so we should have the
                #last name from the last line
                if chomp.startswith("\x97"):
                    first = chomp[1:].lower()
                    first = first.replace("\x97", "")
                    if first in nameabbr:
                        first = nameabbr[first]
                    entry["first"] = first.capitalize()
                    entry["last"] = last_name
                #if line starts with a last name, then grab the
                #first name after it as well
                elif chomp.lower() in lnames:
#            print "%d %s from\n%s" % (line_no+1, chomp, line)
                    chomp = chomp.capitalize()
                    #if the line was misread by OCR or if the lastname is multiple
                    #words not connected by a hyphen, then grab the rest of it
                    if chomp == "Co" or chomp == "De" or chomp == "Di" or chomp == "O":
                        plname = chomp 
                        for atom in line.split()[1:]:
                            plname += atom.lower()
                            if plname in lnames:
                                chomp = plname
                                break
                    if valid_jump(last_name, chomp):
                        dist = distance(lname_index, chomp.lower())
                        if dist != -1:
                            #XXX neighborhood/lastname clashes
                            if chomp.lower() in nhabbr:
                                pass
                            else:
                                last_name = chomp
                                lname_index += dist
                        else:
                            broken.append({'filepath':infile, 'line_no':line_no, 'line':line.strip(), 'reason':'bad jump'})
                    else:
                        broken.append({'filepath':infile, 'line_no':line_no, 'line':line.strip(), 'reason':'bad jump'})
                        continue
                    
                    chomp = lineiter.next()
                    count += 1

                    first = chomp.lower()
                    if first in nameabbr:
                        entry["first"] = nameabbr[first].capitalize()
                    elif first in fnames:
                        entry["first"] = first.capitalize()
                    else:
                        broken.append({'filepath':infile, 'line_no':line_no, 'line':line.strip(), 'reason':'unrecognized first name'})
                        continue
                    entry["last"] = last_name
                #if it's not a lastname or a subentry, then it's a line
                #we should have handled in our preprocessor; mark it.
                else:
                    broken.append({'filepath':infile, 'line_no':line_no, 'line':line.strip(), 'reason':'bad prefix'})
                    continue

                chomp = lineiter.next()
                count += 1
            
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
                    #first name initial
                    elif tup[2] == INITIAL:
                        entry[tup[0]] += " " + tup[1]
                    #spousal entry
                    elif tup[2] == SPOUSE:
                        while not chomp.endswith(")"):
                            chomp += " " + lineiter.next()
                            count += 1
                        name = tup[1].capitalize()
                        if name.lower() in nameabbr:
                            name = nameabbr[name.lower()].capitalize()
                        elif name.lower() in fnames:
                            if "spouse" in entry:
                                entry["spouse"] += " " + chomp.strip("()")
                            else:
                                entry["spouse"] = chomp.strip("()")
                        else:
                            business = chomp.strip("()")
                            entry["business"] = business
                    #widowed entry; deceased's name optionally follows
                    elif tup[2] == WIDOWED:
                        entry[tup[0]] = tup[1]
                        chomp = lineiter.next()
                        count += 1
                        if chomp.lower() in nameabbr:
                            chomp = nameabbr[chomp.lower()]
                        if chomp.lower() in fnames:
                            entry["spouse"] = chomp.capitalize()
                        else: continue
                    #we've hit the address section, finish up with everything in
                    #parse_addr
                    elif tup[2] is OWNER or tup[2] == HOUSE_NUM or chomp.lower() in streets:
#                addresses = parse_addr(line)
#                print "dummy bit " + " ".join(line.split()[count:])
                        addresses = parse_addr("dummy bit " + " ".join(line.split()[count:]))
#                print "%d %s\n%s" % (line_no+1, line.strip(), addresses)
                        if addresses is None:
                            break
                        entry.update(addresses)
                        break
                    else:
                        entry[tup[0]] = tup[1]
                        last_chomp = tup[2]
                    chomp = lineiter.next()
                    count += 1
            except StopIteration:
                pass

            if "first" not in entry or "last" not in entry or "street" not in entry:
                entry['reason'] = 'incomplete'
                errors.append(entry)
                continue
            lines.append(entry)

    return (lines, errors, broken, died)
