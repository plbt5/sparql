from pyparsing import *
from sparqlparser.base import *


# s = "'work' ^^<work>"
# 
# r = RDFLiteral(s)

# Aword_p = Word(alphas)
# class Aword(SPARQLTerminal):
#     def assignPattern(self):
#         return eval(self.__class__.__name__ + '_p')
# Aword_p.setParseAction(parseInfoFunc(Aword))


s = 'algebra'

r = Aword(s)

r.dump()




    