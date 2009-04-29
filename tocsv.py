import sys
import bparser
from helpers import *

year = sys.argv[1]

lines, errors, broken, died = bparser.parse('%s/directory/data_converted' % (year))
#lines, errors, broken, died = bparser.parse('test/front')
print "good:%d errord:%d broken:%d" % (len(lines), len(errors), len(broken))
for error in errors:
    print error

for broke in broken:
    print broke


outfile_boston = open("%s_boston_res.csv" % (year), 'w')
outfile_nonboston = open("%s_nonboston_res.csv" % (year), 'w')

for line in lines:
    towrite = "%s,%s," % (line['last'], line['first'])
    if 'number' in line:
        towrite += line['number']
    towrite = "%s,%s,%s,%s,%s" % (towrite, line['street'], line['strsuffix'], line['nh'], line['filepath'][30:])
    if line['nh'].lower() in boston_nh: 
        outfile_boston.write(towrite + '\n')
    else:
        outfile_nonboston.write(towrite + '\n')


outfile_boston.close()
outfile_nonboston.close()
