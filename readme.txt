THE PROBLEM
We have a metric shitton of data (~30GB) which needs to be parsed
into machine readable (and manipulable) format. The data is based
from the Boston Directory, 1955-1975, which contains a directory
listing of names, addresses, and other miscellaneous data (including
deaths, marital status, profession, and employer) which are less
important to analyze, but we'd like to hold on to for future use
of said data.

The data comes from OCR ouput of jpg files gotten from the Internet
Archive. OCR is great, but there remain some artifacts in the plain
text output that we have to maneuver around. Once we get the well-
formatted lines parsed, then we want to tackle correcting some of
those artifacts and extracting information from the error'd lines.

WHAT WE WANT
From this data, we want to acquire a database from which we can
draw location and name data, at the very least. This will be used
to map a name to a location on a map in a Google Maps application,
yet to be built. The ultimate goal is to be able to track names
in a neighborhood over time and from that infer ethnic migration
patterns in Boston from 1955 to 1975.

SAMPLE LINES FROM OCR OUTPUT
Coltun Harry (Flynn. Abrams, Coltun & Flynn) lwyr
r 70 Fremont Chel
Colucci Arth P (Sally M) clo cln 241 Meridian EB h
6 Everett do
<97>Carl J (Lillian M) barber h 144 StAndrew rd EB
<97>Carmela Mrs h 37 Cooper
<97>Concetta Mrs died Nov 14, 1954                                          
<97>Geo E (Florence) barber 245 Meridian EB h 242
79 Old Colony av SB

DESIRED OUTPUT FROM SAMPLE

{'70 Fremont St, Chelsea':{'last':'Colton', 'first':'Harry',
 'emp':'Flynn. Abrams, Coltun & Flynn', 'prof':'lwyr',
 'marital':'r', 'number':'70', 'street':'Fremont St',
 'nh':'Chelsea'}, 
 '241 Meridian St, East Boston':{'last':'Colucci',
 'first':'Arthur P', 'spouse':'Sally M', 'prof':'clo cln',
 'empaddr':'241 Meridian EB', 'marital':'h', 'number':'6',
 'street':'Everett', 'nh':'Dorchester'
 ...
 ...etc.}


