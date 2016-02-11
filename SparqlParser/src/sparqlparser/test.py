from pyparsing import *
from sparqlparser.base import *
from sparqlparser.grammar import *

print(PN_LOCAL_ESC.__name__)

r = PN_LOCAL_ESC('\\&')

class A:
    pattern = __name__
    def printName(self): print(self.__class__.pattern)
    
x = A()
x.printName()
    