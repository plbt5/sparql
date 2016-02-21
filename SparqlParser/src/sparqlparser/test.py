from pyparsing import *
from sparqlparser.grammar import *


s = '?S <testIri> ?S . "TriplesBlock" @en-bf <TriplesBlock> ?TriplesBlock ; <v> TriplesBlock, (TriplesBlock) ;;'

r1 = TriplesBlock_p.parseString(s)[0]
  
r1.dump()
r1.test(render=True)
# print()

print(r1)

t = '"work" @en-bf <test> ?path ; <test2> $algebra, ($TriplesNode) ;;'

