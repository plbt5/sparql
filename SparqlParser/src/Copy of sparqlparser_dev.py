'''
Created on 4 dec. 2015

@author: jeroenbruijning
'''
from pyparsing import ParseFatalException, Regex, Literal, Combine, Optional,\
    Forward, CaselessKeyword, delimitedList, Suppress, ParserElement
import sys

if sys.version_info < (3,3):
    raise ParseFatalException('This parser only works with Python 3.3 or later (due to unicode handling issues)')


# Conversion of EBNF syntax for SPARQL to pyparsing. For the grammar see http://www.w3.org/TR/sparql11-query/#grammar.
# 
# Productions for terminals
#

# [173]   PN_LOCAL_ESC      ::=   '\' ( '_' | '~' | '.' | '-' | '!' | '$' | '&' | "'" | '(' | ')' | '*' | '+' | ',' | ';' | '=' | '/' | '?' | '#' | '@' | '%' ) 
PN_LOCAL_ESC_re = r'\\[_~.\-!$&\'()*+,;=/?#@%]'
PN_LOCAL_ESC = Regex(PN_LOCAL_ESC_re)

# [172]   HEX       ::=   [0-9] | [A-F] | [a-f] 
HEX_re = r'[0-9A-Fa-f]'
HEX = Regex(HEX_re)

# [171]   PERCENT   ::=   '%' HEX HEX
PERCENT_re = r'%({})({})'.format( HEX_re, HEX_re)
PERCENT = Regex(PERCENT_re)

# [170]   PLX       ::=   PERCENT | PN_LOCAL_ESC 
PLX_re = r'({})|({})'.format( PERCENT_re, PN_LOCAL_ESC_re)
PLX = Regex(PLX_re)

# [164]   PN_CHARS_BASE     ::=   [A-Z] | [a-z] | [#x00C0-#x00D6] | [#x00D8-#x00F6] | [#x00F8-#x02FF] | [#x0370-#x037D] | [#x037F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF] 
PN_CHARS_BASE_re = r'[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF]'
PN_CHARS_BASE = Regex(PN_CHARS_BASE_re)

# [165]   PN_CHARS_U        ::=   PN_CHARS_BASE | '_' 
PN_CHARS_U_re = r'({})|({})'.format( PN_CHARS_BASE_re, r'_')
PN_CHARS_U = Regex(PN_CHARS_U_re)

# [167]   PN_CHARS          ::=   PN_CHARS_U | '-' | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] 
PN_CHARS_re = r'({})|({})|({})|({})|({})|({})'.format( PN_CHARS_U_re, r'\-', r'[0-9]',  r'\u00B7', r'[\u0300-\u036F]', r'[\u203F-\u2040]')
PN_CHARS = Regex(PN_CHARS_re) 

# [169]   PN_LOCAL          ::=   (PN_CHARS_U | ':' | [0-9] | PLX ) ((PN_CHARS | '.' | ':' | PLX)* (PN_CHARS | ':' | PLX) )?
PN_LOCAL_re = r'(({})|({})|({})|({}))((({})|({})|({})|({}))*(({})|({})|({})))?'.format( PN_CHARS_U_re, r':', r'[0-9]', PLX_re, PN_CHARS_re, r'\.', r':', PLX_re, PN_CHARS_re, r':', PLX_re) 
PN_LOCAL = Regex(PN_LOCAL_re)
            
# [168]   PN_PREFIX         ::=   PN_CHARS_BASE ((PN_CHARS|'.')* PN_CHARS)?
PN_PREFIX_re = r'({})((({})|({}))*({}))?'.format( PN_CHARS_BASE_re, PN_CHARS_re, r'\.', PN_CHARS_re)
PN_PREFIX = Regex(PN_PREFIX_re)

# [166]   VARNAME   ::=   ( PN_CHARS_U | [0-9] ) ( PN_CHARS_U | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] )* 
VARNAME_re = r'(({})|({}))(({})|({})|({})|({})|({}))*'.format( PN_CHARS_U_re, r'[0-9]', PN_CHARS_U_re, r'[0-9]', r'\u00B7', r'[\u0030-036F]', r'[\u0203-\u2040]')
VARNAME = Regex(VARNAME_re)

# [163]   ANON      ::=   '[' WS* ']' 
ANON = Literal('[') + ']'

# [162]   WS        ::=   #x20 | #x9 | #xD | #xA 
# WS is not used
# In the SPARWQL EBNF this production is used for defining NIL and ANON, but in this pyparsing implementation those are implemented independently

# [161]   NIL       ::=   '(' WS* ')' 
NIL = Literal('(') + ')'

# [160]   ECHAR     ::=   '\' [tbnrf\"']
ECHAR_re = r'\\[tbnrf\\"\']'
ECHAR = Regex(ECHAR_re) 
 
# [159]   STRING_LITERAL_LONG2      ::=   '"""' ( ( '"' | '""' )? ( [^"\] | ECHAR ) )* '"""'  
STRING_LITERAL_LONG2_re = r'"""((""|")?(({})|({})))*"""'.format(r'[^"\\]', ECHAR_re)
STRING_LITERAL_LONG2 = Regex(STRING_LITERAL_LONG2_re)

# [158]   STRING_LITERAL_LONG1      ::=   "'''" ( ( "'" | "''" )? ( [^'\] | ECHAR ) )* "'''" 
STRING_LITERAL_LONG1_re = r"'''(('|'')?(({})|({})))*'''".format(r"[^'\\]", ECHAR_re)
STRING_LITERAL_LONG1 = Regex(STRING_LITERAL_LONG1_re)  

# [157]   STRING_LITERAL2   ::=   '"' ( ([^#x22#x5C#xA#xD]) | ECHAR )* '"' 
STRING_LITERAL2_re = r'"(({})|({}))*"'.format(ECHAR_re, r'[^\u0022\u005C\u000A\u000D]')
STRING_LITERAL2 = Regex(STRING_LITERAL2_re)
                           
# [156]   STRING_LITERAL1   ::=   "'" ( ([^#x27#x5C#xA#xD]) | ECHAR )* "'" 
STRING_LITERAL1_re = r"'(({})|({}))*'".format(ECHAR_re, r'[^\u0027\u005C\u000A\u000D]')
STRING_LITERAL1 = Regex(STRING_LITERAL1_re)
                            
# [155]   EXPONENT          ::=   [eE] [+-]? [0-9]+ 
EXPONENT_re = r'[eE][+-][0-9]+'
EXPONENT = Regex(EXPONENT_re)

# [148]   DOUBLE    ::=   [0-9]+ '.' [0-9]* EXPONENT | '.' ([0-9])+ EXPONENT | ([0-9])+ EXPONENT 
DOUBLE_re = r'([0-9]+\.[0-9]*({}))|(\.[0-9]+({}))|([0-9]+({}))'.format(EXPONENT_re, EXPONENT_re, EXPONENT_re)
DOUBLE = Regex(DOUBLE_re)

# [154]   DOUBLE_NEGATIVE   ::=   '-' DOUBLE 
DOUBLE_NEGATIVE_re = r'\-({})'.format(DOUBLE_re)
DOUBLE_NEGATIVE = Regex(DOUBLE_NEGATIVE_re)

# [151]   DOUBLE_POSITIVE   ::=   '+' DOUBLE 
DOUBLE_POSITIVE_re = r'\+({})'.format(DOUBLE_re)
DOUBLE_POSITIVE = Regex(DOUBLE_POSITIVE_re)

# [147]   DECIMAL   ::=   [0-9]* '.' [0-9]+ 
DECIMAL_re = r'[0-9]*\.[0-9]+'
DECIMAL = Regex(DECIMAL_re)

# [153]   DECIMAL_NEGATIVE          ::=   '-' DECIMAL 
DECIMAL_NEGATIVE_re = r'\-({})'.format(DECIMAL_re)
DECIMAL_NEGATIVE = Regex(DECIMAL_NEGATIVE_re)

# [150]   DECIMAL_POSITIVE          ::=   '+' DECIMAL 
DECIMAL_POSITIVE_re = r'\+({})'.format(DECIMAL_re)
DECIMAL_POSITIVE = Regex(DECIMAL_POSITIVE_re)

# [146]   INTEGER   ::=   [0-9]+ 
INTEGER_re = r'[0-9]+'
INTEGER = Regex(INTEGER_re)

# [152]   INTEGER_NEGATIVE          ::=   '-' INTEGER
INTEGER_NEGATIVE_re = r'\-({})'.format(INTEGER_re)
INTEGER_NEGATIVE = Regex(INTEGER_NEGATIVE_re)

# [149]   INTEGER_POSITIVE          ::=   '+' INTEGER 
INTEGER_POSITIVE_re = r'\+({})'.format(INTEGER_re)
INTEGER_POSITIVE = Regex(INTEGER_POSITIVE_re)

# [145]   LANGTAG   ::=   '@' [a-zA-Z]+ ('-' [a-zA-Z0-9]+)* 
LANGTAG_re = r'@[a-zA-Z]+(\-[a-zA-Z0-9]+)*'
LANGTAG = Regex(LANGTAG_re)

# [144]   VAR2      ::=   '$' VARNAME 
VAR2_re = r'\$({})'.format(VARNAME_re)
VAR2 = Regex(VAR2_re)

# [143]   VAR1      ::=   '?' VARNAME 
VAR1_re = r'\?({})'.format(VARNAME_re)
VAR1 = Regex(VAR1_re)

# [142]   BLANK_NODE_LABEL          ::=   '_:' ( PN_CHARS_U | [0-9] ) ((PN_CHARS|'.')* PN_CHARS)?
BLANK_NODE_LABEL_re = r'_:(({})|[0-9])((({})|\.)*({}))?'.format(PN_CHARS_U_re, PN_CHARS_re, PN_CHARS_re)
BLANK_NODE_LABEL = Regex(BLANK_NODE_LABEL_re)

# [140]   PNAME_NS          ::=   PN_PREFIX? ':'
PNAME_NS_re = r'({})?:'.format(PN_PREFIX_re)
PNAME_NS = Regex(PNAME_NS_re)

# [141]   PNAME_LN          ::=   PNAME_NS PN_LOCAL 
PNAME_LN_re = r'({})({})'.format(PNAME_NS_re, PN_LOCAL_re)
PNAME_LN = Regex(PNAME_LN_re)

# [139]   IRIREF    ::=   '<' ([^<>"{}|^`\]-[#x00-#x20])* '>' 
IRIREF_re = r'<[^<>"{}|^`\\\\\u0000-\u0020]*>'
IRIREF = Regex(IRIREF_re)

#
# Productions for non-terminals
#

# Keywords
#
DISTINCT_kw = CaselessKeyword('DISTINCT')
COUNT_kw = CaselessKeyword('COUNT')
SUM_kw = CaselessKeyword('SUM')
MIN_kw = CaselessKeyword('MIN') 
MAX_kw = CaselessKeyword('MAX') 
AVG_kw = CaselessKeyword('AVG') 
SAMPLE_kw = CaselessKeyword('SAMPLE') 
GROUP_CONCAT_kw = CaselessKeyword('GROUP_CONCAT') 
SEPARATOR_kw = CaselessKeyword('SEPARATOR')
NOT_kw = CaselessKeyword('NOT')
EXISTS_kw = CaselessKeyword('EXISTS')
REPLACE_kw = CaselessKeyword('REPLACE')
SUBSTR_kw = CaselessKeyword('SUBSTR')
REGEX_kw = CaselessKeyword('REGEX')

# Brackets and separators
LPAR, RPAR, SEMICOL, COMMA = map(Suppress, '();,')


# [138]   BlankNode         ::=   BLANK_NODE_LABEL | ANON 
BlankNode = BLANK_NODE_LABEL ^ ANON

# [137]   PrefixedName      ::=   PNAME_LN | PNAME_NS 
PrefixedName = PNAME_LN ^ PNAME_NS

# [136]   iri       ::=   IRIREF | PrefixedName 
iri = IRIREF ^ PrefixedName

# [135]   String    ::=   STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 
String = STRING_LITERAL1 ^ STRING_LITERAL2 ^ STRING_LITERAL_LONG1 ^ STRING_LITERAL_LONG2
 
# [134]   BooleanLiteral    ::=   'true' | 'false' 
BooleanLiteral = Literal('true') | Literal('false')
 
# # [133]   NumericLiteralNegative    ::=   INTEGER_NEGATIVE | DECIMAL_NEGATIVE | DOUBLE_NEGATIVE 
NumericLiteralNegative = INTEGER_NEGATIVE ^ DECIMAL_NEGATIVE ^ DOUBLE_NEGATIVE 

# # [132]   NumericLiteralPositive    ::=   INTEGER_POSITIVE | DECIMAL_POSITIVE | DOUBLE_POSITIVE 
NumericLiteralPositive = INTEGER_POSITIVE ^ DECIMAL_POSITIVE ^ DOUBLE_POSITIVE 

# # [131]   NumericLiteralUnsigned    ::=   INTEGER | DECIMAL | DOUBLE 
NumericLiteralUnsigned = INTEGER ^ DECIMAL ^ DOUBLE
# 
# # [130]   NumericLiteral    ::=   NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative 
NumericLiteral = NumericLiteralUnsigned ^ NumericLiteralPositive ^ NumericLiteralNegative 

# [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
RDFLiteral = Combine( String + Optional( ( LANGTAG ^ ('^^' + iri) ) ) )

# TODO
Expression = Forward()
Expression << Literal('*Expression*')

# [71]    ArgList   ::=   NIL | '(' 'DISTINCT'? Expression ( ',' Expression )* ')' 
ArgList =   NIL ^ ( LPAR + Optional(DISTINCT_kw) + delimitedList(Expression) + RPAR )


# [128]   iriOrFunction     ::=   iri ArgList? 
iriOrFunction = iri + Optional(ArgList)

# [127]   Aggregate         ::=     'COUNT' '(' 'DISTINCT'? ( '*' | Expression ) ')' 
#             | 'SUM' '(' 'DISTINCT'? Expression ')' 
#             | 'MIN' '(' 'DISTINCT'? Expression ')' 
#             | 'MAX' '(' 'DISTINCT'? Expression ')' 
#             | 'AVG' '(' 'DISTINCT'? Expression ')' 
#             | 'SAMPLE' '(' 'DISTINCT'? Expression ')' 
#             | 'GROUP_CONCAT' '(' 'DISTINCT'? Expression ( ';' 'SEPARATOR' '=' String )? ')' 
Aggregate = ( COUNT_kw + LPAR + Optional(DISTINCT_kw) + ( Literal('*') ^ Expression ) + RPAR ) ^ \
            ( SUM_kw + LPAR + Optional(DISTINCT_kw) + ( Literal('*') ^ Expression ) + RPAR ) ^ \
            ( MIN_kw + LPAR + Optional(DISTINCT_kw) + ( Literal('*') ^ Expression ) + RPAR ) ^ \
            ( MAX_kw + LPAR + Optional(DISTINCT_kw) + ( Literal('*') ^ Expression ) + RPAR ) ^ \
            ( AVG_kw + LPAR + Optional(DISTINCT_kw) + ( Literal('*') ^ Expression ) + RPAR ) ^ \
            ( SAMPLE_kw + LPAR + Optional(DISTINCT_kw) + ( Literal('*') ^ Expression ) + RPAR ) ^ \
            ( GROUP_CONCAT_kw + LPAR + Optional(DISTINCT_kw) + Expression + Optional( SEMICOL + SEPARATOR_kw + '=' + String ) + RPAR )

# TODO
GroupGraphPattern = Forward()
GroupGraphPattern << Literal('*GroupGraphPattern*')

# [126]   NotExistsFunc     ::=   'NOT' 'EXISTS' GroupGraphPattern 
NotExistsFunc = NOT_kw + EXISTS_kw + GroupGraphPattern

# [125]   ExistsFunc        ::=   'EXISTS' GroupGraphPattern 
ExistsFunc = EXISTS_kw + GroupGraphPattern

# [124]   StrReplaceExpression      ::=   'REPLACE' '(' Expression ',' Expression ',' Expression ( ',' Expression )? ')' 
StrReplaceExpression = REPLACE_kw + LPAR + Expression + COMMA + Expression + COMMA + Expression + Optional(COMMA + Expression) + RPAR

# [123]   SubstringExpression       ::=   'SUBSTR' '(' Expression ',' Expression ( ',' Expression )? ')' 
SubstringExpression = SUBSTR_kw + LPAR + Expression + COMMA + Expression + Optional(COMMA + Expression) + RPAR

# [122]   RegexExpression   ::=   'REGEX' '(' Expression ',' Expression ( ',' Expression )? ')' 
RegexExpression = REGEX_kw + LPAR + Expression + COMMA + Expression + Optional(COMMA + Expression) + RPAR

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

# [120]   BrackettedExpression      ::=   '(' Expression ')' 

# [119]   PrimaryExpression         ::=   BrackettedExpression | BuiltInCall | iriOrFunction | RDFLiteral | NumericLiteral | BooleanLiteral | Var 

# [118]   UnaryExpression   ::=     '!' PrimaryExpression 

#             | '+' PrimaryExpression 

#             | '-' PrimaryExpression 

#             | PrimaryExpression 

# [117]   MultiplicativeExpression          ::=   UnaryExpression ( '*' UnaryExpression | '/' UnaryExpression )* 

# [116]   AdditiveExpression        ::=   MultiplicativeExpression ( '+' MultiplicativeExpression | '-' MultiplicativeExpression | ( NumericLiteralPositive | NumericLiteralNegative ) ( ( '*' UnaryExpression ) | ( '/' UnaryExpression ) )* )* 

# [115]   NumericExpression         ::=   AdditiveExpression 

# [114]   RelationalExpression      ::=   NumericExpression ( '=' NumericExpression | '!=' NumericExpression | '<' NumericExpression | '>' NumericExpression | '<=' NumericExpression | '>=' NumericExpression | 'IN' ExpressionList | 'NOT' 'IN' ExpressionList )? 

# [113]   ValueLogical      ::=   RelationalExpression 

# [112]   ConditionalAndExpression          ::=   ValueLogical ( '&&' ValueLogical )* 

# [111]   ConditionalOrExpression   ::=   ConditionalAndExpression ( '||' ConditionalAndExpression )* 

# [110]   Expression        ::=   ConditionalOrExpression 

# [109]   GraphTerm         ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | BlankNode | NIL 

# [108]   Var       ::=   VAR1 | VAR2 

# [107]   VarOrIri          ::=   Var | iri 

# [106]   VarOrTerm         ::=   Var | GraphTerm 

# [105]   GraphNodePath     ::=   VarOrTerm | TriplesNodePath 

# [104]   GraphNode         ::=   VarOrTerm | TriplesNode 

# [103]   CollectionPath    ::=   '(' GraphNodePath+ ')' 

# [102]   Collection        ::=   '(' GraphNode+ ')' 

# [101]   BlankNodePropertyListPath         ::=   '[' PropertyListPathNotEmpty ']' 

# [100]   TriplesNodePath   ::=   CollectionPath | BlankNodePropertyListPath 

# [99]    BlankNodePropertyList     ::=   '[' PropertyListNotEmpty ']' 

# [98]    TriplesNode       ::=   Collection | BlankNodePropertyList 

# [97]    Integer   ::=   INTEGER 

# [96]    PathOneInPropertySet      ::=   iri | 'a' | '^' ( iri | 'a' ) 

# [95]    PathNegatedPropertySet    ::=   PathOneInPropertySet | '(' ( PathOneInPropertySet ( '|' PathOneInPropertySet )* )? ')' 

# [94]    PathPrimary       ::=   iri | 'a' | '!' PathNegatedPropertySet | '(' Path ')' 

# [93]    PathMod   ::=   '?' | '*' | '+' 

# [92]    PathEltOrInverse          ::=   PathElt | '^' PathElt 

# [91]    PathElt   ::=   PathPrimary PathMod? 

# [90]    PathSequence      ::=   PathEltOrInverse ( '/' PathEltOrInverse )* 

# [89]    PathAlternative   ::=   PathSequence ( '|' PathSequence )* 

# [88]    Path      ::=   PathAlternative 

# [87]    ObjectPath        ::=   GraphNodePath 

# [86]    ObjectListPath    ::=   ObjectPath ( ',' ObjectPath )* 

# [85]    VerbSimple        ::=   Var 

# [84]    VerbPath          ::=   Path 

# [83]    PropertyListPathNotEmpty          ::=   ( VerbPath | VerbSimple ) ObjectListPath ( ';' ( ( VerbPath | VerbSimple ) ObjectList )? )* 

# [82]    PropertyListPath          ::=   PropertyListPathNotEmpty? 

# [81]    TriplesSameSubjectPath    ::=   VarOrTerm PropertyListPathNotEmpty | TriplesNodePath PropertyListPath 

# [80]    Object    ::=   GraphNode 

# [79]    ObjectList        ::=   Object ( ',' Object )* 

# [78]    Verb      ::=   VarOrIri | 'a' 

# [77]    PropertyListNotEmpty      ::=   Verb ObjectList ( ';' ( Verb ObjectList )? )* 

# [76]    PropertyList      ::=   PropertyListNotEmpty? 

# [75]    TriplesSameSubject        ::=   VarOrTerm PropertyListNotEmpty | TriplesNode PropertyList 

# [74]    ConstructTriples          ::=   TriplesSameSubject ( '.' ConstructTriples? )? 

# [73]    ConstructTemplate         ::=   '{' ConstructTriples? '}' 

# [72]    ExpressionList    ::=   NIL | '(' Expression ( ',' Expression )* ')' 

# [70]    FunctionCall      ::=   iri ArgList 

# [69]    Constraint        ::=   BrackettedExpression | BuiltInCall | FunctionCall 

# [68]    Filter    ::=   'FILTER' Constraint 

# [67]    GroupOrUnionGraphPattern          ::=   GroupGraphPattern ( 'UNION' GroupGraphPattern )* 

# [66]    MinusGraphPattern         ::=   'MINUS' GroupGraphPattern 

# [65]    DataBlockValue    ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | 'UNDEF' 

# [64]    InlineDataFull    ::=   ( NIL | '(' Var* ')' ) '{' ( '(' DataBlockValue* ')' | NIL )* '}' 

# [63]    InlineDataOneVar          ::=   Var '{' DataBlockValue* '}' 

# [62]    DataBlock         ::=   InlineDataOneVar | InlineDataFull 

# [61]    InlineData        ::=   'VALUES' DataBlock 

# [60]    Bind      ::=   'BIND' '(' Expression 'AS' Var ')' 

# [59]    ServiceGraphPattern       ::=   'SERVICE' 'SILENT'? VarOrIri GroupGraphPattern 

# [58]    GraphGraphPattern         ::=   'GRAPH' VarOrIri GroupGraphPattern 

# [57]    OptionalGraphPattern      ::=   'OPTIONAL' GroupGraphPattern 

# [56]    GraphPatternNotTriples    ::=   GroupOrUnionGraphPattern | OptionalGraphPattern | MinusGraphPattern | GraphGraphPattern | ServiceGraphPattern | Filter | Bind | InlineData 

# [55]    TriplesBlock      ::=   TriplesSameSubjectPath ( '.' TriplesBlock? )? 

# [54]    GroupGraphPatternSub      ::=   TriplesBlock? ( GraphPatternNotTriples '.'? TriplesBlock? )* 

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


if __name__ == '__main__':
    pass