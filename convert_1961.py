import os
import re
import sys
from helpers import *

#builds the neigh_pattern to strip parens from it
def build_nhpat(path):
    infile = open(path)
    pattern = ""
    for line in infile:
        pattern += "|" + line.split(",")[0]
    infile.close()
    return pattern[1:]

neighborhoods = build_nhpat("dict/allnhabbr.txt")

def convert(path):
    outname = "1961/directory/data_converted/out" + path[20:]
    outfile = open(outname, 'w')
    with open(path) as infile:
        text = infile.read()
        for apt in re.findall(r'(?im)(\bAPT\s+(?:\d|A)+(?:\b|\n|\r)+)', text):
            text = text.replace(apt, " ")
#        for st in re.findall(r'(?i)\bst\b', text):
#            text = text.replace(st, "")
        for line in text.split("\r\n"):
            if line.startswith("\""):
                line = "\x97" + line[1:].strip()
            if line.isspace() or len(line) == 0:
                continue
            words = line.split()
            if len(words) == 1  and words[0].lower() in lnames:
                outfile.write(line.upper() + '\n')
                continue
            if re.search(r'(?i)\bdied\b', line):
                outfile.write(line + '\n')
                continue
            if re.search(r'(?i)\bsee\b', line):
                outfile.write(line + '\n')
                continue
            line = " ".join(words).title() + '\n'
            #condensing Mrs; only crops up in uppercase years
#            if re.search(r'Mr S', line):
#                line = line.replace('Mr S', 'Mrs')
            #splitting ownership details and house number
            for num in re.findall(r'(?i)\b(?:R|H)(?:\d|I|l|S|O)+\b', line):
                if translate(num[1:]).isdigit():
                    line = line.replace(num, "%s %s" % (num[0].lower(), translate(num[1:])))
            #removing neighborhood from parens
            nh_pattern = r'(?i)((?:\(|<|C)\s*(%s|0)\s*(?:\)|>))' % neighborhoods
            for num in re.findall(nh_pattern, line):
                nh = num[1]
                if nh == "0":
                    nh = "D"
#                if nh.lower() in nhabbr:
#                    nh = nhabbr[nh.lower()]
                line = line.replace(num[0], nh)
            if line.isspace():
                continue
            outfile.write(line)        
    outfile.close()

if __name__ == "__main__":
    directory = "1961/directory/data"
    filepaths = []
    if os.path.isdir(directory):
        filepaths = os.listdir(directory)
        filepaths = sorted(map((lambda x: directory + "/" + x), filepaths))
    elif os.path.isfile(directory):
        filepaths.append(directory)
    else:
        raise NotImplementedError
    count = 0
    for infile in filepaths:
        count += 1
        if count % 100 == 0:
            print count
        convert(infile)
