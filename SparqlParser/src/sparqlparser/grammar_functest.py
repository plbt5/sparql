from sparqlparser.grammar import *

# Next lines are temporary during development, to be deleted as implementions added to .grammar
# Expression_p << Literal('"*Expression*"')
GroupGraphPattern_p << Literal('{}')
# TriplesNodePath_p << Literal('($TriplesNodePath)')
# TriplesNode_p << Literal('($TriplesNode)')
# PropertyListPathNotEmpty_p << Literal('$VerbPath ?ObjectListPath') 
# PropertyListNotEmpty_p << Literal('$Verb $ObjectList')
# Path_p << Literal('<Path>')
# ConstructTriples_p << Literal('?ConstructTriples')
# ExpressionList_p << '()'


def printResults(l, rule, dump=False):
    print('=' * 80)
    print(rule)
    print('=' * 80)
    for s in l:
        rule_p = eval(rule + '_p')
        r = rule_p.parseString(s, parseAll=True)
        if dump:
            print()
            r[0].dump()
            print()
        rendering = r[0].render()
        print('\nParse : {}'.format(s))
        print('Render:', rendering)
        assert ''.join(r[0].render().upper().split()) == ''.join(s.upper().split()), 'Parsed expression: "{}" conflicts with original: "{}"'.format(r[0].render(), s)
        if s != rendering:
            print()
            print('+' * 80)
            print('Note: rendering (len={}) differs from input (len={})'.format(len(rendering), len(s)))
            print('+' * 80)
        print('\n' + '-' * 80)
        
if __name__ == '__main__':
    
        
    # [173]   PN_LOCAL_ESC      ::=   '\' ( '_' | '~' | '.' | '-' | '!' | '$' | '&' | "'" | '(' | ')' | '*' | '+' | ',' | ';' | '=' | '/' | '?' | '#' | '@' | '%' ) 
    l = ['\\&', '\\,']
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
    l = ['aA', 'Z.a', '\u022D%FA.:', '\u218F0:']
    printResults(l, 'PN_LOCAL')
                     
    # [168]   PN_PREFIX         ::=   PN_CHARS_BASE ((PN_CHARS|'.')* PN_CHARS)?
    l = ['aA', 'Z.8', 'zDFA.-', '\u218F0']
    printResults(l, 'PN_PREFIX')
                     
    # [166]   VARNAME   ::=   ( PN_CHARS_U | [0-9] ) ( PN_CHARS_U | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] )* 
    l = ['aA', '8fes', '_zDFA', '9_\u218B7']
    # printResults(l, 'VARNAME')
                    
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
    l = ['aA:Z.a', 'Z.8:AA']
    printResults(l, 'PNAME_LN')
                     
    # [139]   IRIREF    ::=   '<' ([^<>"{}|^`\]-[#x00-#x20])* '>' 
    l = ['<work:22?>']
    printResults(l, 'IRIREF')
                    
    # [138]   BlankNode         ::=   BLANK_NODE_LABEL | ANON 
    l = ['_:test9.33', '[ ]']
    printResults(l, 'BlankNode')
                    
    # [137]   PrefixedName      ::=   PNAME_LN | PNAME_NS 
    l = ['aA:Z.a', 'Z.8:AA', 'aA:', 'Z.8:', ':']
    printResults(l, 'PrefixedName')
                   
    # [136]   iri       ::=   IRIREF | PrefixedName 
    l = ['<work:22?>','aA:Z.a', 'Z.8:AA', 'aA:', 'Z.8:', ':']
    printResults(l, 'iri')
                  
    # [135]   String    ::=   STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 
    l = ['"""abc def"\t ghi""x yz"""', "'''abc def'\t ghi''x yz'''", '"abc d\'ef\t ghix yz"', '"abc d\'ef   ghix yz"', "'abc d\"ef\t ghix yz'"]
    printResults(l, 'String')
                  
    # [134]   BooleanLiteral    ::=   'true' | 'false' 
    l = ['true']
    printResults(l, 'BooleanLiteral')
                  
    # [133]   NumericLiteralNegative    ::=   INTEGER_NEGATIVE | DECIMAL_NEGATIVE | DOUBLE_NEGATIVE 
    l = ['-33', '-22.33', '-22.33e-44']
    printResults(l, 'NumericLiteralNegative')
                  
    # [132]   NumericLiteralPositive    ::=   INTEGER_POSITIVE | DECIMAL_POSITIVE | DOUBLE_POSITIVE 
    l = ['+33', '+22.33', '+22.33e-44']
    printResults(l, 'NumericLiteralPositive')
                  
    # [131]   NumericLiteralUnsigned    ::=   INTEGER | DECIMAL | DOUBLE 
    l = ['33', '22.33', '22.33e-44']
    printResults(l, 'NumericLiteralUnsigned')
                  
    # [130]   NumericLiteral    ::=   NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative 
    l = ['33', '+22.33', '-22.33e-44']
    printResults(l, 'NumericLiteral')
           
    # [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
    l = ['"work"', '"work" @en-bf', "'work' ^^ <work>", "'work'^^:"]
    printResults(l, 'RDFLiteral')
           
    # [71]    ArgList   ::=   NIL | '(' 'DISTINCT'? Expression ( ',' Expression )* ')' 
    l = ['()', '( "*Expression*") ', '("*Expression*", "*Expression*")', '(DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )']
    printResults(l, 'ArgList')
           
    # [128]   iriOrFunction     ::=   iri ArgList? 
    l = ['<work:22?>','aA:Z.a', 'Z.8:AA', 'aA:', 'Z.8:', ':', '<work:22?>()','aA:Z.a ("*Expression*")']
    printResults(l, 'iriOrFunction')
 
    # [127]   Aggregate         ::=     'COUNT' '(' 'DISTINCT'? ( '*' | Expression ) ')' 
    #             | 'SUM' '(' 'DISTINCT'? Expression ')' 
    #             | 'MIN' '(' 'DISTINCT'? Expression ')' 
    #             | 'MAX' '(' 'DISTINCT'? Expression ')' 
    #             | 'AVG' '(' 'DISTINCT'? Expression ')' 
    #             | 'SAMPLE' '(' 'DISTINCT'? Expression ')' 
    #             | 'GROUP_CONCAT' '(' 'DISTINCT'? Expression ( ';' 'SEPARATOR' '=' String )? ')' 
    l = ['avg(*)', 'count (distinct *)', 'min("*Expression*")', 'GROUP_CONCAT ( distinct "*Expression*" ; SEPARATOR = "sep")']
    printResults(l, 'Aggregate')
    
    # [126]   NotExistsFunc     ::=   'NOT' 'EXISTS' GroupGraphPattern 
    l = ['NOT Exists {}']
    printResults(l, 'NotExistsFunc')

    # [125]   ExistsFunc        ::=   'EXISTS' GroupGraphPattern 
    l = ['Exists {}']
    printResults(l, 'ExistsFunc')
    
    # [124]   StrReplaceExpression      ::=   'REPLACE' '(' Expression ',' Expression ',' Expression ( ',' Expression )? ')' 
    l = ['REPLACE ("*Expression*", "*Expression*", "*Expression*")', 'REPLACE ("*Expression*", "*Expression*", "*Expression*", "*Expression*")']
    printResults(l, 'StrReplaceExpression')
    
    # [123]   SubstringExpression       ::=   'SUBSTR' '(' Expression ',' Expression ( ',' Expression )? ')' 
    l = ['SUBSTR ("*Expression*", "*Expression*")', 'SUBSTR ("*Expression*", "*Expression*", "*Expression*")']
    printResults(l, 'SubstringExpression')

    # [122]   RegexExpression   ::=   'REGEX' '(' Expression ',' Expression ( ',' Expression )? ')' 
    l = ['REGEX ("*Expression*", "*Expression*")', 'REGEX ("*Expression*", "*Expression*", "*Expression*")']
    printResults(l, 'RegexExpression')
    
    # [108]   Var       ::=   VAR1 | VAR2 
    l = ['$aA', '?9_\u218B7']
    printResults(l, 'Var')

    # [121]   BuiltInCall       ::=     Aggregate 
    #             | 'STR' '(' Expression ')' 
    #             | 'LANG' '(' Expression ')' 
    #             | 'LANGMATCHES' '(' Expression ',' Expression ')' 
    #             | 'DATATYPE' '(' Expression ')' 
    #             | 'BOUND' '(' Var ')' 
    #             | 'IRI' '(' Expression ')' 
    #             | 'URI' '(' Expression ')' 
    #             | 'BNODE' ( '(' Expression ')' | NIL ) 
    #             | 'RAND' NIL 
    #             | 'ABS' '(' Expression ')' 
    #             | 'CEIL' '(' Expression ')' 
    #             | 'FLOOR' '(' Expression ')' 
    #             | 'ROUND' '(' Expression ')' 
    #             | 'CONCAT' ExpressionList 
    #             | SubstringExpression 
    #             | 'STRLEN' '(' Expression ')' 
    #             | StrReplaceExpression 
    #             | 'UCASE' '(' Expression ')' 
    #             | 'LCASE' '(' Expression ')' 
    #             | 'ENCODE_FOR_URI' '(' Expression ')' 
    #             | 'CONTAINS' '(' Expression ',' Expression ')' 
    #             | 'STRSTARTS' '(' Expression ',' Expression ')' 
    #             | 'STRENDS' '(' Expression ',' Expression ')' 
    #             | 'STRBEFORE' '(' Expression ',' Expression ')' 
    #             | 'STRAFTER' '(' Expression ',' Expression ')' 
    #             | 'YEAR' '(' Expression ')' 
    #             | 'MONTH' '(' Expression ')' 
    #             | 'DAY' '(' Expression ')' 
    #             | 'HOURS' '(' Expression ')' 
    #             | 'MINUTES' '(' Expression ')' 
    #             | 'SECONDS' '(' Expression ')' 
    #             | 'TIMEZONE' '(' Expression ')' 
    #             | 'TZ' '(' Expression ')' 
    #             | 'NOW' NIL 
    #             | 'UUID' NIL 
    #             | 'STRUUID' NIL 
    #             | 'MD5' '(' Expression ')' 
    #             | 'SHA1' '(' Expression ')' 
    #             | 'SHA256' '(' Expression ')' 
    #             | 'SHA384' '(' Expression ')' 
    #             | 'SHA512' '(' Expression ')' 
    #             | 'COALESCE' ExpressionList 
    #             | 'IF' '(' Expression ',' Expression ',' Expression ')' 
    #             | 'STRLANG' '(' Expression ',' Expression ')' 
    #             | 'STRDT' '(' Expression ',' Expression ')' 
    #             | 'sameTerm' '(' Expression ',' Expression ')' 
    #             | 'isIRI' '(' Expression ')' 
    #             | 'isURI' '(' Expression ')' 
    #             | 'isBLANK' '(' Expression ')' 
    #             | 'isLITERAL' '(' Expression ')' 
    #             | 'isNUMERIC' '(' Expression ')' 
    #             | RegexExpression 
    #             | ExistsFunc 
    #             | NotExistsFunc 
    l = ['STRUUID()', 'ROUND ( "*Expression*")', 'isBLANK ("*Expression*")', 'COUNT ( * )']
    printResults(l, 'BuiltInCall')
    
    # [120]   BrackettedExpression      ::=   '(' Expression ')' 
    l = ['("*Expression*")']
    printResults(l, 'BracketedExpression')
    
    # [119]   PrimaryExpression         ::=   BrackettedExpression | BuiltInCall | iriOrFunction | RDFLiteral | NumericLiteral | BooleanLiteral | Var 
    l = ['("*Expression*")', 'AVG ("*Expression*")', '<work:22?>()', '"work"^^<test>', '113.44', 'true', '$algebra']
    printResults(l, 'PrimaryExpression')
    
    # [118]   UnaryExpression   ::=     '!' PrimaryExpression 
    #             | '+' PrimaryExpression 
    #             | '-' PrimaryExpression 
    #             | PrimaryExpression 
    l = ['("*Expression*")', '!AVG ("*Expression*")', '+ <work:22?>()', '-"work"^^<test>']
    printResults(l, 'UnaryExpression')

    # [117]   MultiplicativeExpression          ::=   UnaryExpression ( '*' UnaryExpression | '/' UnaryExpression )* 
    l = ['<test()> * !$algebra / true']
    printResults(l, 'MultiplicativeExpression')

    # [116]   AdditiveExpression        ::=   MultiplicativeExpression ( '+' MultiplicativeExpression | '-' MultiplicativeExpression | ( NumericLiteralPositive | NumericLiteralNegative ) ( ( '*' UnaryExpression ) | ( '/' UnaryExpression ) )* )* 
    l = ['33*<test>() + 44*55 - 77']
    printResults(l, 'AdditiveExpression')
    
    # [115]   NumericExpression         ::=   AdditiveExpression 
    l = ['33*<test>() + 44*55 - 77']
    printResults(l, 'NumericExpression')
        
    # [114]   RelationalExpression      ::=   NumericExpression ( '=' NumericExpression | '!=' NumericExpression | '<' NumericExpression | '>' NumericExpression | '<=' NumericExpression | '>=' NumericExpression | 'IN' ExpressionList | 'NOT' 'IN' ExpressionList )? 
    l = ['33*<test>() = 33 * 75', '33 IN ()', '44 * 75 NOT IN ()']
    printResults(l, 'RelationalExpression')
        
    # [113]   ValueLogical      ::=   RelationalExpression 
    l = ['33*<test>() = 33 * 75', '33 IN ()', '44 * 75 NOT IN ()']
    printResults(l, 'ValueLogical')
    
    # [112]   ConditionalAndExpression          ::=   ValueLogical ( '&&' ValueLogical )* 
    l = ['33*<test>() = 33 * 44 && 33 IN ()', '44 * 75 NOT IN ()']
    printResults(l, 'ConditionalAndExpression')

    # [111]   ConditionalOrExpression   ::=   ConditionalAndExpression ( '||' ConditionalAndExpression )* 
    l = ['("*Expression*")', '33*<test>() = 33 * 44 && 33 IN ()']
    printResults(l, 'ConditionalOrExpression')
        
    # [110]   Expression        ::=   ConditionalOrExpression 
    l = ['("*Expression*")', '33*<test>() = 33 * 44 && 33 IN ()  || 44 * 75 NOT IN ()']
    printResults(l, 'Expression')
        
    # [109]   GraphTerm         ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | BlankNode | NIL 
    l = ['aA:Z.a', '"work" @en-bf', '-22.33e-44', 'true', '_:test9.33', '[ ]', '()']
    printResults(l, 'GraphTerm')
        
    # [107]   VarOrIri          ::=   Var | iri 
    l = ['$algebra', '<test>', 'az:Xy']
    printResults(l, 'VarOrIri')
    
    # [106]   VarOrTerm         ::=   Var | GraphTerm 
    l = ['$algebra', '"work" @en-bf', '-22.33e-44']
    printResults(l, 'VarOrTerm')
        
    # [105]   GraphNodePath     ::=   VarOrTerm | TriplesNodePath 
    l = ['$algebra', '($TriplesNodePath)']
    printResults(l, 'GraphNodePath')
            
    # [104]   GraphNode         ::=   VarOrTerm | TriplesNode 
    l = ['$algebra', '($TriplesNode)']
    printResults(l, 'GraphNode')
    
    # [103]   CollectionPath    ::=   '(' GraphNodePath+ ')' 
    l = ['($algebra)', '(($TriplesNodePath) $algebra )']
    printResults(l, 'CollectionPath')
        
    # [102]   Collection        ::=   '(' GraphNode+ ')' 
    l = ['($algebra)', '($algebra ($TriplesNode))']
    printResults(l, 'Collection')
        
    # [101]   BlankNodePropertyListPath         ::=   '[' PropertyListPathNotEmpty ']' 
    l = ['[ $VerbPath ?ObjectListPath ]']
    printResults(l, 'BlankNodePropertyListPath')
            
    # [100]   TriplesNodePath   ::=   CollectionPath | BlankNodePropertyListPath 
    l = ['($algebra)', '(($TriplesNodePath) $algebra )', '[ $VerbPath ?ObjectListPath ]']
    printResults(l, 'TriplesNodePath')
        
    # [99]    BlankNodePropertyList     ::=   '[' PropertyListNotEmpty ']' 
    l = ['[ $Verb $ObjectList ]']
    printResults(l, 'BlankNodePropertyList')
        
    # [98]    TriplesNode       ::=   Collection | BlankNodePropertyList 
    l = ['($algebra)', '($algebra ($TriplesNode))', '[ $Verb $ObjectList ]']
    printResults(l, 'TriplesNode')    
    
    # [97]    Integer   ::=   INTEGER 
    l = ['33']
    printResults(l, 'Integer')
    
    # [96]    PathOneInPropertySet      ::=   iri | 'a' | '^' ( iri | 'a' ) 
    l = ['<test>', 'a', '^<test>', '^ a']
    printResults(l, 'PathOneInPropertySet')    
    
    # [95]    PathNegatedPropertySet    ::=   PathOneInPropertySet | '(' ( PathOneInPropertySet ( '|' PathOneInPropertySet )* )? ')' 
    l = ['(^<testIri>|^<testIri>)', '()', '(^ a|^<testIri>)']
    printResults(l, 'PathNegatedPropertySet')    
    
    # [94]    PathPrimary       ::=   iri | 'a' | '!' PathNegatedPropertySet | '(' Path ')' 
    l = ['<testIri>', 'a', '!(^<testIri>|^<testIri>)', '! ( )', '! ( ^ a | ^ <testIri> )', '(<Path>)']
    printResults(l, 'PathPrimary')    
        
    # [93]    PathMod   ::=   '?' | '*' | '+' 
    l = ['*']
    printResults(l, 'PathMod')    
     
    # [91]    PathElt   ::=   PathPrimary PathMod? 
    l = ['! ( ^ <testIri> | ^ <testIri> )', 'a ?']
    printResults(l, 'PathElt')    

    # [92]    PathEltOrInverse          ::=   PathElt | '^' PathElt 
    l = ['! ( ^ <testIri> | ^ <testIri> )', 'a ?', '^ ! ( ^ <testIri> | ^ <testIri> )', '^a ?']
    printResults(l, 'PathEltOrInverse')   
        
    # [90]    PathSequence      ::=   PathEltOrInverse ( '/' PathEltOrInverse )* 
    l = ['a ? / ^ ! ( ^ <testIri> | ^ <testIri> )']
    printResults(l, 'PathSequence')    
    
    # [89]    PathAlternative   ::=   PathSequence ( '|' PathSequence )* 
    l = ['a ? / ^ ! ( ^ <testIri> | ^ <testIri> ) | a ? / ^ ! ( ^ <testIri> | ^ <testIri> )']
    printResults(l, 'PathAlternative')   
        
    # [88]    Path      ::=   PathAlternative 
    l = ['a ? / ^ ! ( ^ <testIri> | ^ <testIri> ) | a ? / ^ ! ( ^ <testIri> | ^ <testIri> )']
    printResults(l, 'Path')   
            
    # [87]    ObjectPath        ::=   GraphNodePath 
    l = ['$algebra', '($TriplesNodePath)']
    printResults(l, 'ObjectPath')   
    
    # [86]    ObjectListPath    ::=   ObjectPath ( ',' ObjectPath )* 
    l = ['$algebra', '(?TriplesNodePath), $algebra']
    printResults(l, 'ObjectListPath')     
    
    # [85]    VerbSimple        ::=   Var 
    l = ['$aA', '?9_\u218B7']
    printResults(l, 'VerbSimple')
    
    # [84]    VerbPath          ::=   Path 
    l = ['a ? / ^ ! ( ^ <testIri> | ^ <testIri> ) | a ? / ^ ! ( ^ <testIri> | ^ <testIri> )']
    printResults(l, 'VerbPath')  
        
    # [80]    Object    ::=   GraphNode 
    l = ['$algebra', '($TriplesNode)']
    printResults(l, 'Object')
        
    # [79]    ObjectList        ::=   Object ( ',' Object )* 
    l = ['$algebra, ($TriplesNode)']
    printResults(l, 'ObjectList')
        
    # [83]    PropertyListPathNotEmpty          ::=   ( VerbPath | VerbSimple ) ObjectListPath ( ';' ( ( VerbPath | VerbSimple ) ObjectList )? )* 
    l = ['<test> ?path ; <test2> $algebra, ($TriplesNode) ;;', '<test> ? ?path']
    printResults(l, 'PropertyListPathNotEmpty')
        
    # [82]    PropertyListPath          ::=   PropertyListPathNotEmpty? 
    l = ['<test> ?path ; <test2> $algebra, ($TriplesNode) ;;', '<test> ? ?path', '']
    printResults(l, 'PropertyListPath')
        
    # [81]    TriplesSameSubjectPath    ::=   VarOrTerm PropertyListPathNotEmpty | TriplesNodePath PropertyListPath 
    l = ['"work" @en-bf <test> ?path ; <test2> $algebra, ($TriplesNode) ;;', '(($TriplesNodePath) $algebra )', '(($TriplesNodePath) $algebra ) <test> ? ?path']
    printResults(l, 'TriplesSameSubjectPath')
    
    # [78]    Verb      ::=   VarOrIri | 'a' 
    l = ['$algebra', '<test>', 'az:Xy', 'a']
    printResults(l, 'Verb')
        
    # [77]    PropertyListNotEmpty      ::=   Verb ObjectList ( ';' ( Verb ObjectList )? )* 
    l = ['$algebra $algebra, ($TriplesNode)', '<test> $algebra, ($TriplesNode) ; a ?algebra, ($TriplesNode)']
    printResults(l, 'PropertyListNotEmpty')
        
    # [76]    PropertyList      ::=   PropertyListNotEmpty? 
    l = ['$algebra $algebra, ($TriplesNode)', '<test> $algebra, ($TriplesNode) ; a ?algebra, ($TriplesNode)', '']
    printResults(l, 'PropertyList')
    
    # [75]    TriplesSameSubject        ::=   VarOrTerm PropertyListNotEmpty | TriplesNode PropertyList 
    l = ['?var $algebra $algebra, ($TriplesNode)', '_:test9.33 <test> $algebra, ($TriplesNode) ; a ?algebra, ($TriplesNode)', '[ $Verb $ObjectList ]']
    printResults(l, 'TriplesSameSubject')

    # [74]    ConstructTriples          ::=   TriplesSameSubject ( '.' ConstructTriples? )? 
    l = ['_:test9.33 <test> $algebra, ($TriplesNode) ; a ?algebra, ($TriplesNode). [ $Verb $ObjectList ]']
    printResults(l, 'ConstructTriples')
        
    # [73]    ConstructTemplate         ::=   '{' ConstructTriples? '}' 
    l = ['{_:test9.33 <test> $algebra, ($TriplesNode) ; a ?algebra, ($TriplesNode)}']
    printResults(l, 'ConstructTemplate')
    
    # [72]    ExpressionList    ::=   NIL | '(' Expression ( ',' Expression )* ')' 
    l = ['()', '(("*Expression*"), 33*<test>() = 33 * 44 && 33 IN ()  || 44 * 75 NOT IN ())']
    printResults(l, 'ExpressionList')
        
    # [70]    FunctionCall      ::=   iri ArgList 
    l = ['<test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )']
    printResults(l, 'FunctionCall')
            
    # [69]    Constraint        ::=   BrackettedExpression | BuiltInCall | FunctionCall 
    l = ['<test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )', 'STRUUID()', 'ROUND ( "*Expression*")', 'isBLANK ("*Expression*")', 'COUNT ( * )', '("*Expression*")']
    printResults(l, 'Constraint')
        
    # [68]    Filter    ::=   'FILTER' Constraint 
    l = ['FILTER <test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )', 'FILTER STRUUID()', 'FILTER ROUND ( "*Expression*")', 'FILTER isBLANK ("*Expression*")', 'FILTER COUNT ( * )', 'FILTER ("*Expression*")']
    printResults(l, 'Filter')
            
    # [67]    GroupOrUnionGraphPattern          ::=   GroupGraphPattern ( 'UNION' GroupGraphPattern )* 
    l = ['{}', '{} UNION {}', '{} UNION {} UNION {}']
    printResults(l, 'GroupOrUnionGraphPattern')
        
    # [66]    MinusGraphPattern         ::=   'MINUS' GroupGraphPattern 
    l = ['MINUS {}']
    printResults(l, 'MinusGraphPattern')
            
    # [65]    DataBlockValue    ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | 'UNDEF' 
    l = ['<work:22?>', '"test" ^^ <test>', '333.55', 'true', 'UNDEF']
    printResults(l, 'DataBlockValue')
                
    # [64]    InlineDataFull    ::=   ( NIL | '(' Var* ')' ) '{' ( '(' DataBlockValue* ')' | NIL )* '}' 
    l = ['( $4℀ $4℀ )  { ( true true ) }']
    printResults(l, 'InlineDataFull')
        
    # [63]    InlineDataOneVar          ::=   Var '{' DataBlockValue* '}' 
    l = ['$S { <testIri> <testIri> }']
    printResults(l, 'InlineDataOneVar')
            
    # [62]    DataBlock         ::=   InlineDataOneVar | InlineDataFull 
    l = ['( $4℀ $4℀ )  { ( true true ) }', '$S { <testIri> <testIri> }']
    printResults(l, 'DataBlock')
        
    # [61]    InlineData        ::=   'VALUES' DataBlock 
#     l = ["VALUES  ( $4℀ $4℀ )  { ( 'te\n' 'te\n' ) }"]
    l = ["VALUES  ( $4℀ $4℀ )  { ( 'te\\n' 'te\\n' ) }"]
    printResults(l, 'InlineData')
            
#     # [60]    Bind      ::=   'BIND' '(' Expression 'AS' Var ')' 
    l = ['BIND ( ("*Expression*") AS $var)']
    printResults(l, 'Bind')
            
    # [59]    ServiceGraphPattern       ::=   'SERVICE' 'SILENT'? VarOrIri GroupGraphPattern 
    l = ['SERVICE <test> {}', 'SERVICE SILENT ?var {}']
    printResults(l, 'ServiceGraphPattern')
                
    # [58]    GraphGraphPattern         ::=   'GRAPH' VarOrIri GroupGraphPattern 
    l = ['GRAPH <test> {}', 'GRAPH ?var {}']
    printResults(l, 'GraphGraphPattern')
        
    # [57]    OptionalGraphPattern      ::=   'OPTIONAL' GroupGraphPattern 
    l = ['OPTIONAL {}']
    printResults(l, 'OptionalGraphPattern')
    
    # [56]    GraphPatternNotTriples    ::=   GroupOrUnionGraphPattern | OptionalGraphPattern | MinusGraphPattern | GraphGraphPattern | ServiceGraphPattern | Filter | Bind | InlineData 
    l = ['{} UNION {} UNION {}', 'OPTIONAL {}', 'MINUS {}', 'GRAPH <test> {}', 'SERVICE SILENT ?var {}',
         'FILTER <test:227> (DISTINCT "*Expression*",  "*Expression*",   "*Expression*" )','BIND ( ("*Expression*") AS $var)', "VALUES  ( $4℀ $4℀ )  { ( 'te\\n' 'te\\n' ) }"]
    printResults(l, 'GraphPatternNotTriples')
        
    # [55]    TriplesBlock      ::=   TriplesSameSubjectPath ( '.' TriplesBlock? )? 
    l = ['(($TriplesNodePath) $algebra ) . "TriplesBlock" @en-bf <test> ?path ; <test2> $algebra, ($TriplesBlock)']
    printResults(l, 'TriplesBlock')
    
    # [54]    GroupGraphPatternSub      ::=   TriplesBlock? ( GraphPatternNotTriples '.'? TriplesBlock? )* 
    l = ['(($TriplesNodePath) $algebra ) . SERVICE SILENT ?var {} . (($TriplesNodePath) $algebra )']
    printResults(l, 'GroupGraphPatternSub')
    
    # [53]    GroupGraphPattern         ::=   '{' ( SubSelect | GroupGraphPatternSub ) '}' 
    
    # [52]    TriplesTemplate   ::=   TriplesSameSubject ( '.' TriplesTemplate? )? 
    
    # [51]    QuadsNotTriples   ::=   'GRAPH' VarOrIri '{' TriplesTemplate? '}' 
    
    # [50]    Quads     ::=   TriplesTemplate? ( QuadsNotTriples '.'? TriplesTemplate? )* 
    
    # [49]    QuadData          ::=   '{' Quads '}' 
    
    # [48]    QuadPattern       ::=   '{' Quads '}' 
    
    # [47]    GraphRefAll       ::=   GraphRef | 'DEFAULT' | 'NAMED' | 'ALL' 
    
    # [46]    GraphRef          ::=   'GRAPH' iri 
    
    # [45]    GraphOrDefault    ::=   'DEFAULT' | 'GRAPH'? iri 
    
    # [44]    UsingClause       ::=   'USING' ( iri | 'NAMED' iri ) 
    
    # [43]    InsertClause      ::=   'INSERT' QuadPattern 
    
    # [42]    DeleteClause      ::=   'DELETE' QuadPattern 
    
    # [41]    Modify    ::=   ( 'WITH' iri )? ( DeleteClause InsertClause? | InsertClause ) UsingClause* 'WHERE' GroupGraphPattern 
    
    # [40]    DeleteWhere       ::=   'DELETE WHERE' QuadPattern 
    
    # [39]    DeleteData        ::=   'DELETE DATA' QuadData 
    
    # [38]    InsertData        ::=   'INSERT DATA' QuadData 
    
    # [37]    Copy      ::=   'COPY' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
    
    # [36]    Move      ::=   'MOVE' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
    
    # [35]    Add       ::=   'ADD' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
    
    # [34]    Create    ::=   'CREATE' 'SILENT'? GraphRef 
    
    # [33]    Drop      ::=   'DROP' 'SILENT'? GraphRefAll 
    
    # [32]    Clear     ::=   'CLEAR' 'SILENT'? GraphRefAll 
    
    # [31]    Load      ::=   'LOAD' 'SILENT'? iri ( 'INTO' GraphRef )? 
    
    # [30]    Update1   ::=   Load | Clear | Drop | Add | Move | Copy | Create | InsertData | DeleteData | DeleteWhere | Modify 
    
    # [29]    Update    ::=   Prologue ( Update1 ( ';' Update )? )? 
    
    # [28]    ValuesClause      ::=   ( 'VALUES' DataBlock )? 
    
    # [27]    OffsetClause      ::=   'OFFSET' INTEGER 
    
    # [26]    LimitClause       ::=   'LIMIT' INTEGER 
    
    # [25]    LimitOffsetClauses        ::=   LimitClause OffsetClause? | OffsetClause LimitClause? 
    
    # [24]    OrderCondition    ::=   ( ( 'ASC' | 'DESC' ) BrackettedExpression ) 
    
    #             | ( Constraint | Var ) 
    
    # [23]    OrderClause       ::=   'ORDER' 'BY' OrderCondition+ 
    
    # [22]    HavingCondition   ::=   Constraint 
    
    # [21]    HavingClause      ::=   'HAVING' HavingCondition+ 
    
    # [20]    GroupCondition    ::=   BuiltInCall | FunctionCall | '(' Expression ( 'AS' Var )? ')' | Var 
    
    # [19]    GroupClause       ::=   'GROUP' 'BY' GroupCondition+ 
    
    # [18]    SolutionModifier          ::=   GroupClause? HavingClause? OrderClause? LimitOffsetClauses? 
    
    # [17]    WhereClause       ::=   'WHERE'? GroupGraphPattern 
    
    # [16]    SourceSelector    ::=   iri 
    
    # [15]    NamedGraphClause          ::=   'NAMED' SourceSelector 
    
    # [14]    DefaultGraphClause        ::=   SourceSelector 
    
    # [13]    DatasetClause     ::=   'FROM' ( DefaultGraphClause | NamedGraphClause ) 
    
    # [12]    AskQuery          ::=   'ASK' DatasetClause* WhereClause SolutionModifier 
    
    # [11]    DescribeQuery     ::=   'DESCRIBE' ( VarOrIri+ | '*' ) DatasetClause* WhereClause? SolutionModifier 
    
    # [10]    ConstructQuery    ::=   'CONSTRUCT' ( ConstructTemplate DatasetClause* WhereClause SolutionModifier | DatasetClause* 'WHERE' '{' TriplesTemplate? '}' SolutionModifier ) 
    
    # [9]     SelectClause      ::=   'SELECT' ( 'DISTINCT' | 'REDUCED' )? ( ( Var | ( '(' Expression 'AS' Var ')' ) )+ | '*' ) 
    
    # [8]     SubSelect         ::=   SelectClause WhereClause SolutionModifier ValuesClause 
    
    # [7]     SelectQuery       ::=   SelectClause DatasetClause* WhereClause SolutionModifier 
    
    # [6]     PrefixDecl        ::=   'PREFIX' PNAME_NS IRIREF 
    
    # [5]     BaseDecl          ::=   'BASE' IRIREF 
    
    # [4]     Prologue          ::=   ( BaseDecl | PrefixDecl )* 
    
    # [3]     UpdateUnit        ::=   Update 
    
    # [2]     Query     ::=   Prologue 
    
    #             ( SelectQuery | ConstructQuery | DescribeQuery | AskQuery ) 
    
    #             ValuesClause 
    
    # [1]     QueryUnit         ::=   Query 
