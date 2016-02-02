from pyparsing import *
from sparqlparser.base import *
from sparqlparser.grammar import *

s = '\\&'

r = PN_LOCAL_ESC_p.parseString(s)[0]

print(type(r))

r.dump()