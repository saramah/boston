# at most 1 name per line
# <97> at beginning of line, though not always
# [lastname] firstname [initial] [(wifename)] [profession] [marital status] number streetname [neighborhood]
# 


class Person(object):
    def __init__(self, first, last, spouse, prof, number, street, nh):
        first = self.first
        last = self.last
        spouse = self.spouse
        prof = self.prof
        number = self.number
        street = self.street
        neighborhood = self.nh

    def __str__(self):
        return self.first + " " + self.last

class Company(object):
    def __init__(self, name, number, street, nh):
        name = self.name
        number = self.number
        street = self.street
        neighborhood = self.nh

    def __str__(self):
        return self.name

lines = []
errors = []
last = ""
line_number = 0
prev_line = ""

#####build dictionaries
#last names, male/female first names, streets, neighborhoods
#neighborhood abbreviations, name abbreviations
lnames = []
with open("../dict/lastnames.txt") as infile:
    for line in enumerate(infile):
        lnames.append(line[1].strip())

mnames = []
with open("../dict/mfirst.txt") as infile:
    for line in enumerate(infile):
        mnames.append(line[1].strip())

fnames = []
with open("../dict/ffirst.txt") as infile:
    for line in enumerate(infile):
        fnames.append(line[1].strip())

nameabbr = {}
with open("../dict/firstabbr.txt") as infile:
    for line in enumerate(infile):
        pair = line[1].strip().split()
        key, value = pair[0], pair[1]
        nameabbr[key] = value

streets = []
with open("../dict/boston-streets.txt") as infile:
    for line in enumerate(infile):
        streets.append(line[1].strip())

nhoods = []
with open("../dict/neighborhoods.txt") as infile:
    for line in enumerate(infile):
        nhoods.append(line[1].strip())

neighabbr = {}
with open("../dict/neighabbr.txt") as infile:
    for line in enumerate(infile):
        pair = line[1].strip().split()
        key, value = pair[0], pair[1]
        neighabbr[key] = value

#####the actual parsing
with open("sample_1955.txt") as infile:
    for line_number, line in enumerate(infile):
        line = line.split()
        if len(line) < 1:
            continue
        #normal line, start of entry (last name header)
        if line[0].startswith("\x97"):
            first = line[0][4:].capitalize()
            #expand abbreviations
            try:
                if nameabbr[first]:
                    first = nameabbr[first]
            except KeyError:
                pass
            lines.append(first + " " + last)
        #last name header
        elif line[0].isupper():
            last = line[0].strip().capitalize()
        #singleton last name/alt multiple lastname, first entry
        elif lnames.__contains__(line[0]):
            last = line[0]
            first = nameabbr[line[1]] or line[1]
            if len(first) is 1 or len(line[2]) is 1:
                first = first + " " + line[2]
            lines.append(first + " " + last)
        #error'd line
        else:
            errors.append(str(line_number) + " " + line[0])
        prev_line = line

print lines
print "ERROR'D"
for xx in errors:
    print xx
