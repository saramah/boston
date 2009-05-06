import re

infile = open("suffolk-streets.txt")
outfile = open("outsuff.txt", 'w')
for line in infile:
    line = line.strip()
    if line.isspace():
        continue
    outfile.write(" ".join(line.split()[:len(line.split())-1]) + '\n')
infile.close()
outfile.close()
