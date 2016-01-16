from sparqlparser.grammar import *


# # [128]   iriOrFunction     ::=   iri ArgList? 
# l = ['<test:22?>','aA:Z.a', 'Z.8:AA', 'aA:', 'Z.8:', ':', '<test:22?>()','aA:Z.a (*Expression*)', 'Z.8:AA ( *Expression*, *Expression* )']
 
s = '<test:22?>()'
 
r = iriOrFunction_p.parseString(s)
 
print(type(r))
 
dumpElement(r)
print()
 
dumpElement(r.iri)
 
i = iri_p.parseString('<test22!>')
 
print()
 
# dumpParseResults(i)
 
setattr(r, 'iri', i)
 
print('r:')
 
dumpElement(r)
print('r.iri:')
dumpElement(r.iri)

