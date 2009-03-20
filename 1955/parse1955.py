# 1 name per line
# <97> at beginning of line
# 

import re

class Person(object):
    def __init__(self, first, last, number, street, nh):
        first = self.first
        last = self.last
        number = self.number
        street = self.street
        neighborhood = self.nh

    def __str__(self):
        return self.first + " " + self.last

lines = []
errors = []
last = ""
line_number = 0


try:
    file = open("sample_1955.txt")
    for line in file:
        line_number = line_number + 1
        if line.isupper():
            last = line.strip().capitalize()
            continue
        elif line.startswith("\x97"):
            first = line.split()[0][4:].capitalize()
            lines.append(first + " " + last)
        #error'd line
        else:
            errors.append(str(line_number) + " " + line.strip())
    file.close()
except IOError:
    print "gah!"

print lines
print "ERROR'D"
for xx in errors:
    print xx
