from sparqlparser.base import *
from sparqlparser.grammar import *

s = '( *Expression*)'

r = ArgList_p.parseString(s)

t = r[0]

print(type(t))
print()
print(t.getKeys())

u = t.arguments
print()
print(type(u))
print()
print(u.getKeys())

v = u.expression_list

print()
print(type(v))
print(v.getKeys())

w = t.arguments.expression_list

assert w == v

print(t.render())

s = '()'

a = ArgList_p.parseString(s)