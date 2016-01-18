from sparqlparser.base import *
from sparqlparser.grammar import *

s = '( *Expression*)'

r = ArgList_p.parseString(s)

t = ParseInfo(r)

print(t.render())
print()
dumpParseInfo(t)
print()
print(type(t))

