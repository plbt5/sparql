from pyparsing import *
from sparqlparser.base import *

do_parseactions = True

def parseInfoFunc(classname):
    
    def keyedList(parseresults):
        valuedict = dict((id(t), k) for (k, t) in parseresults.items())
        assert len(valuedict) == len(list(parseresults.items())), 'internal error: len(valuedict) = {}, len(parseresults.items) = {}'.format(len(valuedict), len(list(parseresults.items)))
        result = []
        for t in parseresults:
            if isinstance(t, str):
                result.append([None, t])
                continue
            if isinstance(t, ParseInfo):
                result.append([valuedict.get(id(t)), t])
                continue
            assert isinstance(t, ParseResults), type(t)
            result.extend(keyedList(t))
        return result
    
    def makeparseinfo(parseresults):
        cls = globals()[classname]
        assert isinstance(parseresults, ParseResults)
        name = parseresults.getName()
        return cls(name, keyedList(parseresults))  
    
    return makeparseinfo

# 
# Parsers and classes for terminals
#

# [173]   PN_LOCAL_ESC      ::=   '\' ( '_' | '~' | '.' | '-' | '!' | '$' | '&' | "'" | '(' | ')' | '*' | '+' | ',' | ';' | '=' | '/' | '?' | '#' | '@' | '%' ) 
PN_LOCAL_ESC_e = r'\\[_~.\-!$&\'()*+,;=/?#@%]'
PN_LOCAL_ESC_p = Regex(PN_LOCAL_ESC_e)
class PN_LOCAL_ESC(SPARQLTerminal): 
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: PN_LOCAL_ESC_p.setParseAction(parseInfoFunc('PN_LOCAL_ESC'))


# [172]   HEX       ::=   [0-9] | [A-F] | [a-f] 
HEX_e = r'[0-9A-Fa-f]'
HEX_p = Regex(HEX_e)
class HEX(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: HEX_p.setParseAction(parseInfoFunc('HEX'))

# [171]   PERCENT   ::=   '%' HEX HEX
PERCENT_e = r'%({})({})'.format( HEX_e, HEX_e)
PERCENT_p = Regex(PERCENT_e)
class PERCENT(SPARQLTerminal):   
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: PERCENT_p.setParseAction(parseInfoFunc('PERCENT'))

# [170]   PLX       ::=   PERCENT | PN_LOCAL_ESC 
PLX_e = r'({})|({})'.format( PERCENT_e, PN_LOCAL_ESC_e)
PLX_p = Regex(PLX_e)
class PLX(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: PLX_p.setParseAction(parseInfoFunc('PLX'))

# [164]   PN_CHARS_BASE     ::=   [A-Z] | [a-z] | [#x00C0-#x00D6] | [#x00D8-#x00F6] | [#x00F8-#x02FF] | [#x0370-#x037D] | [#x037F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF] 
PN_CHARS_BASE_e = r'[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF]'
PN_CHARS_BASE_p = Regex(PN_CHARS_BASE_e)
class PN_CHARS_BASE(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: PN_CHARS_BASE_p.setParseAction(parseInfoFunc('PN_CHARS_BASE'))

# [165]   PN_CHARS_U        ::=   PN_CHARS_BASE | '_' 
PN_CHARS_U_e = r'({})|({})'.format( PN_CHARS_BASE_e, r'_')
PN_CHARS_U_p = Regex(PN_CHARS_U_e)
class PN_CHARS_U(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: PN_CHARS_U_p.setParseAction(parseInfoFunc('PN_CHARS_U'))

# [167]   PN_CHARS          ::=   PN_CHARS_U | '-' | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] 
PN_CHARS_e = r'({})|({})|({})|({})|({})|({})'.format( PN_CHARS_U_e, r'\-', r'[0-9]',  r'\u00B7', r'[\u0300-\u036F]', r'[\u203F-\u2040]')
PN_CHARS_p = Regex(PN_CHARS_e) 
class PN_CHARS(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: PN_CHARS_p.setParseAction(parseInfoFunc('PN_CHARS'))

# [169]   PN_LOCAL          ::=   (PN_CHARS_U | ':' | [0-9] | PLX ) ((PN_CHARS | '.' | ':' | PLX)* (PN_CHARS | ':' | PLX) )?
PN_LOCAL_e = r'(({})|({})|({})|({}))((({})|({})|({})|({}))*(({})|({})|({})))?'.format( PN_CHARS_U_e, r':', r'[0-9]', PLX_e, PN_CHARS_e, r'\.', r':', PLX_e, PN_CHARS_e, r':', PLX_e) 
PN_LOCAL_p = Regex(PN_LOCAL_e)
class PN_LOCAL(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: PN_LOCAL_p.setParseAction(parseInfoFunc('PN_LOCAL'))
            
# [168]   PN_PREFIX         ::=   PN_CHARS_BASE ((PN_CHARS|'.')* PN_CHARS)?
PN_PREFIX_e = r'({})((({})|({}))*({}))?'.format( PN_CHARS_BASE_e, PN_CHARS_e, r'\.', PN_CHARS_e)
PN_PREFIX_p = Regex(PN_PREFIX_e)
class PN_PREFIX(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: PN_PREFIX_p.setParseAction(parseInfoFunc('PN_PREFIX'))

# [166]   VARNAME   ::=   ( PN_CHARS_U | [0-9] ) ( PN_CHARS_U | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] )* 
VARNAME_e = r'(({})|({}))(({})|({})|({})|({})|({}))*'.format( PN_CHARS_U_e, r'[0-9]', PN_CHARS_U_e, r'[0-9]', r'\u00B7', r'[\u0030-036F]', r'[\u0203-\u2040]')
VARNAME_p = Regex(VARNAME_e)
class VARNAME(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: VARNAME_p.setParseAction(parseInfoFunc('VARNAME'))

# [163]   ANON      ::=   '[' WS* ']' 
ANON_p = Literal('[') + ']'
class ANON(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: ANON_p.setParseAction(parseInfoFunc('ANON'))

# [162]   WS        ::=   #x20 | #x9 | #xD | #xA 
# WS is not used
# In the SPARQL EBNF this production is used for defining NIL and ANON, but in this pyparsing implementation those are implemented differently

# [161]   NIL       ::=   '(' WS* ')' 
NIL_p = Literal('(') + ')'
class NIL(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: NIL_p.setParseAction(parseInfoFunc('NIL'))

# [160]   ECHAR     ::=   '\' [tbnrf\"']
ECHAR_e = r'\\[tbnrf\\"\']'
ECHAR_p = Regex(ECHAR_e) 
class ECHAR(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: ECHAR_p.setParseAction(parseInfoFunc('ECHAR'))
 
# [159]   STRING_LITERAL_LONG2      ::=   '"""' ( ( '"' | '""' )? ( [^"\] | ECHAR ) )* '"""'  
STRING_LITERAL_LONG2_e = r'"""((""|")?(({})|({})))*"""'.format(r'[^"\\]', ECHAR_e)
STRING_LITERAL_LONG2_p = Regex(STRING_LITERAL_LONG2_e)
class STRING_LITERAL_LONG2(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
STRING_LITERAL_LONG2_p.parseWithTabs()
if do_parseactions: STRING_LITERAL_LONG2_p.setParseAction(parseInfoFunc('STRING_LITERAL_LONG2'))

# [158]   STRING_LITERAL_LONG1      ::=   "'''" ( ( "'" | "''" )? ( [^'\] | ECHAR ) )* "'''" 
STRING_LITERAL_LONG1_e = r"'''(('|'')?(({})|({})))*'''".format(r"[^'\\]", ECHAR_e)
STRING_LITERAL_LONG1_p = Regex(STRING_LITERAL_LONG1_e)  
class STRING_LITERAL_LONG1(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
STRING_LITERAL_LONG1_p.parseWithTabs()
if do_parseactions: STRING_LITERAL_LONG1_p.setParseAction(parseInfoFunc('STRING_LITERAL_LONG1'))

# [157]   STRING_LITERAL2   ::=   '"' ( ([^#x22#x5C#xA#xD]) | ECHAR )* '"' 
STRING_LITERAL2_e = r'"(({})|({}))*"'.format(ECHAR_e, r'[^\u0022\u005C\u000A\u000D]')
STRING_LITERAL2_p = Regex(STRING_LITERAL2_e)
class STRING_LITERAL2(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
STRING_LITERAL2_p.parseWithTabs()
if do_parseactions: STRING_LITERAL2_p.setParseAction(parseInfoFunc('STRING_LITERAL2'))
                           
# [156]   STRING_LITERAL1   ::=   "'" ( ([^#x27#x5C#xA#xD]) | ECHAR )* "'" 
STRING_LITERAL1_e = r"'(({})|({}))*'".format(ECHAR_e, r'[^\u0027\u005C\u000A\u000D]')
STRING_LITERAL1_p = Regex(STRING_LITERAL1_e)
class STRING_LITERAL1(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
STRING_LITERAL1_p.parseWithTabs()
if do_parseactions: STRING_LITERAL1_p.setParseAction(parseInfoFunc('STRING_LITERAL1'))
                            
# [155]   EXPONENT          ::=   [eE] [+-]? [0-9]+ 
EXPONENT_e = r'[eE][+-][0-9]+'
EXPONENT_p = Regex(EXPONENT_e)
class EXPONENT(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: EXPONENT_p.setParseAction(parseInfoFunc('EXPONENT'))

# [148]   DOUBLE    ::=   [0-9]+ '.' [0-9]* EXPONENT | '.' ([0-9])+ EXPONENT | ([0-9])+ EXPONENT 
DOUBLE_e = r'([0-9]+\.[0-9]*({}))|(\.[0-9]+({}))|([0-9]+({}))'.format(EXPONENT_e, EXPONENT_e, EXPONENT_e)
DOUBLE_p = Regex(DOUBLE_e)
class DOUBLE(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: DOUBLE_p.setParseAction(parseInfoFunc('DOUBLE'))

# [154]   DOUBLE_NEGATIVE   ::=   '-' DOUBLE 
DOUBLE_NEGATIVE_e = r'\-({})'.format(DOUBLE_e)
DOUBLE_NEGATIVE_p = Regex(DOUBLE_NEGATIVE_e)
class DOUBLE_NEGATIVE(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: DOUBLE_NEGATIVE_p.setParseAction(parseInfoFunc('DOUBLE_NEGATIVE'))

# [151]   DOUBLE_POSITIVE   ::=   '+' DOUBLE 
DOUBLE_POSITIVE_e = r'\+({})'.format(DOUBLE_e)
DOUBLE_POSITIVE_p = Regex(DOUBLE_POSITIVE_e)
class DOUBLE_POSITIVE(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: DOUBLE_POSITIVE_p.setParseAction(parseInfoFunc('DOUBLE_POSITIVE'))

# [147]   DECIMAL   ::=   [0-9]* '.' [0-9]+ 
DECIMAL_e = r'[0-9]*\.[0-9]+'
DECIMAL_p = Regex(DECIMAL_e)
class DECIMAL(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: DECIMAL_p.setParseAction(parseInfoFunc('DECIMAL'))

# [153]   DECIMAL_NEGATIVE          ::=   '-' DECIMAL 
DECIMAL_NEGATIVE_e = r'\-({})'.format(DECIMAL_e)
DECIMAL_NEGATIVE_p = Regex(DECIMAL_NEGATIVE_e)
class DECIMAL_NEGATIVE(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: DECIMAL_NEGATIVE_p.setParseAction(parseInfoFunc('DECIMAL_NEGATIVE'))

# [150]   DECIMAL_POSITIVE          ::=   '+' DECIMAL 
DECIMAL_POSITIVE_e = r'\+({})'.format(DECIMAL_e)
DECIMAL_POSITIVE_p = Regex(DECIMAL_POSITIVE_e)
class DECIMAL_POSITIVE(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: DECIMAL_POSITIVE_p.setParseAction(parseInfoFunc('DECIMAL_POSITIVE'))

# [146]   INTEGER   ::=   [0-9]+ 
INTEGER_e = r'[0-9]+'
INTEGER_p = Regex(INTEGER_e)
class INTEGER(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: INTEGER_p.setParseAction(parseInfoFunc('INTEGER'))

# [152]   INTEGER_NEGATIVE          ::=   '-' INTEGER
INTEGER_NEGATIVE_e = r'\-({})'.format(INTEGER_e)
INTEGER_NEGATIVE_p = Regex(INTEGER_NEGATIVE_e)
class INTEGER_NEGATIVE(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: INTEGER_NEGATIVE_p.setParseAction(parseInfoFunc('INTEGER_NEGATIVE'))

# [149]   INTEGER_POSITIVE          ::=   '+' INTEGER 
INTEGER_POSITIVE_e = r'\+({})'.format(INTEGER_e)
INTEGER_POSITIVE_p = Regex(INTEGER_POSITIVE_e)
class INTEGER_POSITIVE(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: INTEGER_POSITIVE_p.setParseAction(parseInfoFunc('INTEGER_POSITIVE'))

# [145]   LANGTAG   ::=   '@' [a-zA-Z]+ ('-' [a-zA-Z0-9]+)* 
LANGTAG_e = r'@[a-zA-Z]+(\-[a-zA-Z0-9]+)*'
LANGTAG_p = Regex(LANGTAG_e)
class LANGTAG(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: LANGTAG_p.setParseAction(parseInfoFunc('LANGTAG'))

# [144]   VAR2      ::=   '$' VARNAME 
VAR2_e = r'\$({})'.format(VARNAME_e)
VAR2_p = Regex(VAR2_e)
class VAR2(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: VAR2_p.setParseAction(parseInfoFunc('VAR2'))

# [143]   VAR1      ::=   '?' VARNAME 
VAR1_e = r'\?({})'.format(VARNAME_e)
VAR1_p = Regex(VAR1_e)
class VAR1(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: VAR1_p.setParseAction(parseInfoFunc('VAR1'))

# [142]   BLANK_NODE_LABEL          ::=   '_:' ( PN_CHARS_U | [0-9] ) ((PN_CHARS|'.')* PN_CHARS)?
BLANK_NODE_LABEL_e = r'_:(({})|[0-9])((({})|\.)*({}))?'.format(PN_CHARS_U_e, PN_CHARS_e, PN_CHARS_e)
BLANK_NODE_LABEL_p = Regex(BLANK_NODE_LABEL_e)
class BLANK_NODE_LABEL(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: BLANK_NODE_LABEL_p.setParseAction(parseInfoFunc('BLANK_NODE_LABEL'))

# [140]   PNAME_NS          ::=   PN_PREFIX? ':'
PNAME_NS_e = r'({})?:'.format(PN_PREFIX_e)
PNAME_NS_p = Regex(PNAME_NS_e)
class PNAME_NS(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: PNAME_NS_p.setParseAction(parseInfoFunc('PNAME_NS'))

# [141]   PNAME_LN          ::=   PNAME_NS PN_LOCAL 
PNAME_LN_e = r'({})({})'.format(PNAME_NS_e, PN_LOCAL_e)
PNAME_LN_p = Regex(PNAME_LN_e)
class PNAME_LN(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: PNAME_LN_p.setParseAction(parseInfoFunc('PNAME_LN'))

# [139]   IRIREF    ::=   '<' ([^<>"{}|^`\]-[#x00-#x20])* '>' 
IRIREF_e = r'<[^<>"{}|^`\\\\\u0000-\u0020]*>'
IRIREF_p = Regex(IRIREF_e)
class IRIREF(SPARQLTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: IRIREF_p.setParseAction(parseInfoFunc('IRIREF'))

#
# Parsers and classes for non-terminals
#

# Keywords
#
DISTINCT_p = CaselessKeyword('DISTINCT')
class DISTINCT(SPARQLKeyword):
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
    def render(self):
        return 'DISTINCT'
DISTINCT_p.setParseAction(parseInfoFunc('DISTINCT'))

COUNT_p = CaselessKeyword('COUNT')
class COUNT(SPARQLKeyword):
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
    def render(self):
        return 'COUNT'
COUNT_p.setParseAction(parseInfoFunc('COUNT'))

SUM_p = CaselessKeyword('SUM')
class SUM(SPARQLKeyword):
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
    def render(self):
        return 'SUM'
SUM_p.setParseAction(parseInfoFunc('SUM'))

MIN_p = CaselessKeyword('MIN') 
class MIN(SPARQLKeyword):
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
    def render(self):
        return 'MIN'
MIN_p.setParseAction(parseInfoFunc('MIN'))

MAX_p = CaselessKeyword('MAX') 
class MAX(SPARQLKeyword):
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
    def render(self):
        return 'MAX'
MAX_p.setParseAction(parseInfoFunc('MAX'))

AVG_p = CaselessKeyword('AVG') 
class AVG(SPARQLKeyword):
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
    def render(self):
        return 'AVG'
AVG_p.setParseAction(parseInfoFunc('AVG'))

SAMPLE_p = CaselessKeyword('SAMPLE') 
class SAMPLE(SPARQLKeyword):
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
    def render(self):
        return 'SAMPLE'
SAMPLE_p.setParseAction(parseInfoFunc('SAMPLE'))

GROUP_CONCAT_p = CaselessKeyword('GROUP_CONCAT') 
class GROUP_CONCAT(SPARQLKeyword):
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
    def render(self):
        return 'GROUP_CONCAT'
GROUP_CONCAT_p.setParseAction(parseInfoFunc('GROUP_CONCAT'))

SEPARATOR_p = CaselessKeyword('SEPARATOR')
class SEPARATOR(SPARQLKeyword):
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
    def render(self):
        return 'SEPARATOR'
SEPARATOR_p.setParseAction(parseInfoFunc('SEPARATOR'))

NOT_p = CaselessKeyword('NOT')
class NOT(SPARQLKeyword):
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
    def render(self):
        return 'NOT'
NOT_p.setParseAction(parseInfoFunc('NOT'))

EXISTS_p = CaselessKeyword('EXISTS')
class EXISTS(SPARQLKeyword):
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
    def render(self):
        return 'EXISTS'
EXISTS_p.setParseAction(parseInfoFunc('EXISTS'))

REPLACE_p = CaselessKeyword('REPLACE')
class REPLACE(SPARQLKeyword):
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
    def render(self):
        return 'REPLACE'
REPLACE_p.setParseAction(parseInfoFunc('REPLACE'))

SUBSTR_p = CaselessKeyword('SUBSTR')
class SUBSTR(SPARQLKeyword):
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
    def render(self):
        return 'SUBSTR'
SUBSTR_p.setParseAction(parseInfoFunc('SUBSTR'))

REGEX_p = CaselessKeyword('REGEX')
class REGEX(SPARQLKeyword):
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
    def render(self):
        return 'REGEX'
REGEX_p.setParseAction(parseInfoFunc('REGEX'))

# Brackets and separators
LPAR_p, RPAR_p, SEMICOL_p, COMMA_p = '();,'

# [138]   BlankNode         ::=   BLANK_NODE_LABEL | ANON 
BlankNode_p = BLANK_NODE_LABEL_p | ANON_p
class BlankNode(SPARQLNonTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: BlankNode_p.setParseAction(parseInfoFunc('BlankNode'))

# [137]   PrefixedName      ::=   PNAME_LN | PNAME_NS 
PrefixedName_p = Group(PNAME_LN_p ^ PNAME_NS_p)
class PrefixedName(SPARQLNonTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: PrefixedName_p.setParseAction(parseInfoFunc('PrefixedName'))

# [136]   iri       ::=   IRIREF | PrefixedName 
iri_p = IRIREF_p ^ PrefixedName_p
class iri(SPARQLNonTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: iri_p.setParseAction(parseInfoFunc('iri'))

# [135]   String    ::=   STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 
String_p = (STRING_LITERAL1_p ^ STRING_LITERAL2_p ^ STRING_LITERAL_LONG1_p ^ STRING_LITERAL_LONG2_p)
class String(SPARQLNonTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
String_p.parseWithTabs()
if do_parseactions: String_p.setParseAction(parseInfoFunc('String'))
 
# [134]   BooleanLiteral    ::=   'true' | 'false' 
BooleanLiteral_p = Group(Literal('true') | Literal('false'))
class BooleanLiteral(SPARQLNonTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: BooleanLiteral_p.setParseAction(parseInfoFunc('BooleanLiteral'))
 
# # [133]   NumericLiteralNegative    ::=   INTEGER_NEGATIVE | DECIMAL_NEGATIVE | DOUBLE_NEGATIVE 
NumericLiteralNegative_p = Group(INTEGER_NEGATIVE_p ^ DECIMAL_NEGATIVE_p ^ DOUBLE_NEGATIVE_p)
class NumericLiteralNegative(SPARQLNonTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: NumericLiteralNegative_p.setParseAction(parseInfoFunc('NumericLiteralNegative'))
 
# # [132]   NumericLiteralPositive    ::=   INTEGER_POSITIVE | DECIMAL_POSITIVE | DOUBLE_POSITIVE 
NumericLiteralPositive_p = Group(INTEGER_POSITIVE_p ^ DECIMAL_POSITIVE_p ^ DOUBLE_POSITIVE_p)
class NumericLiteralPositive(SPARQLNonTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: NumericLiteralPositive_p.setParseAction(parseInfoFunc('NumericLiteralPositive'))
 
# # [131]   NumericLiteralUnsigned    ::=   INTEGER | DECIMAL | DOUBLE 
NumericLiteralUnsigned_p = Group(INTEGER_p ^ DECIMAL_p ^ DOUBLE_p)
class NumericLiteralUnsigned(SPARQLNonTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: NumericLiteralUnsigned_p.setParseAction(parseInfoFunc('NumericLiteralUnsigned'))
# 
# # [130]   NumericLiteral    ::=   NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative 
NumericLiteral_p = Group(NumericLiteralUnsigned_p ^ NumericLiteralPositive_p ^ NumericLiteralNegative_p)
class NumericLiteral(SPARQLNonTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: NumericLiteral_p.setParseAction(parseInfoFunc('NumericLiteral'))

# [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
RDFLiteral_p = (
                     Group(String_p('lexical_form')) \
                     + Optional(
                                Group (
                                       (
                                        LANGTAG_p('langtag') \
                                        ^ \
                                        ('^^' + iri_p('datatype'))('caps')
                                        )
                                       )
                                )
                     )
class RDFLiteral(SPARQLNonTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: RDFLiteral_p.setParseAction(parseInfoFunc('RDFLiteral'))


# TODO
Expression_p = Forward()
Expression_p << Group(Literal('*Expression*'))
class Expression(SPARQLNonTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: Expression_p.setParseAction(parseInfoFunc('Expression'))

# pattern and class to parse and render delimited Expression lists
ExpressionList_p = delimitedList(Expression_p)
class ExpressionList(SPARQLNonTerminal):
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
    def render(self):
        return ', '.join([v[1] if isinstance(v[1], str) else v[1].render() for v in self.getItems()])
if do_parseactions: ExpressionList_p.setParseAction(parseInfoFunc('ExpressionList'))
    
 
# [71]    ArgList   ::=   NIL | '(' 'DISTINCT'? Expression ( ',' Expression )* ')' 
ArgList_p = Group(NIL_p('nil')) | (LPAR_p + Optional(Group(DISTINCT_p('distinct'))) + Group(ExpressionList_p('expression_list')) + RPAR_p)
class ArgList(SPARQLNonTerminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
if do_parseactions: ArgList_p.setParseAction(parseInfoFunc('ArgList'))


# [128]   iriOrFunction     ::=   iri ArgList? 
iriOrFunction_p = iri_p('iri') + Optional(Group(ArgList_p))('ArgList')

# [127]   Aggregate         ::=     'COUNT' '(' 'DISTINCT'? ( '*' | Expression ) ')' 
#             | 'SUM' '(' 'DISTINCT'? Expression ')' 
#             | 'MIN' '(' 'DISTINCT'? Expression ')' 
#             | 'MAX' '(' 'DISTINCT'? Expression ')' 
#             | 'AVG' '(' 'DISTINCT'? Expression ')' 
#             | 'SAMPLE' '(' 'DISTINCT'? Expression ')' 
#             | 'GROUP_CONCAT' '(' 'DISTINCT'? Expression ( ';' 'SEPARATOR' '=' String )? ')' 
Aggregate_p = ( COUNT_p + LPAR_p + Optional(DISTINCT_p) + ( Literal('*') ^ Expression_p ) + RPAR_p ) ^ \
            ( SUM_p + LPAR_p + Optional(DISTINCT_p) + ( Literal('*') ^ Expression_p ) + RPAR_p ) ^ \
            ( MIN_p + LPAR_p + Optional(DISTINCT_p) + ( Literal('*') ^ Expression_p ) + RPAR_p ) ^ \
            ( MAX_p + LPAR_p + Optional(DISTINCT_p) + ( Literal('*') ^ Expression_p ) + RPAR_p ) ^ \
            ( AVG_p + LPAR_p + Optional(DISTINCT_p) + ( Literal('*') ^ Expression_p ) + RPAR_p ) ^ \
            ( SAMPLE_p + LPAR_p + Optional(DISTINCT_p) + ( Literal('*') ^ Expression_p ) + RPAR_p ) ^ \
            ( GROUP_CONCAT_p + LPAR_p + Optional(DISTINCT_p) + Expression_p + Optional( SEMICOL_p + SEPARATOR_p + '=' + String_p ) + RPAR_p )

# # TODO
GroupGraphPattern_p = Forward()
GroupGraphPattern_p << Literal('*GroupGraphPattern*')
 
# [126]   NotExistsFunc     ::=   'NOT' 'EXISTS' GroupGraphPattern 
NotExistsFunc_p = NOT_p + EXISTS_p + GroupGraphPattern_p
 
# [125]   ExistsFunc        ::=   'EXISTS' GroupGraphPattern 
ExistsFunc_p = EXISTS_p + GroupGraphPattern_p
 
# [124]   StrReplaceExpression      ::=   'REPLACE' '(' Expression ',' Expression ',' Expression ( ',' Expression )? ')' 
StrReplaceExpression_p = REPLACE_p + LPAR_p + Expression_p + COMMA_p + Expression_p + COMMA_p + Expression_p + Optional(COMMA_p + Expression_p) + RPAR_p
 
# [123]   SubstringExpression       ::=   'SUBSTR' '(' Expression ',' Expression ( ',' Expression )? ')' 
SubstringExpression_p = SUBSTR_p + LPAR_p + Expression_p + COMMA_p + Expression_p + Optional(COMMA_p + Expression_p) + RPAR_p
 
# [122]   RegexExpression   ::=   'REGEX' '(' Expression ',' Expression ( ',' Expression )? ')' 
RegexExpression_p = REGEX_p + LPAR_p + Expression_p + COMMA_p + Expression_p + Optional(COMMA_p + Expression_p) + RPAR_p
 
# [122]   RegexExpression   ::=   'REGEX' '(' Expression ',' Expression ( ',' Expression )? ')' 
RegexExpression_p = REGEX_p + LPAR_p + Expression_p + COMMA_p + Expression_p + Optional(COMMA_p + Expression_p) + RPAR_p

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
