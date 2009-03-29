import sys

def condense_lines(line, linelist):
    """
    Condenses a list of lines into one line. Strips hyphens
    and recondenses words, if split between lines. Otherwise
    simply appends the next line, inserting space.
    """
    try:
        line2 = linelist.pop(0)
        space = " "
        if line.endswith("-"):
            line = line[:len(line)-1]
            space = ""
        line = "%s%s%s" % (line, space, line2)
        condense_lines(line, linelist)
    except IndexError: pass
    return line


with open(sys.argv[1]) as infile:
    with open(sys.argv[2], 'w') as outfile:
        prev_line = ""
        condense = False
        for line in infile:
            line = line.strip()
            if condense:
                line = condense_lines(prev_line, [line])
                condense = False
            if line.endswith("-"):
                prev_line = line
                condense = True
                print prev_line
                #wait to write the line until we've condensed it
                continue
            outfile.write(line + '\n')

