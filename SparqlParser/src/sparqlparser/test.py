from pyparsing import *
from sparqlparser.grammar import *

# [29]    Update    ::=   Prologue ( Update1 ( ';' Update )? )? 

Prologue_p << Literal('BASE <prologue:22> PREFIX prologue: <prologue:33>')
# Update_p << Literal('BASE <update:22> PREFIX update: <update:33>')
Update_p << (Prologue_p + Optional(Update1_p + Optional(SEMICOL_p + Update_p))) 


s = 'BASE <prologue:22> PREFIX prologue: <prologue:33> LOAD <testIri> ; BASE <prologue:22> PREFIX prologue: <prologue:33>'


print(Prologue_p.parseString(s))
print((Prologue_p + Optional(Update1_p + SEMICOL_p)).parseString(s))
print((Prologue_p + Optional(Update1_p + SEMICOL_p + Update_p)).parseString(s))

print(Update_p.parseString(s))

