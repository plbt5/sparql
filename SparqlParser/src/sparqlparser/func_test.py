from pyparsing import *
from sparqlparser.base import *

# setup

s = "'work' ^^<work>"

r = RDFLiteral(s)

# test copy 
p = r.copy()
q = p.copy()

assert p == r
assert q == r

# test render functie

assert r.render() == "'work' ^^ <work>" 
 
# test init van ParseInfo (twee manieren) geeft hetzelfde resultaat
 
assert r == RDFLiteral_p.parseString(s)[0]
 
# test dot access (read)
 
assert r.lexical_form.render() == "'work'"

# test dot access (write)
 
p.lexical_form.lexical_form = STRING_LITERAL1("'work'")
assert p.lexical_form.render() == "'work'"
assert p.render() == "'work' ^^ <work>"
assert p.yieldsValidExpression()
assert p.isValid()
assert p.isValid()
assert r == p
 
p.lexical_form.lexical_form = STRING_LITERAL1("'work2'")
assert p.lexical_form.render() == "'work2'"
assert p.render() == "'work2' ^^ <work>"
assert p.yieldsValidExpression()
assert p.isValid()
 
q.lexical_form = STRING_LITERAL1("'work'")
assert q.lexical_form.render() == "'work'"
assert q.render() == "'work' ^^ <work>"
assert q.yieldsValidExpression()
assert not q.isValid()
assert not r == q
  
r.lexical_form.lexical_form = String("'test2'")
assert r.lexical_form.render() == "'test2'"
assert r.render() == "'test2' ^^ <work>"
assert not r.isValid()
assert r.yieldsValidExpression()
 
r.lexical_form = STRING_LITERAL1("'test2'")
assert r.lexical_form.render() == "'test2'"
assert r.render() == "'test2' ^^ <work>"
assert r.yieldsValidExpression()
 
  
r.datatype_uri = PN_LOCAL_ESC('\\&')
assert r.datatype_uri.render() == '\\&'
assert r.render() == "'test2' ^^ \\&"
assert not r.yieldsValidExpression()
 
s = '(DISTINCT *Expression*,  *Expression*,   *Expression* )'
p = ArgList_p.parseString(s)[0]
q = ArgList(s)
 
assert p == q
assert p.render() == q.render()
assert p.hasKey('distinct')
p.expression_list = Expression('*Expression*')
assert p.yieldsValidExpression()

print('Passed')

