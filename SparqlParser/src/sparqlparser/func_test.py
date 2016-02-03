from pyparsing import *
from sparqlparser.base import *
from sparqlparser.grammar import *

# setup

s = "'test' ^^<test>"

r = RDFLiteral(s)
p = RDFLiteral_p.parseString(s)

# test render functie

assert r.render() == "'test' ^^ <test>" 
 
# test init van ParseInfo (twee manieren) geeft hetzelfde resultaat
 
assert r == p[0]
assert r.render() == p[0].render()
 
# test dot access (read)
 
assert r.lexical_form.render() == "'test'"
 
# test dot access (write)
 
r.lexical_form = String("'test2'")
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

print('Passed')

