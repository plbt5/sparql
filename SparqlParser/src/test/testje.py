'''
Created on 4 dec. 2015

@author: jeroenbruijning
'''
from pyparsing import ParseFatalException, Regex, Literal, Group, Optional,\
    Forward, CaselessKeyword, Suppress, ParseResults, delimitedList
import sys

if sys.version_info < (3,3):
    raise ParseFatalException('This parser only works with Python 3.3 or later (due to unicode handling issues)')


# Conversion of EBNF syntax for SPARQL 1.1 to pyparsing. For the grammar see http://www.w3.org/TR/sparql11-query/#grammar.

#
# Base classes for representative objects
#

class SPARQLNode():
    
    def __init__(self, pr):
        self.pr = pr
    def __str__(self):
        return ' <<< Class:' + self.__class__.__name__ + ', dict=' + str(self.__dict__) + ' >>> '
    __repr__ = __str__
    def render(self):
        raise NotImplementedError
    
            
class Terminal(SPARQLNode):
    
    def render(self):
        return ''.join([t for t in self.pr])
            
class NonTerminal(SPARQLNode):

    def render(self):
        reslist = []
        for t in self.pr:
            if isinstance(t, str):
                reslist.append(t)
            elif isinstance(t, Terminal):
                reslist.append(t.render())
            elif isinstance(t, NonTerminal):
                reslist.append(t.pr.render())
            else:
                assert isinstance(t, ParseResults)
                reslist.append(t.render())                
        return ' '.join(reslist)  
            

def dumpSPARQLNode(node, indent, depth=0):
    
    skip = indent * depth
    print(skip + '[' + node.__class__.__name__ + ']')
    if isinstance(node, Terminal):
        print(skip + node.render())
    else:
        assert isinstance(node, NonTerminal)
        dumpParseResults(node.pr, indent, depth + 1)


def dumpParseResults(pr, indent=' ', depth=0):
    skip = indent * depth
    for t in pr:
        if isinstance(t, ParseResults):
            try:
                label = ('>> ' + t.getName() + ': ' if t.getName() else '')
            except AttributeError:
                label = ''
            print(skip + label)
            dumpParseResults(t, indent, depth+1)
        elif isinstance(t, str):
            print(skip + t)
        else:
            assert isinstance(t, SPARQLNode)
            dumpSPARQLNode(t, indent, depth)
            
            
def renderSPARQLNode(node):
    if isinstance(node, Terminal):
        return node.render()
    else:
        assert isinstance(node, NonTerminal)
        return renderParseResults(node.pr)
     
     
def renderParseResults(pr):
    reslist = []
    for t in pr:
        if isinstance(t, str):
            reslist.append(t) 
        elif isinstance(t, SPARQLNode):
            reslist.append(renderSPARQLNode(t))
        else:
            assert isinstance(t, ParseResults)
            reslist.append(renderParseResults(t))
    return ' '.join(reslist)

# 
# Parsers and classes for terminals
#

# [173]   PN_LOCAL_ESC      ::=   '\' ( '_' | '~' | '.' | '-' | '!' | '$' | '&' | "'" | '(' | ')' | '*' | '+' | ',' | ';' | '=' | '/' | '?' | '#' | '@' | '%' ) 
PN_LOCAL_ESC_e = r'\\[_~.\-!$&\'()*+,;=/?#@%]'
PN_LOCAL_ESC_p = Regex(PN_LOCAL_ESC_e)
class PN_LOCAL_ESC(Terminal): pass
PN_LOCAL_ESC_p.setParseAction(PN_LOCAL_ESC)

# [172]   HEX       ::=   [0-9] | [A-F] | [a-f] 
HEX_e = r'[0-9A-Fa-f]'
HEX_p = Regex(HEX_e)
class HEX(Terminal): pass
HEX_p.setParseAction(HEX)

# [171]   PERCENT   ::=   '%' HEX HEX
PERCENT_e = r'%({})({})'.format( HEX_e, HEX_e)
PERCENT_p = Regex(PERCENT_e)
class PERCENT(Terminal):  pass
PERCENT_p.setParseAction(PERCENT)

# [170]   PLX       ::=   PERCENT | PN_LOCAL_ESC 
PLX_e = r'({})|({})'.format( PERCENT_e, PN_LOCAL_ESC_e)
PLX_p = Regex(PLX_e)
class PLX(Terminal): pass
PLX_p.setParseAction(PLX)

# [164]   PN_CHARS_BASE     ::=   [A-Z] | [a-z] | [#x00C0-#x00D6] | [#x00D8-#x00F6] | [#x00F8-#x02FF] | [#x0370-#x037D] | [#x037F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF] 
PN_CHARS_BASE_e = r'[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF]'
PN_CHARS_BASE_p = Regex(PN_CHARS_BASE_e)
class PN_CHARS_BASE(Terminal): pass
PN_CHARS_BASE_p.setParseAction(PN_CHARS_BASE)

# [165]   PN_CHARS_U        ::=   PN_CHARS_BASE | '_' 
PN_CHARS_U_e = r'({})|({})'.format( PN_CHARS_BASE_e, r'_')
PN_CHARS_U_p = Regex(PN_CHARS_U_e)
class PN_CHARS_U(Terminal): pass
PN_CHARS_U_p.setParseAction(PN_CHARS_U)

# [167]   PN_CHARS          ::=   PN_CHARS_U | '-' | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] 
PN_CHARS_e = r'({})|({})|({})|({})|({})|({})'.format( PN_CHARS_U_e, r'\-', r'[0-9]',  r'\u00B7', r'[\u0300-\u036F]', r'[\u203F-\u2040]')
PN_CHARS_p = Regex(PN_CHARS_e) 
class PN_CHARS(Terminal): pass
PN_CHARS_p.setParseAction(PN_CHARS)

# [169]   PN_LOCAL          ::=   (PN_CHARS_U | ':' | [0-9] | PLX ) ((PN_CHARS | '.' | ':' | PLX)* (PN_CHARS | ':' | PLX) )?
PN_LOCAL_e = r'(({})|({})|({})|({}))((({})|({})|({})|({}))*(({})|({})|({})))?'.format( PN_CHARS_U_e, r':', r'[0-9]', PLX_e, PN_CHARS_e, r'\.', r':', PLX_e, PN_CHARS_e, r':', PLX_e) 
PN_LOCAL_p = Regex(PN_LOCAL_e)
class PN_LOCAL(Terminal): pass
PN_LOCAL_p.setParseAction(PN_LOCAL)
            
# [168]   PN_PREFIX         ::=   PN_CHARS_BASE ((PN_CHARS|'.')* PN_CHARS)?
PN_PREFIX_e = r'({})((({})|({}))*({}))?'.format( PN_CHARS_BASE_e, PN_CHARS_e, r'\.', PN_CHARS_e)
PN_PREFIX_p = Regex(PN_PREFIX_e)
class PN_PREFIX(Terminal): pass
PN_PREFIX_p.setParseAction(PN_PREFIX)

# [166]   VARNAME   ::=   ( PN_CHARS_U | [0-9] ) ( PN_CHARS_U | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] )* 
VARNAME_e = r'(({})|({}))(({})|({})|({})|({})|({}))*'.format( PN_CHARS_U_e, r'[0-9]', PN_CHARS_U_e, r'[0-9]', r'\u00B7', r'[\u0030-036F]', r'[\u0203-\u2040]')
VARNAME_p = Regex(VARNAME_e)
class VARNAME(Terminal): pass
VARNAME_p.setParseAction(VARNAME)

# [163]   ANON      ::=   '[' WS* ']' 
ANON_p = Literal('[') + ']'
class ANON(Terminal): pass
ANON_p.setParseAction(ANON)

# [162]   WS        ::=   #x20 | #x9 | #xD | #xA 
# WS is not used
# In the SPARQL EBNF this production is used for defining NIL and ANON, but in this pyparsing implementation those are implemented differently

# [161]   NIL       ::=   '(' WS* ')' 
NIL_p = Literal('(') + ')'
class NIL(Terminal): pass
NIL_p.setParseAction(NIL)

# [160]   ECHAR     ::=   '\' [tbnrf\"']
ECHAR_e = r'\\[tbnrf\\"\']'
ECHAR_p = Regex(ECHAR_e) 
class ECHAR(Terminal): pass
ECHAR_p.setParseAction(ECHAR)
 
# [159]   STRING_LITERAL_LONG2      ::=   '"""' ( ( '"' | '""' )? ( [^"\] | ECHAR ) )* '"""'  
STRING_LITERAL_LONG2_e = r'"""((""|")?(({})|({})))*"""'.format(r'[^"\\]', ECHAR_e)
STRING_LITERAL_LONG2_p = Regex(STRING_LITERAL_LONG2_e)
class STRING_LITERAL_LONG2(Terminal): pass
STRING_LITERAL_LONG2_p.parseWithTabs()
STRING_LITERAL_LONG2_p.setParseAction(STRING_LITERAL_LONG2)

# [158]   STRING_LITERAL_LONG1      ::=   "'''" ( ( "'" | "''" )? ( [^'\] | ECHAR ) )* "'''" 
STRING_LITERAL_LONG1_e = r"'''(('|'')?(({})|({})))*'''".format(r"[^'\\]", ECHAR_e)
STRING_LITERAL_LONG1_p = Regex(STRING_LITERAL_LONG1_e)  
class STRING_LITERAL_LONG1(Terminal): pass
STRING_LITERAL_LONG1_p.parseWithTabs()
STRING_LITERAL_LONG1_p.setParseAction(STRING_LITERAL_LONG1)

# [157]   STRING_LITERAL2   ::=   '"' ( ([^#x22#x5C#xA#xD]) | ECHAR )* '"' 
STRING_LITERAL2_e = r'"(({})|({}))*"'.format(ECHAR_e, r'[^\u0022\u005C\u000A\u000D]')
STRING_LITERAL2_p = Regex(STRING_LITERAL2_e)
class STRING_LITERAL2(Terminal): pass
STRING_LITERAL2_p.parseWithTabs()
STRING_LITERAL2_p.setParseAction(STRING_LITERAL2)
                           
# [156]   STRING_LITERAL1   ::=   "'" ( ([^#x27#x5C#xA#xD]) | ECHAR )* "'" 
STRING_LITERAL1_e = r"'(({})|({}))*'".format(ECHAR_e, r'[^\u0027\u005C\u000A\u000D]')
STRING_LITERAL1_p = Regex(STRING_LITERAL1_e)
class STRING_LITERAL1(Terminal): pass
STRING_LITERAL1_p.parseWithTabs()
STRING_LITERAL1_p.setParseAction(STRING_LITERAL1)
                            
# [155]   EXPONENT          ::=   [eE] [+-]? [0-9]+ 
EXPONENT_e = r'[eE][+-][0-9]+'
EXPONENT_p = Regex(EXPONENT_e)
class EXPONENT(Terminal): pass
EXPONENT_p.setParseAction(EXPONENT)

# [148]   DOUBLE    ::=   [0-9]+ '.' [0-9]* EXPONENT | '.' ([0-9])+ EXPONENT | ([0-9])+ EXPONENT 
DOUBLE_e = r'([0-9]+\.[0-9]*({}))|(\.[0-9]+({}))|([0-9]+({}))'.format(EXPONENT_e, EXPONENT_e, EXPONENT_e)
DOUBLE_p = Regex(DOUBLE_e)
class DOUBLE(Terminal): pass
DOUBLE_p.setParseAction(DOUBLE)

# [154]   DOUBLE_NEGATIVE   ::=   '-' DOUBLE 
DOUBLE_NEGATIVE_e = r'\-({})'.format(DOUBLE_e)
DOUBLE_NEGATIVE_p = Regex(DOUBLE_NEGATIVE_e)
class DOUBLE_NEGATIVE(Terminal): pass
DOUBLE_NEGATIVE_p.setParseAction(DOUBLE_NEGATIVE)

# [151]   DOUBLE_POSITIVE   ::=   '+' DOUBLE 
DOUBLE_POSITIVE_e = r'\+({})'.format(DOUBLE_e)
DOUBLE_POSITIVE_p = Regex(DOUBLE_POSITIVE_e)
class DOUBLE_POSITIVE(Terminal): pass
DOUBLE_POSITIVE_p.setParseAction(DOUBLE_POSITIVE)

# [147]   DECIMAL   ::=   [0-9]* '.' [0-9]+ 
DECIMAL_e = r'[0-9]*\.[0-9]+'
DECIMAL_p = Regex(DECIMAL_e)
class DECIMAL(Terminal): pass
DECIMAL_p.setParseAction(DECIMAL)

# [153]   DECIMAL_NEGATIVE          ::=   '-' DECIMAL 
DECIMAL_NEGATIVE_e = r'\-({})'.format(DECIMAL_e)
DECIMAL_NEGATIVE_p = Regex(DECIMAL_NEGATIVE_e)
class DECIMAL_NEGATIVE(Terminal): pass
DECIMAL_NEGATIVE_p.setParseAction(DECIMAL_NEGATIVE)

# [150]   DECIMAL_POSITIVE          ::=   '+' DECIMAL 
DECIMAL_POSITIVE_e = r'\+({})'.format(DECIMAL_e)
DECIMAL_POSITIVE_p = Regex(DECIMAL_POSITIVE_e)
class DECIMAL_POSITIVE(Terminal): pass
DECIMAL_POSITIVE_p.setParseAction(DECIMAL_POSITIVE)

# [146]   INTEGER   ::=   [0-9]+ 
INTEGER_e = r'[0-9]+'
INTEGER_p = Regex(INTEGER_e)
class INTEGER(Terminal): pass
INTEGER_p.setParseAction(INTEGER)

# [152]   INTEGER_NEGATIVE          ::=   '-' INTEGER
INTEGER_NEGATIVE_e = r'\-({})'.format(INTEGER_e)
INTEGER_NEGATIVE_p = Regex(INTEGER_NEGATIVE_e)
class INTEGER_NEGATIVE(Terminal): pass
INTEGER_NEGATIVE_p.setParseAction(INTEGER_NEGATIVE)

# [149]   INTEGER_POSITIVE          ::=   '+' INTEGER 
INTEGER_POSITIVE_e = r'\+({})'.format(INTEGER_e)
INTEGER_POSITIVE_p = Regex(INTEGER_POSITIVE_e)
class INTEGER_POSITIVE(Terminal): pass
INTEGER_POSITIVE_p.setParseAction(INTEGER_POSITIVE)

# [145]   LANGTAG   ::=   '@' [a-zA-Z]+ ('-' [a-zA-Z0-9]+)* 
LANGTAG_e = r'@[a-zA-Z]+(\-[a-zA-Z0-9]+)*'
LANGTAG_p = Regex(LANGTAG_e)
class LANGTAG(Terminal): pass
LANGTAG_p.setParseAction(LANGTAG)

# [144]   VAR2      ::=   '$' VARNAME 
VAR2_e = r'\$({})'.format(VARNAME_e)
VAR2_p = Regex(VAR2_e)
class VAR2(Terminal): pass
VAR2_p.setParseAction(VAR2)

# [143]   VAR1      ::=   '?' VARNAME 
VAR1_e = r'\?({})'.format(VARNAME_e)
VAR1_p = Regex(VAR1_e)
class VAR1(Terminal): pass
VAR1_p.setParseAction(VAR1)

# [142]   BLANK_NODE_LABEL          ::=   '_:' ( PN_CHARS_U | [0-9] ) ((PN_CHARS|'.')* PN_CHARS)?
BLANK_NODE_LABEL_e = r'_:(({})|[0-9])((({})|\.)*({}))?'.format(PN_CHARS_U_e, PN_CHARS_e, PN_CHARS_e)
BLANK_NODE_LABEL_p = Regex(BLANK_NODE_LABEL_e)
class BLANK_NODE_LABEL(Terminal): pass
BLANK_NODE_LABEL_p.setParseAction(BLANK_NODE_LABEL)

# [140]   PNAME_NS          ::=   PN_PREFIX? ':'
PNAME_NS_e = r'({})?:'.format(PN_PREFIX_e)
PNAME_NS_p = Regex(PNAME_NS_e)
class PNAME_NS(Terminal): pass
PNAME_NS_p.setParseAction(PNAME_NS)

# [141]   PNAME_LN          ::=   PNAME_NS PN_LOCAL 
PNAME_LN_e = r'({})({})'.format(PNAME_NS_e, PN_LOCAL_e)
PNAME_LN_p = Regex(PNAME_LN_e)
class PNAME_LN(Terminal): pass
PNAME_LN_p.setParseAction(PNAME_LN)

# [139]   IRIREF    ::=   '<' ([^<>"{}|^`\]-[#x00-#x20])* '>' 
IRIREF_e = r'<[^<>"{}|^`\\\\\u0000-\u0020]*>'
IRIREF_p = Regex(IRIREF_e)
class IRIREF(Terminal): pass
IRIREF_p.setParseAction(IRIREF)

#
# Parsers and classes for non-terminals
#

# Keywords
#
DISTINCT_p = CaselessKeyword('DISTINCT')
# class DISTINCT(Terminal):
#     def render(self):
#         return 'DISTINCT'
# DISTINCT_p.setParseAction((DISTINCT))

COUNT_p = CaselessKeyword('COUNT')
SUM_p = CaselessKeyword('SUM')
MIN_p = CaselessKeyword('MIN') 
MAX_p = CaselessKeyword('MAX') 
AVG_p = CaselessKeyword('AVG') 
SAMPLE_p = CaselessKeyword('SAMPLE') 
GROUP_CONCAT_p = CaselessKeyword('GROUP_CONCAT') 
SEPARATOR_p = CaselessKeyword('SEPARATOR')
NOT_p = CaselessKeyword('NOT')
EXISTS_p = CaselessKeyword('EXISTS')
REPLACE_p = CaselessKeyword('REPLACE')
SUBSTR_p = CaselessKeyword('SUBSTR')
REGEX_p = CaselessKeyword('REGEX')

# Brackets and separators
LPAR_p, RPAR_p, SEMICOL_p, COMMA_p = '();,'

# [138]   BlankNode         ::=   BLANK_NODE_LABEL | ANON 
BlankNode_p = Group(BLANK_NODE_LABEL_p | ANON_p)('choice')
class BlankNode(NonTerminal): pass
BlankNode_p.setParseAction(BlankNode)

# [137]   PrefixedName      ::=   PNAME_LN | PNAME_NS 
PrefixedName_p = Group(PNAME_LN_p ^ PNAME_NS_p)('choice')
class PrefixedName(NonTerminal): pass
PrefixedName_p.setParseAction(PrefixedName)

# [136]   iri       ::=   IRIREF | PrefixedName 
iri_p = Group(IRIREF_p ^ PrefixedName_p)('choice')
class iri(NonTerminal): pass
iri_p.setParseAction(iri)

# [135]   String    ::=   STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 
String_p = Group(STRING_LITERAL1_p ^ STRING_LITERAL2_p ^ STRING_LITERAL_LONG1_p ^ STRING_LITERAL_LONG2_p)('choice')
class String(NonTerminal): pass
String_p.parseWithTabs()
String_p.setParseAction(String)
 
# [134]   BooleanLiteral    ::=   'true' | 'false' 
BooleanLiteral_p = Group(Literal('true') | Literal('false'))('choice')
class BooleanLiteral(NonTerminal): pass
BooleanLiteral_p.setParseAction(BooleanLiteral)
 
# # [133]   NumericLiteralNegative    ::=   INTEGER_NEGATIVE | DECIMAL_NEGATIVE | DOUBLE_NEGATIVE 
NumericLiteralNegative_p = Group(INTEGER_NEGATIVE_p ^ DECIMAL_NEGATIVE_p ^ DOUBLE_NEGATIVE_p)('choice') 
class NumericLiteralNegative(NonTerminal): pass
NumericLiteralNegative_p.setParseAction(NumericLiteralNegative)
 
# # [132]   NumericLiteralPositive    ::=   INTEGER_POSITIVE | DECIMAL_POSITIVE | DOUBLE_POSITIVE 
NumericLiteralPositive_p = Group(INTEGER_POSITIVE_p ^ DECIMAL_POSITIVE_p ^ DOUBLE_POSITIVE_p)('choice') 
class NumericLiteralPositive(NonTerminal): pass
NumericLiteralPositive_p.setParseAction(NumericLiteralPositive)
 
# # [131]   NumericLiteralUnsigned    ::=   INTEGER | DECIMAL | DOUBLE 
NumericLiteralUnsigned_p = Group(INTEGER_p ^ DECIMAL_p ^ DOUBLE_p)('choice')
class NumericLiteralUnsigned(NonTerminal): pass
NumericLiteralUnsigned_p.setParseAction(NumericLiteralUnsigned)
# 
# # [130]   NumericLiteral    ::=   NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative 
NumericLiteral_p = Group(NumericLiteralUnsigned_p ^ NumericLiteralPositive_p ^ NumericLiteralNegative_p)('choice') 
class NumericLiteral(NonTerminal): pass
NumericLiteral_p.setParseAction(NumericLiteral)

# [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
RDFLiteral_p = Group(String_p)('lexical_form') + Optional( Group ( ( LANGTAG_p ^ ('^^' + iri_p ) ) ) ('type_info') ) 
class RDFLiteral(NonTerminal): pass
#     def asString(self):
#         return self.joinChars()
#     def render(self):
#         if len(self.elements._fields) > 1 and isinstance(self.elements.E2_type_info[0][0], iri):
#             assert len(self.elements._fields) == 2
#             return NonTerminal.render(self, sep='^^')
#         else:
#             return NonTerminal.render(self, sep='')
RDFLiteral_p.setParseAction(RDFLiteral)


# TODO
Expression_p = Forward()
Expression_p << Group(Literal('*Expression*'))('exp')
class Expression(NonTerminal): pass
Expression_p.setParseAction(Expression)

# pattern and class to parse and render delimited Expression lists
expressionList_p = delimitedList(Expression_p)
class ExpressionList(NonTerminal):
#     def __init__(self, pr):
#         self.pr = pr
    def render(self):
        return ', '.join([v.render() for v in self.unpackParseResults(self.elements)])
expressionList_p.setParseAction(ExpressionList)
    
 
# [71]    ArgList   ::=   NIL | '(' 'DISTINCT'? Expression ( ',' Expression )* ')' 
ArgList_p =   Group(NIL_p)('nil') | Group( LPAR_p + Optional(DISTINCT_p)('F1') + expressionList_p('F2') + RPAR_p )('expression_list')
class ArgList(NonTerminal): pass
ArgList_p.setParseAction(ArgList)


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
# 
# # [126]   NotExistsFunc     ::=   'NOT' 'EXISTS' GroupGraphPattern 
NotExistsFunc_p = NOT_p + EXISTS_p + GroupGraphPattern_p
# 
# # [125]   ExistsFunc        ::=   'EXISTS' GroupGraphPattern 
ExistsFunc_p = EXISTS_p + GroupGraphPattern_p
# 
# # [124]   StrReplaceExpression      ::=   'REPLACE' '(' Expression ',' Expression ',' Expression ( ',' Expression )? ')' 
StrReplaceExpression_p = REPLACE_p + LPAR_p + Expression_p + COMMA_p + Expression_p + COMMA_p + Expression_p + Optional(COMMA_p + Expression_p) + RPAR_p
# 
# # [123]   SubstringExpression       ::=   'SUBSTR' '(' Expression ',' Expression ( ',' Expression )? ')' 
SubstringExpression_p = SUBSTR_p + LPAR_p + Expression_p + COMMA_p + Expression_p + Optional(COMMA_p + Expression_p) + RPAR_p
# 
# # [122]   RegexExpression   ::=   'REGEX' '(' Expression ',' Expression ( ',' Expression )? ')' 
RegexExpression_p = REGEX_p + LPAR_p + Expression_p + COMMA_p + Expression_p + Optional(COMMA_p + Expression_p) + RPAR_p


def printResults(l, rule):
    print('=' * 80)
    print(rule)
    print('=' * 80)
    for s in l:
        r = eval(rule + '_p').parseString(s)
        print('\nParse : {}'.format(s))
        print()
#         inspect(r[0])
#         print()
        dumpParseResults(r)
        print()
        rendering = renderParseResults(r)
        print('Render:', rendering)
        if s != rendering:
            print()
            print('+'* 80)
            print('Note: rendering (len={}) differs from input (len={})'.format(len(rendering), len(s)))
            print('+'* 80)
        print('\n' + '-'*80)
        
# # [173]   PN_LOCAL_ESC      ::=   '\' ( '_' | '~' | '.' | '-' | '!' | '$' | '&' | "'" | '(' | ')' | '*' | '+' | ',' | ';' | '=' | '/' | '?' | '#' | '@' | '%' ) 
# l = ['\\&']
# printResults(l, 'PN_LOCAL_ESC')
#            
# # [172]   HEX       ::=   [0-9] | [A-F] | [a-f] 
# l = ['D']
# printResults(l, 'HEX')
#              
# # [171]   PERCENT   ::=   '%' HEX HEX
# l = ['%F0']
# printResults(l, 'PERCENT')
#              
# # [170]   PLX       ::=   PERCENT | PN_LOCAL_ESC 
# l = ['%FA', '\\*']
# printResults(l, 'PLX')
#             
# # [164]   PN_CHARS_BASE     ::=   [A-Z] | [a-z] | [#x00C0-#x00D6] | [#x00D8-#x00F6] | [#x00F8-#x02FF] | [#x0370-#x037D] | [#x037F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF] 
# l = ['a', 'Z', '\u022D', '\u218F']
# printResults(l, 'PN_CHARS_BASE')
#             
# # [165]   PN_CHARS_U        ::=   PN_CHARS_BASE | '_' 
# l = ['a', 'Z', '\u022D', '\u218F', '_']
# printResults(l, 'PN_CHARS_U')
#             
# # # [167]   PN_CHARS          ::=   PN_CHARS_U | '-' | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] 
# l = ['a', 'Z', '\u022D', '\u218F', '_', '7', '\u203F']
# printResults(l, 'PN_CHARS')
#              
# # [169]   PN_LOCAL          ::=   (PN_CHARS_U | ':' | [0-9] | PLX ) ((PN_CHARS | '.' | ':' | PLX)* (PN_CHARS | ':' | PLX) )?
# l = ['aA', 'Z.a', '\u022D%FA.:', '\u218F0:']
# printResults(l, 'PN_LOCAL')
#             
# # [168]   PN_PREFIX         ::=   PN_CHARS_BASE ((PN_CHARS|'.')* PN_CHARS)?
# l = ['aA', 'Z.8', 'zDFA.-', '\u218F0']
# printResults(l, 'PN_PREFIX')
#             
# # [166]   VARNAME   ::=   ( PN_CHARS_U | [0-9] ) ( PN_CHARS_U | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] )* 
# l = ['aA', '8fes', '_zDFA', '9_\u218B7']
# # printResults(l, 'VARNAME')
#            
# # [163]   ANON      ::=   '[' WS* ']' 
# l = ['[]', '[ ]', '[\t]']
# printResults(l, 'ANON')
#           
# # [161]   NIL       ::=   '(' WS* ')' 
# l = ['()', '(    )', '(\t)']
# printResults(l, 'NIL')
#             
# # [160]   ECHAR     ::=   '\' [tbnrf\"']
# l = [r'\t', r'\"']
# printResults(l, 'ECHAR')
#             
# # [159]   STRING_LITERAL_LONG2      ::=   '"""' ( ( '"' | '""' )? ( [^"\] | ECHAR ) )* '"""'  
# l = ['"""abc def"\t ghi""x yz"""']
# printResults(l, 'STRING_LITERAL_LONG2')
#             
# # [158]   STRING_LITERAL_LONG1      ::=   "'''" ( ( "'" | "''" )? ( [^'\] | ECHAR ) )* "'''" 
# l = ["'''abc def'\t ghi''x yz'''"]
# printResults(l, 'STRING_LITERAL_LONG1')
#             
# # [157]   STRING_LITERAL2   ::=   '"' ( ([^#x22#x5C#xA#xD]) | ECHAR )* '"' 
# l = ['"abc d\'ef\t ghix yz"']
# printResults(l, 'STRING_LITERAL2')
#             
# # [156]   STRING_LITERAL1   ::=   "'" ( ([^#x27#x5C#xA#xD]) | ECHAR )* "'" 
# l = ["'abc d\"ef\t ghix yz'"]
# printResults(l, 'STRING_LITERAL1')
#             
# # [155]   EXPONENT          ::=   [eE] [+-]? [0-9]+ 
# l = ['e-12', 'E+13']
# printResults(l, 'EXPONENT')
#             
# # [148]   DOUBLE    ::=   [0-9]+ '.' [0-9]* EXPONENT | '.' ([0-9])+ EXPONENT | ([0-9])+ EXPONENT 
# l = ['088.77e+24', '.88e+24', '88e+24']
# printResults(l, 'DOUBLE')
#             
# # [154]   DOUBLE_NEGATIVE   ::=   '-' DOUBLE 
# l = ['-088.77e+24', '-.88e+24', '-88e+24']
# printResults(l, 'DOUBLE_NEGATIVE')
#             
# # [151]   DOUBLE_POSITIVE   ::=   '+' DOUBLE 
# l = ['+088.77e+24', '+.88e+24', '+88e+24']
# printResults(l, 'DOUBLE_POSITIVE')
#             
# # [147]   DECIMAL   ::=   [0-9]* '.' [0-9]+ 
# l = ['.33', '03.33']
# printResults(l, 'DECIMAL')
#             
# # [153]   DECIMAL_NEGATIVE          ::=   '-' DECIMAL 
# l = ['-.33', '-03.33']
# printResults(l, 'DECIMAL_NEGATIVE')
#             
# # [150]   DECIMAL_POSITIVE          ::=   '+' DECIMAL 
# l = ['+.33', '+03.33']
# printResults(l, 'DECIMAL_POSITIVE')
#             
# # [146]   INTEGER   ::=   [0-9]+ 
# l = ['33']
# printResults(l, 'INTEGER')
#             
# # [152]   INTEGER_NEGATIVE          ::=   '-' INTEGER
# l = ['-33']
# printResults(l, 'INTEGER_NEGATIVE')
#             
# # [149]   INTEGER_POSITIVE          ::=   '+' INTEGER 
# l = ['+33']
# printResults(l, 'INTEGER_POSITIVE')
#             
# # [145]   LANGTAG   ::=   '@' [a-zA-Z]+ ('-' [a-zA-Z0-9]+)* 
# l = ['@Test', '@Test-nl-be']
# printResults(l, 'LANGTAG')
#             
# # [144]   VAR2      ::=   '$' VARNAME 
# l = ['$aA', '$8fes', '$_zDFA', '$9_\u218B7']
# printResults(l, 'VAR2')
#             
# # [143]   VAR1      ::=   '?' VARNAME 
# l = ['?aA', '?8fes', '?_zDFA', '?9_\u218B7']
# printResults(l, 'VAR1')
#             
# # [142]   BLANK_NODE_LABEL          ::=   '_:' ( PN_CHARS_U | [0-9] ) ((PN_CHARS|'.')* PN_CHARS)?
# l = ['_:test9.33']
# printResults(l, 'BLANK_NODE_LABEL')
#             
# # [140]   PNAME_NS          ::=   PN_PREFIX? ':'
# l = ['aA:', 'Z.8:', ':']
# printResults(l, 'PNAME_NS')
#             
# # [141]   PNAME_LN          ::=   PNAME_NS PN_LOCAL 
# l = ['aA:Z.a', 'Z.8:AA']
# printResults(l, 'PNAME_LN')
#             
# # [139]   IRIREF    ::=   '<' ([^<>"{}|^`\]-[#x00-#x20])* '>' 
# l = ['<test:22?>']
# printResults(l, 'IRIREF')
#             
# # [138]   BlankNode         ::=   BLANK_NODE_LABEL | ANON 
# l = ['_:test9.33', '[ ]']
# printResults(l, 'BlankNode')
#             
# # [137]   PrefixedName      ::=   PNAME_LN | PNAME_NS 
# l = ['aA:Z.a', 'Z.8:AA', 'aA:', 'Z.8:', ':']
# printResults(l, 'PrefixedName')
#            
# # [136]   iri       ::=   IRIREF | PrefixedName 
# l = ['<test:22?>','aA:Z.a', 'Z.8:AA', 'aA:', 'Z.8:', ':']
# printResults(l, 'iri')
#           
# # [135]   String    ::=   STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 
# l = ['"""abc def"\t ghi""x yz"""', "'''abc def'\t ghi''x yz'''", '"abc d\'ef\t ghix yz"', '"abc d\'ef   ghix yz"', "'abc d\"ef\t ghix yz'"]
# printResults(l, 'String')
#           
# # [134]   BooleanLiteral    ::=   'true' | 'false' 
# l = ['true']
# printResults(l, 'BooleanLiteral')
#           
# # [133]   NumericLiteralNegative    ::=   INTEGER_NEGATIVE | DECIMAL_NEGATIVE | DOUBLE_NEGATIVE 
# l = ['-33', '-22.33', '-22.33e-44']
# printResults(l, 'NumericLiteralNegative')
#           
# # [132]   NumericLiteralPositive    ::=   INTEGER_POSITIVE | DECIMAL_POSITIVE | DOUBLE_POSITIVE 
# l = ['+33', '+22.33', '+22.33e-44']
# printResults(l, 'NumericLiteralPositive')
#           
# # [131]   NumericLiteralUnsigned    ::=   INTEGER | DECIMAL | DOUBLE 
# l = ['33', '22.33', '22.33e-44']
# printResults(l, 'NumericLiteralUnsigned')
#           
# # [130]   NumericLiteral    ::=   NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative 
# l = ['33', '+22.33', '-22.33e-44']
# printResults(l, 'NumericLiteral')
    
# [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
l = ['"test"', '"test" @en-bf', "'test' ^^ <test>", "'test'^^:"]
printResults(l, 'RDFLiteral')
     
# TODO: Expression
l = ['*Expression*']
printResults(l, 'Expression')
    
# [71]    ArgList   ::=   NIL | '(' 'DISTINCT'? Expression ( ',' Expression )* ')' 
# TODO
l = ['()', '( *Expression*) ', '(*Expression*, *Expression*)', '(DISTINCT *Expression*,  *Expression*,   *Expression* )']
printResults(l, 'ArgList')
    
# [128]   iriOrFunction     ::=   iri ArgList? 
l = ['<test:22?>','aA:Z.a', 'Z.8:AA', 'aA:', 'Z.8:', ':', '<test:22?>()','aA:Z.a (*Expression*)', 'Z.8:AA ( *Expression*, *Expression* )']
printResults(l, 'iriOrFunction')