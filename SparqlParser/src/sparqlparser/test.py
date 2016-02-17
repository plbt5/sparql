from pyparsing import *
from sparqlparser.base import *


# s = '?test'
# 
# r = PathMod_p.parseString(s)[0]
# 
# r.dump()
s1 = '<t>'
 
s2a = ' $a'
s2b = ' ?a'
 
s12a = s1 + ' ' + s2a
s12b = s1 + ' ' + s2b
 
PropertyListPathNotEmpty_p<< ( VerbPath_p | VerbSimple_p ) + ObjectListPath_p +  ZeroOrMore( SEMICOL_p + Optional( ( VerbPath_p | VerbSimple_p ) + ObjectList_p ) )
 
p1 = PropertyListPathNotEmpty_p.parseString('<test> ?test') 

p1[0].dump()