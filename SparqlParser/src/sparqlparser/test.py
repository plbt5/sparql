from pyparsing import *
from sparqlparser.base import *
from sparqlparser.grammar import *


# [71]    ArgList   ::=   NIL | '(' 'DISTINCT'? Expression ( ',' Expression )* ')' 
# TODO
# l = ['()', '( *Expression*) ', '(*Expression*, *Expression*)', '(DISTINCT *Expression*,  *Expression*,   *Expression* )']
# 
# for s in l:
#     r = ArgList_p.parseString(s)[0]
#     r.dump()
#     print()
    
# s = '(DISTINCT *Expression*,  *Expression*,   *Expression* )'
#   
# r = ArgList_p.parseString(s)[0]
 
# s = 'DISTINCT'
# 
# r = DISTINCT_p.parseString(s)[0]
# r.dump()
# print()
# print(r.getName())
# print(r.getKeys())
# print(r.getValuesForKey('distinct'))
# print(r.getValuesForKey('expression_list'))
# print(r.distinct, type(r.distinct))
# print(r.expression_list)
# print(r.distinct.getName())
# print(r.distinct.getKeys())
# print(r.distinct.getItems())
# r.distinct.dump()
# r.expression_list.dump()

# s = '\\&'
# 
# r = PN_LOCAL_ESC_p.parseString(s)[0]

s = "'test' ^^ <test>"

r = RDFLiteral(s)

r.dump()

lf = r.lexical_form

lf.dump()

print(type(lf))

new_lexical_form = String("'test2'")

print(r.lexical_form.render())
r.lexical_form = new_lexical_form

print(r.render())