from pyparsing import *
from sparqlparser.base import *
from sparqlparser.grammar import *

        
RDFPattern = Group(
                     String_p('lexical_form') \
                     + Optional(
                                Group (
                                       (
                                        LANGTAG_p('langtag') \
                                        ^ \
                                        ('^^' + iri_p('datatype'))
                                        )
                                       )
                                )
                     )('group')
                     
# [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
l = ['"test"', '"test" @en-bf', "'test' ^^ <test>", "'test'^^:"]
# printResults(l, 'RDFLiteral')

print()

s = "'test' ^^ <test>"

r = RDFLiteral_p.parseString(s)

pass
dumpSPARQLNode(r[0])