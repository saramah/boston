cat 1955streets.txt|perl -ne 'print "$1\n" if /^\s+([A-Z][a-zA-Z\s]+)\s+(?:pk\.|pi\.|rd\.|ct\.|av\.|st\.|circle),\s/i;' | egrep '^[A-Z]' | sort | uniq > 1955streets.parsed.txt
