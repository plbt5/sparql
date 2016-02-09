from pyparsing import *
from sparqlparser.base import *
from sparqlparser.grammar import *

# setup

s = "'test' ^^<test>"

r = RDFLiteral(s)
p = RDFLiteral_p.parseString(s)[0]
q = RDFLiteral(s)
# test render functie

assert r.render() == "'test' ^^ <test>" 
 
# test init van ParseInfo (twee manieren) geeft hetzelfde resultaat
 
assert r == p
assert r.render() == p.render()
 
# test dot access (read)
 
assert r.lexical_form.render() == "'test'"

# test dot access (write)
 
p.lexical_form.lexical_form = STRING_LITERAL1("'test'")
assert p.lexical_form.render() == "'test'"
assert p.render() == "'test' ^^ <test>"
assert p.isValid()
assert r == p

q.lexical_form = STRING_LITERAL1("'test'")
assert q.lexical_form.render() == "'test'"
assert q.render() == "'test' ^^ <test>"
assert q.isValid()
assert not r == q
 
r.lexical_form.lexical_form = String("'test2'")
assert r.lexical_form.render() == "'test2'"
assert r.render() == "'test2' ^^ <test>"
assert r.isValid()

r.lexical_form = STRING_LITERAL1("'test2'")
assert r.lexical_form.render() == "'test2'"
assert r.render() == "'test2' ^^ <test>"
assert r.isValid()

 
r.datatype = PN_LOCAL_ESC('\\&')
assert r.datatype.render() == '\\&'
assert r.render() == "'test2' ^^ \\&"
assert not r.isValid()

s = '(DISTINCT *Expression*,  *Expression*,   *Expression* )'
p = ArgList_p.parseString(s)[0]
q = ArgList(s)

assert p == q
assert p.render() == q.render()
assert p.hasKey('distinct')
p.expression_list = Expression('*Expression*')
assert p.isValid()

print('\nPassed')

