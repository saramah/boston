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
outfile_boston_complete = open("%s_boston_complete.csv" % (year), 'w')
outfile_nonboston_complete = open("%s_nonboston_complete.csv" % (year), 'w')

#compressed files
#last,first,number,street,strsuffix,nh,filepath

#full files
#last,first,number,street,strsuffix,nh,owner,b_number,b_street,b_strsuffix,b_nh,b_owner,prof,business,married,widowed,spouse,filepath

keys = ['owner','b_number','b_street','b_strsuffix','b_nh','b_owner','prof','business','married','widowed','spouse','filepath']

for line in lines:
    towrite = "%s,%s," % (line['last'], line['first'])
    if 'number' in line:
        towrite += line['number']
    towrite = "%s,%s,%s,%s" % (towrite, line['street'], line['strsuffix'], line['nh'])
    if line['nh'].lower() in boston_nh: 
        outfile_boston.write(towrite + "," + line['filepath'][30:] + '\n')
    else:
        outfile_nonboston.write(towrite + line['filepath'][30:] + '\n')
    for key in keys:
        value = ""
        if key in line:
            value = key + " " + line[key].__repr__()
        towrite += "," + value
    if line['nh'].lower() in boston_nh: 
        outfile_boston_complete.write(towrite + "," + line['filepath'][30:] + '\n')
    else:
        outfile_nonboston_complete.write(towrite + line['filepath'][30:] + '\n')

outfile_boston.close()
outfile_nonboston.close()
outfile_boston_complete.close()
outfile_nonboston_complete.close()
