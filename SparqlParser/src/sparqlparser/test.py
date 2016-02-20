from pyparsing import *
from sparqlparser.grammar import *


s = 'BIND ( 123 AS ?S )'

r1 = Bind(s)
  
r1.dump()
r1.test(render=True)
print()

