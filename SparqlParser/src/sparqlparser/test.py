from pyparsing import *
from sparqlparser.base import *
from sparqlparser.grammar import *
from sparqlparser.grammar_functest import printResults

l = ['NOT Exists *GroupGraphPattern*']
# printResults(l, 'GroupGraphPattern')

r = NOT_p.parseString('NOT')
r = (NOT_p + EXISTS_p).parseString('NOT EXISTS')
r = (NOT_p + EXISTS_p + GroupGraphPattern_p).parseString('NOT EXISTS *GroupGraphPattern*')
# r = GroupGraphPattern_p.parseString(l[0])