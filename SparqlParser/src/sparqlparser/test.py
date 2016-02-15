from pyparsing import *
from sparqlparser.base import *

s = '"*Expression*"'

r = Expression_p.parseString(s)[0]

print(type(r))

r.dump()