file = open("lastnames.txt")
for line in file:
    print line.split()[0].capitalize()
