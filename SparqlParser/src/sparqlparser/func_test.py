from pyparsing import *
from sparqlparser.base import *
from sparqlparser.grammar import *

s = "'test' ^^<test>"

r = RDFLiteral(s)
p = RDFLiteral_p.parseString(s)

assert r == p[0]
assert r.render() == "'test' ^^ <test>" 

assert r.lexical_form.render() == "'test'"

r.lexical_form = String("'test2'")
assert r.lexical_form.render() == "'test2'"

assert r.render() == "'test2' ^^ <test>"
