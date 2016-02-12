from pyparsing import *
from sparqlparser.base import *


# s = "'work' ^^<work>"
# 
# r = RDFLiteral(s)

s = 'a:z'
r = PrefixedName(s)
# r.test(render=True, dump=True)
rc = r.copy()
# rc.test(render=True, dump=True)

assert rc == r
    