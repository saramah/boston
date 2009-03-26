file = open("boston-streets.txt")
for line in file:
    print line.split()[0].capitalize()
