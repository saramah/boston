# datatodb.py - converting the entries we parsed from our raw
# files into database entries

import parser
import sqlalchemy as sa
from entry import Entry, ErroredEntry, BrokenLine, DiedLine
from sqlalchemy import Table, Column, Integer, Boolean, Unicode, MetaData
from sqlalchemy.orm import mapper, sessionmaker

meta = MetaData()

addresses_table = Table('addresses', meta,
        Column('id', Integer, primary_key=True),
        Column('filepath', Unicode),
        Column('line_no', Integer),
        Column('last', Unicode),
        Column('first', Unicode),
        Column('widowed', Boolean),
        Column('spouse', Unicode),
        Column('married', Boolean),
        Column('prof', Unicode),
        Column('business', Unicode),
        Column('ownership', Boolean),
        Column('b_number', Unicode(8)),
        Column('b_street', Unicode),
        Column('b_strsuffix', Unicode(5)),
        Column('b_nh', Unicode),
        Column('number', Unicode(8)),
        Column('street', Unicode),
        Column('strsuffix', Unicode(5)),
        Column('nh', Unicode)
        )

errors_table = Table('errors', meta,
        Column('id', Integer, primary_key=True),
        Column('filepath', Unicode),
        Column('line_no', Integer),
        Column('last', Unicode),
        Column('first', Unicode),
        Column('widowed', Boolean),
        Column('spouse', Unicode),
        Column('married', Boolean),
        Column('prof', Unicode),
        Column('business', Unicode),
        Column('ownership', Boolean),
        Column('b_number', Unicode(8)),
        Column('b_street', Unicode),
        Column('b_strsuffix', Unicode(5)),
        Column('b_nh', Unicode),
        Column('number', Unicode(8)),
        Column('street', Unicode),
        Column('strsuffix', Unicode(5)),
        Column('nh', Unicode),
        Column('reason', Unicode)
        )

broken_table = Table('broken', meta,
        Column('id', Integer, primary_key=True),
        Column('filepath', Unicode),
        Column('line_no', Integer),
        Column('line', Unicode),
        Column('reason', Unicode)
        )
died_table = Table('died', meta,
        Column('id', Integer, primary_key=True),
        Column('filepath', Unicode),
        Column('line_no', Integer),
        Column('line', Unicode),
        )

engine = sa.create_engine("sqlite:///addr_data.db")
meta.bind = engine
meta.create_all()
mapper(Entry, addresses_table)
mapper(ErroredEntry, errors_table)
mapper(BrokenLine, broken_table)
mapper(DiedLine, died_table)
Session = sessionmaker(bind=engine)
session = Session()

lines, errors, broken, died = parser.parse("select")

for atom in lines:
    entry = Entry()
    for attr in atom:
        setattr(entry, attr, unicode(atom[attr]))
    session.add(entry)
session.commit()

for atom in errors:
    entry = ErroredEntry()
    for attr in atom:
        setattr(entry, attr, unicode(atom[attr]))
    session.add(entry)
session.commit()

for atom in broken:
    entry = BrokenLine()
    for attr in atom:
        setattr(entry, attr, unicode(atom[attr]))
    session.add(entry)
session.commit()

for atom in broken:
    entry = DiedLine()
    for attr in atom:
        setattr(entry, attr, unicode(atom[attr]))
    session.add(entry)
session.commit()

session.close()
