# datatodb.py - converting the entries we parsed from our raw
# files into database entries

import sqlalchemy as sa
from entry import Entry, Line
from sqlalchemy import Table, Column, Integer, Boolean, String, MetaData
from sqlalchemy.orm import mapper

meta = MetaData()

addresses_table = Table('addresses', meta,
        Column('id', Integer, primary_key=True),
        Column('filepath', String),
        Column('line_no', Integer),
        Column('last', String),
        Column('first', String),
        Column('widowed', Boolean),
        Column('spouse', String),
        Column('married', Boolean),
        Column('prof', String),
        Column('business', String),
        Column('ownership', Boolean),
        Column('b_number', String(8)),
        Column('b_street', String),
        Column('b_strsuffix', String(5)),
        Column('b_nh', String),
        Column('number', String(8)),
        Column('street', String),
        Column('strsuffix', String(5)),
        Column('nh', String)
        )

errors_table = Table('errors', meta,
        Column('id', Integer, primary_key=True),
        Column('filepath', String),
        Column('line_no', Integer),
        Column('last', String),
        Column('first', String),
        Column('widowed', Boolean),
        Column('spouse', String),
        Column('married', Boolean),
        Column('prof', String),
        Column('business', String),
        Column('ownership', Boolean),
        Column('b_number', String(8)),
        Column('b_street', String),
        Column('b_strsuffix', String(5)),
        Column('b_nh', String),
        Column('number', String(8)),
        Column('street', String),
        Column('strsuffix', String(5)),
        Column('nh', String)
        )

broken_table = Table('broken', meta,
        Column('id', Integer, primary_key=True),
        Column('filepath', String),
        Column('line_no', Integer),
        Column('line', String)
        )
died_table = Table('died', meta,
        Column('id', Integer, primary_key=True),
        Column('filepath', String),
        Column('line_no', Integer),
        Column('line', String)
        )

engine = sa.create_engine("sqlite:///addr_data")
meta.bind = engine
meta.create_all()
mapper(Entry, addresses_table)
mapper(ErroredEntry, errors_table)
mapper(BrokenLine, broken_table)
mapper(DiedLine, died_table)
