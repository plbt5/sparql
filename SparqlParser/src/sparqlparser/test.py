from pyparsing import *
from sparqlparser.base import *


r = PN_LOCAL_ESC('\\&')
r.dump()
x = r.copy()
assert x == r
        
    