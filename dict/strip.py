infile = open("Resident_List_2008_Aug.txt")
lnames = {}
for line in infile:
    lname = line.split()[0].capitalize()
    if lname not in lnames:
        lnames[lname] = True
infile.close()
outfile = open("2008lnames.txt", 'w')
lnames = lnames.keys()
for atom in lnames:
    outfile.write(atom + '\n')
outfile.close()
