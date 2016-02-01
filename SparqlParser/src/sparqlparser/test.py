from pyparsing import *
from sparqlparser.base import *
from sparqlparser.grammar import *

# [137]   PrefixedName      ::=   PNAME_LN | PNAME_NS 
l = ['aA:Z.a', 'Z.8:AA', 'aA:', 'Z.8:', ':']

f = parseInfoFunc('PrefixedName')

for s in l:
    r = PrefixedName_p.parseString(s)
    print(r[0].__dict__)


    