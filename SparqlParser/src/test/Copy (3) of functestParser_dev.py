from sparqlparser_dev import *

def printResults(l, rule):
    print(rule)
    for s in l:
        r = eval(rule + '_p').parseString(s)
        print('\tParse: {} --> {}'.format(s, r[0]))
        print('\tChars:', r[0].asString())
# [173]   PN_LOCAL_ESC      ::=   '\' ( '_' | '~' | '.' | '-' | '!' | '$' | '&' | "'" | '(' | ')' | '*' | '+' | ',' | ';' | '=' | '/' | '?' | '#' | '@' | '%' ) 
l = ['\\&']
printResults(l, 'PN_LOCAL_ESC')
 
# [172]   HEX       ::=   [0-9] | [A-F] | [a-f] 
l = ['D']
printResults(l, 'HEX')
  
# [171]   PERCENT   ::=   '%' HEX HEX
l = ['%F0']
printResults(l, 'PERCENT')
  
# [170]   PLX       ::=   PERCENT | PN_LOCAL_ESC 
l = ['%FA', '\\*']
printResults(l, 'PLX')
 
# [164]   PN_CHARS_BASE     ::=   [A-Z] | [a-z] | [#x00C0-#x00D6] | [#x00D8-#x00F6] | [#x00F8-#x02FF] | [#x0370-#x037D] | [#x037F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF] 
l = ['a', 'Z', '\u022D', '\u218F']
printResults(l, 'PN_CHARS_BASE')
 
# [165]   PN_CHARS_U        ::=   PN_CHARS_BASE | '_' 
l = ['a', 'Z', '\u022D', '\u218F', '_']
printResults(l, 'PN_CHARS_U')
 
# # [167]   PN_CHARS          ::=   PN_CHARS_U | '-' | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] 
l = ['a', 'Z', '\u022D', '\u218F', '_', '7', '\u203F']
printResults(l, 'PN_CHARS')
  
# [169]   PN_LOCAL          ::=   (PN_CHARS_U | ':' | [0-9] | PLX ) ((PN_CHARS | '.' | ':' | PLX)* (PN_CHARS | ':' | PLX) )?
l = ['aA', 'Z.', '\u022D%FA.:', '\u218F0:']
printResults(l, 'PN_LOCAL')
 
# [168]   PN_PREFIX         ::=   PN_CHARS_BASE ((PN_CHARS|'.')* PN_CHARS)?
l = ['aA', 'Z.8', 'zDFA.-', '\u218F0']
printResults(l, 'PN_PREFIX')
 
# [166]   VARNAME   ::=   ( PN_CHARS_U | [0-9] ) ( PN_CHARS_U | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] )* 
l = ['aA', '8fes', '_zDFA', '9_\u218B7']
printResults(l, 'VARNAME')
 
# [163]   ANON      ::=   '[' WS* ']' 
l = ['[]', '[ ]', '[\t]']
printResults(l, 'ANON')
 
# [161]   NIL       ::=   '(' WS* ')' 
l = ['()', '(    )', '(\t)']
printResults(l, 'NIL')
 
# [160]   ECHAR     ::=   '\' [tbnrf\"']
l = [r'\t', r'\"']
printResults(l, 'ECHAR')
 
# [159]   STRING_LITERAL_LONG2      ::=   '"""' ( ( '"' | '""' )? ( [^"\] | ECHAR ) )* '"""'  
l = ['"""abc def"\t ghi""x yz"""']
printResults(l, 'STRING_LITERAL_LONG2')
 
# [158]   STRING_LITERAL_LONG1      ::=   "'''" ( ( "'" | "''" )? ( [^'\] | ECHAR ) )* "'''" 
l = ["'''abc def'\t ghi''x yz'''"]
printResults(l, 'STRING_LITERAL_LONG1')
 
# [157]   STRING_LITERAL2   ::=   '"' ( ([^#x22#x5C#xA#xD]) | ECHAR )* '"' 
l = ['"abc d\'ef\t ghix yz"']
printResults(l, 'STRING_LITERAL2')
 
# [156]   STRING_LITERAL1   ::=   "'" ( ([^#x27#x5C#xA#xD]) | ECHAR )* "'" 
l = ["'abc d\"ef\t ghix yz'"]
printResults(l, 'STRING_LITERAL1')
 
# [155]   EXPONENT          ::=   [eE] [+-]? [0-9]+ 
l = ['e-12', 'E+13']
printResults(l, 'EXPONENT')
 
# [148]   DOUBLE    ::=   [0-9]+ '.' [0-9]* EXPONENT | '.' ([0-9])+ EXPONENT | ([0-9])+ EXPONENT 
l = ['088.77e+24', '.88e+24', '88e+24']
printResults(l, 'DOUBLE')
 
# [154]   DOUBLE_NEGATIVE   ::=   '-' DOUBLE 
l = ['-088.77e+24', '-.88e+24', '-88e+24']
printResults(l, 'DOUBLE_NEGATIVE')
 
# [151]   DOUBLE_POSITIVE   ::=   '+' DOUBLE 
l = ['+088.77e+24', '+.88e+24', '+88e+24']
printResults(l, 'DOUBLE_POSITIVE')
 
# [147]   DECIMAL   ::=   [0-9]* '.' [0-9]+ 
l = ['.33', '03.33']
printResults(l, 'DECIMAL')
 
# [153]   DECIMAL_NEGATIVE          ::=   '-' DECIMAL 
l = ['-.33', '-03.33']
printResults(l, 'DECIMAL_NEGATIVE')
 
# [150]   DECIMAL_POSITIVE          ::=   '+' DECIMAL 
l = ['+.33', '+03.33']
printResults(l, 'DECIMAL_POSITIVE')
 
# [146]   INTEGER   ::=   [0-9]+ 
l = ['33']
printResults(l, 'INTEGER')
 
# [152]   INTEGER_NEGATIVE          ::=   '-' INTEGER
l = ['-33']
printResults(l, 'INTEGER_NEGATIVE')
 
# [149]   INTEGER_POSITIVE          ::=   '+' INTEGER 
l = ['+33']
printResults(l, 'INTEGER_POSITIVE')
 
# [145]   LANGTAG   ::=   '@' [a-zA-Z]+ ('-' [a-zA-Z0-9]+)* 
l = ['@Test', '@Test-nl-be']
printResults(l, 'LANGTAG')
 
# [144]   VAR2      ::=   '$' VARNAME 
l = ['$aA', '$8fes', '$_zDFA', '$9_\u218B7']
printResults(l, 'VAR2')
 
# [143]   VAR1      ::=   '?' VARNAME 
l = ['?aA', '?8fes', '?_zDFA', '?9_\u218B7']
printResults(l, 'VAR1')
 
# [142]   BLANK_NODE_LABEL          ::=   '_:' ( PN_CHARS_U | [0-9] ) ((PN_CHARS|'.')* PN_CHARS)?
l = ['_:test9.33']
printResults(l, 'BLANK_NODE_LABEL')
 
# [140]   PNAME_NS          ::=   PN_PREFIX? ':'
l = ['aA:', 'Z.8:', ':']
printResults(l, 'PNAME_NS')
 
# [141]   PNAME_LN          ::=   PNAME_NS PN_LOCAL 
l = ['aA:Z.', 'Z.8:AA']
printResults(l, 'PNAME_LN')
 
# [139]   IRIREF    ::=   '<' ([^<>"{}|^`\]-[#x00-#x20])* '>' 
l = ['<test:22?>']
printResults(l, 'IRIREF')
 
# [138]   BlankNode         ::=   BLANK_NODE_LABEL | ANON 
l = ['_:test9.33', '[ ]']
printResults(l, 'BlankNode')
 
# [137]   PrefixedName      ::=   PNAME_LN | PNAME_NS 
l = ['aA:Z.', 'Z.8:AA', 'aA:', 'Z.8:', ':']
printResults(l, 'PrefixedName')
 
# [136]   iri       ::=   IRIREF | PrefixedName 
l = ['<test:22?>','aA:Z.', 'Z.8:AA', 'aA:', 'Z.8:', ':']
printResults(l, 'iri')
 
# [135]   String    ::=   STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 
l = ['"""abc def"\t ghi""x yz"""', "'''abc def'\t ghi''x yz'''", '"abc d\'ef\t ghix yz"', "'abc d\"ef\t ghix yz'"]
printResults(l, 'String')
 
# [134]   BooleanLiteral    ::=   'true' | 'false' 
l = ['true']
printResults(l, 'BooleanLiteral')
 
# # [133]   NumericLiteralNegative    ::=   INTEGER_NEGATIVE | DECIMAL_NEGATIVE | DOUBLE_NEGATIVE 
l = ['-33', '-22.33', '-22.33e-44']
printResults(l, 'NumericLiteralNegative')
 
# # [132]   NumericLiteralPositive    ::=   INTEGER_POSITIVE | DECIMAL_POSITIVE | DOUBLE_POSITIVE 
l = ['+33', '+22.33', '+22.33e-44']
printResults(l, 'NumericLiteralPositive')
 
# # [131]   NumericLiteralUnsigned    ::=   INTEGER | DECIMAL | DOUBLE 
l = ['33', '22.33', '22.33e-44']
printResults(l, 'NumericLiteralUnsigned')
 
# # [130]   NumericLiteral    ::=   NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative 
l = ['33', '+22.33', '-22.33e-44']
printResults(l, 'NumericLiteral')
 
# [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
l = ['"test"', '"test" @en-bf', "'test' ^^ <test>", "'test'^^:"]
printResults(l, 'RDFLiteral')
