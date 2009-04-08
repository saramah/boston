file = open("boston-streets.txt")
for line in file:
    x = ""
    for atom in line.split()[:-1]:
        if atom == "St":
            x += atom
        else:
            x += atom + " "
    print x.strip()
