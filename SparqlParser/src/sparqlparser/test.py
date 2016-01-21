from sparqlparser.base import *
from sparqlparser.grammar import *

s = '( *Expression*)'
t1 = ArgList_p.parseString(s)[0]
print()
# print(t1.getKeys())
print()
t2 = ArgList(s)

assert t1.pattern == t2.pattern
print('equal?', t1 == t2)

print(t2.render())
print()
dumpParseInfo(t2)
print()
# print()
# print(t2.arguments.expression_list.render())
e = ExpressionList('*Expression*, *Expression*')
t2.arguments.expression_list = e
print(t2.render())
print()
dumpParseInfo(t2)

print('equal?', t1 == t2)

# print(t2.getKeys())
# print(t.parseinfo.__dict__.keys())
# print(t.parseinfo.namedtokens.__dict__.keys())
# 
# print(type(t))
# print()
# print(t.getKeys())
# 
# u = t.arguments
# print()
# print(type(u))
# print()
# print(u.getKeys())
# 
# v = u.expression_list
# 
# print()
# print(type(v))
# print(v.getKeys())
# 
# w = t.arguments.expression_list
# 
# assert w == v
# 
# print(t.render())
# 
# s = '()'
# 
# a = ArgList_p.parseString(s)