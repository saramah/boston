#helper classes for mapping our data with sqlalchemy

class Entry(object):
#    def __init__(self, filepath, line_no, last, first, widowed, spouse, married, prof, business, ownership, b_number, b_street, b_strsuffix, b_nh, number, street, strsuffix, nh):
#        self.filepath = filepath
#        self.line_no = line_no
#        self.last = last
#        self.first = first
#        self.widowed = widowed
#        self.spouse = spouse
#        self.married = married
#        self.prof = prof
#        self.business = business
#        self.ownership = ownership
#        self.b_number = b_number
#        self.b_street = b_street
#        self.b_strsuffix = b_strsuffix
#        self.b_nh = b_nh
#        self.number = number
#        self.street = street
#        self.strsuffix = strsuffix
#        self.nh = nh

    def __str__(self):
        return "%s %s %d %s %s %s" % (self.last, self.first, self.number, self.street,
                self.strsuffix, self.nh)

    def __cmp__(self, other):
        return cmp((self.last+" "+self.first), (other.last+" "+other.first))

class ErroredEntry(object):
#    def __init__(self, filepath, line_no, last, first, widowed, spouse, married, prof, business, ownership, b_number, b_street, b_strsuffix, b_nh, number, street, strsuffix, nh):
#        self.filepath = filepath
#        self.line_no = line_no
#        self.last = last
#        self.first = first
#        self.widowed = widowed
#        self.spouse = spouse
#        self.married = married
#        self.prof = prof
#        self.business = business
#        self.ownership = ownership
#        self.b_number = b_number
#        self.b_street = b_street
#        self.b_strsuffix = b_strsuffix
#        self.b_nh = b_nh
#        self.number = number
#        self.street = street
#        self.strsuffix = strsuffix
#        self.nh = nh

    def __str__(self):
        return "%s %s %d %s %s %s" % (self.last, self.first, self.number, self.street,
                self.strsuffix, self.nh)

    def __cmp__(self, other):
        return cmp((self.last+" "+self.first), (other.last+" "+other.first))

class DiedLine(object):
#    def __init__(self, filepath, line_no, line):
#        self.filepath = filepath
#        self.line_no = line_no
#        self.line = line

    def __str__(self):
        return "%d %s" % (self.line_no, self.line)

    def __cmp__(self, other):
        if self.filepath == other.filepath:
            return cmp(self.line_no, other.line_no)
        else:
            return cmp(self.filepath, other.filepath)

class BrokenLine(object):
#    def __init__(self, filepath, line_no, line):
#        self.filepath = filepath
#        self.line_no = line_no
#        self.line = line

    def __str__(self):
        return "%d %s" % (self.line_no, self.line)

    def __cmp__(self, other):
        if self.filepath == other.filepath:
            return cmp(self.line_no, other.line_no)
        else:
            return cmp(self.filepath, other.filepath)
