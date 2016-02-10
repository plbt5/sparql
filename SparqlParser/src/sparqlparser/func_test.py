from pyparsing import *
from sparqlparser.base import *
from sparqlparser.grammar import *

# setup

s = "'work' ^^<work>"

r = RDFLiteral(s)
p = RDFLiteral_p.parseString(s)[0]
q = RDFLiteral(s)
# work render functie

assert r.render() == "'work' ^^ <work>" 
 
# work init van ParseInfo (twee manieren) geeft hetzelfde resultaat
 
assert r == p
assert r.render() == p.render()
 
# work dot access (read)
 
assert r.lexical_form.render() == "'work'"

# work dot access (write)
 
p.lexical_form.lexical_form = STRING_LITERAL1("'work'")
assert p.lexical_form.render() == "'work'"
assert p.render() == "'work' ^^ <work>"
assert p.isValid()
assert r == p

q.lexical_form = STRING_LITERAL1("'work'")
assert q.lexical_form.render() == "'work'"
assert q.render() == "'work' ^^ <work>"
assert q.isValid()
assert not r == q
 
r.lexical_form.lexical_form = String("'test2'")
assert r.lexical_form.render() == "'test2'"
assert r.render() == "'test2' ^^ <work>"
assert r.isValid()

r.lexical_form = STRING_LITERAL1("'test2'")
assert r.lexical_form.render() == "'test2'"
assert r.render() == "'test2' ^^ <work>"
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

