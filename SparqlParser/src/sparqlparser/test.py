from pyparsing import *
from sparqlparser.base import *
from sparqlparser.grammar import *

s = '"test"'

r = RDFLiteral(s)

assert r == RDFLiteral_p.parseString(s)[0]

comment = """
[RDFLiteral] "test"
  > lexical_form:
  [String] "test"
    > lexical_form:
    [STRING_LITERAL2] "test"
      - "test" <str>
"""

r.dump()