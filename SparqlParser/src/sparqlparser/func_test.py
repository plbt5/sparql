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
assert p.yieldsValidExpression()
assert p.isConsistent()
assert r == p

q.lexical_form = STRING_LITERAL1("'work'")
assert q.lexical_form.render() == "'work'"
assert q.render() == "'work' ^^ <work>"
assert q.yieldsValidExpression()
assert q.isConsistent()
assert not r == q
 
r.lexical_form.lexical_form = String("'test2'")
assert r.lexical_form.render() == "'test2'"
assert r.render() == "'test2' ^^ <work>"
assert r.isConsistent()
assert r.yieldsValidExpression()

r.lexical_form = STRING_LITERAL1("'test2'")
assert r.lexical_form.render() == "'test2'"
assert r.render() == "'test2' ^^ <work>"
assert r.isConsistent()
assert r.yieldsValidExpression()

 
r.datatype_uri = PN_LOCAL_ESC('\\&')
assert r.datatype_uri.render() == '\\&'
assert r.render() == "'test2' ^^ \\&"
assert r.isConsistent()
assert not r.yieldsValidExpression()

s = '(DISTINCT *Expression*,  *Expression*,   *Expression* )'
p = ArgList_p.parseString(s)[0]
q = ArgList(s)

assert p == q
assert p.render() == q.render()
assert p.hasKey('distinct')
p.expression_list = Expression('*Expression*')
assert p.yieldsValidExpression()

print('\nPassed')

