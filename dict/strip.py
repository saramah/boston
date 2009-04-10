import re

infile = open("1955streets.txt")
outfile = open("1955streetsout.txt", 'w')
for line in infile:
    line = line.strip()
    if line.isspace():
        continue
    if line.isdigit():
        continue
    if re.search(r'\d+-\d+', line):
        continue
    print line
    outfile.write(line + '\n')
infile.close()
outfile.close()
