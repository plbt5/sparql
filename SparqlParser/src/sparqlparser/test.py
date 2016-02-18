from pyparsing import *
from sparqlparser.grammar import *


s = '?S Âꝷ﫜: ?S . '#?ConstructTriples'
s = '?ConstructTriples a $var'
r1 = TriplesSameSubject(s)

r1.dump()

print()

# r2 = ConstructTriples(s)
# 
# r2.dump()