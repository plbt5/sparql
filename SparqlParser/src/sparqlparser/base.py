from pyparsing import *
from sparqlparser import do_parseactions

# Parser for SPARQL 1.1, based on its EBNF syntax and using pyparsing.
# For the grammar see http://www.w3.org/TR/sparql11-query/#grammar.

#
# Base classes for representative objects
#

# do_parseactions = False

class ParsePattern(type):
    def __new__(cls, name, bases, namespace, **kwds):
        result = type.__new__(cls, name, bases, dict(namespace))
        try:
            result.pattern = eval(name+'_p')
        except NameError:
            result.pattern = None
        return result
    
class ParseInfo(metaclass=ParsePattern):
    
    def __init__(self, *args):
        if len(args) == 2:
            self.__dict__['name'] = args[0] 
            self.__dict__['items'] = args[1] 
        else:
            assert len(args) == 1 and isinstance(args[0], str)
            self.__dict__['name'] = None
            self.__dict__['items'] = self.__getPattern().parseString(args[0], parseAll=True)[0].items
        assert self.__isKeyConsistent()
                
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.name == other.name and self.items == other.items
    
    def __getattr__(self, key):
        if key in self.getKeys():
            values = self.getValuesForKey(key)
            assert len(values) == 1
            return values[0] 
        else:
            raise AttributeError('Unknown key: {}'.format(key))
#     
    def __setattr__(self, key, value):
        if key in self.getKeys():
            items = self.getItemsForKey(key)
            assert len(items) == 1
            assert items[0][0] == key
            value.__dict__['name'] = items[0][0]
            items[0][1] = value     
            assert self.__isKeyConsistent()               
        else:
            raise AttributeError('Unknown key: {}'.format(key))
   
    def __isKeyConsistent(self):
        return all([t[0] == t[1].name if isinstance(t[1], ParseInfo) else t[0] == None if isinstance(t[1], str) else False for t in self.getItems()])

    def __getPattern(self):
        return self.__class__.pattern
        
    def __copyItems(self):
        result = []
        for k, v in self.items:
            if isinstance(v, str):
                result.append([k, v])
            else:
                assert isinstance(v, ParseInfo)
                result.append([k, v.copy()])
        return result
        
    def copy(self):
        result = globals()[self.__class__.__name__](self.name, self.__copyItems())
        assert result == self
        return result
    
    def test(self, render=False, dump=False):
        print('{} is{}internally key-consistent'.format(self, ' ' if self.__isKeyConsistent() else ' not '))
        print('{} renders a{}expression'.format(self, ' valid ' if self.yieldsValidExpression() else 'n invalid '))
        print('{} is a{}valid parse object'.format(self, ' ' if self.isValid() else ' not '))
        if render:
            print('--rendering:')
            print(self.render())
        if dump:
            print('--dump:')
            self.dump()
    
    def assignPattern(self):
        raise NotImplementedError

    def getName(self):
        return self.name
    
    def getItems(self):
        return self.items
    
    def getValues(self):
        return [i[1] for i in self.getItems()]
    
    def getKeys(self):
        return [i[0] for i in self.getItems() if i[0]]
    
    def hasKey(self, k):
        return k in self.getKeys()
    
    def getValuesForKey(self, k):
        result = [i[1] for i in self.getItems() if i[0] == k]
        if len(result) > 1:
            raise NotImplementedError('Multiple values ({}) for key {} not yet supported'.format(result, k))
        return result
    
    def getItemsForKey(self, k):
        result = [i for i in self.getItems() if i[0] == k]
        if len(result) > 1:
            raise NotImplementedError('Multiple items ({}) for key {} not yet supported'.format(result, k))
        return result

    def dump(self, indent='', step='.'):
        
        def dumpString(s, indent, step):
#             print(indent + s + ' <str>' )
            print(indent + '<str>')
            print(indent + s)
        
        def dumpItems(items, indent, step):
            for _, v in items:
                if isinstance(v, str):
                    dumpString(v, indent+step, step)
                elif isinstance(v, list):
                    dumpItems(v, indent+step, step)
                else:
                    assert isinstance(v, ParseInfo)
                    v.dump(indent+step, step)       
       
        print(indent + ('> '+ self.name + ':\n' + indent if self.name else '') + '[' + self.__class__.__name__ + '] ' + self.render())
        dumpItems(self.items, indent, step)

    def render(self):
        sep = ' '
        def renderList(l):
            resultList = []
            for i in l:
                if isinstance(i, str):
                    resultList.append(i)
                    continue
                if isinstance(i, ParseInfo):
                    resultList.append(i.render())
                    continue
                if isinstance(i, list):
                    resultList.append(renderList(i))
            return sep.join(resultList)
        result = []
        for t in self.items:
            if isinstance(t[1], str):
                result.append(t[1]) 
            elif isinstance(t[1], list):
#                 result.append(t.renderItems(sep))
                result.append(renderList(t[1]))
            else:
                assert isinstance(t[1], ParseInfo), type(t[1])
                result.append(t[1].render())
        return sep.join(result)
    
    def yieldsValidExpression(self):
        try:
            self.__getPattern().parseString(self.render(), parseAll=True)
            return True
        except ParseException:
            return False
        
    def isValid(self):
        return self == self.__getPattern().parseString(self.render())[0]
    
    
def parseInfoFunc(classname):
            
    def keyedList(parseresults):
        while len(parseresults) == 1 and isinstance(parseresults[0], ParseResults):
            parseresults = parseresults[0]
        valuedict = dict((id(t), k) for (k, t) in parseresults.items())
        assert len(valuedict) == len(list(parseresults.items())), 'internal error: len(valuedict) = {}, len(parseresults.items) = {}'.format(len(valuedict), len(list(parseresults.items)))
        result = []
        for t in parseresults:
            if isinstance(t, str):
                result.append([None, t])
            elif isinstance(t, ParseInfo):
                t.__dict__['name'] = valuedict.get(id(t))
                result.append([valuedict.get(id(t)), t])
            else:
                assert isinstance(t, ParseResults), type(t)
                assert valuedict.get(id(t)) == None, 'Error: found name ({}) for compound expression {}, remove'.format(valuedict.get(id(t)), t.render())
                result.extend(keyedList(t))
        return result
    
    def makeparseinfo(parseresults):
        cls = globals()[classname]
        assert isinstance(parseresults, ParseResults)
        return cls(None, keyedList(parseresults))  
    
    return makeparseinfo


class SPARQLElement(ParseInfo):
    pass


class SPARQLNode(SPARQLElement):
    pass

            
class SPARQLTerminal(SPARQLNode):
    def render(self):
        return ''.join([t[1] for t in self.items])
    __str__ = render
            
            
class SPARQLNonTerminal(SPARQLNode):
    pass


class SPARQLKeyword(SPARQLElement):
    pass


class SPARQLOperator(SPARQLElement):
    pass



# Special tokens
ALL_VALUES_st_p = Literal('*')
class ALL_VALUES_st(SPARQLKeyword):
    pass
    def render(self):
        return '*'
if do_parseactions: ALL_VALUES_st_p.setParseAction(parseInfoFunc('ALL_VALUES_st'))

#
# Brackets and interpunction
#

LPAR_p, RPAR_p, LBRACK_p, RBRACK_p, SEMICOL_p, COMMA_p = map(Literal, '()[];,')

#
# Operators
#

NOT_op_p = Literal('!')
class NOT_op(SPARQLOperator):
    def render(self):
        return '!'
if do_parseactions: NOT_op_p.setParseAction(parseInfoFunc('NOT_op'))

PLUS_op_p = Literal('+')
class PLUS_op(SPARQLOperator):
    def render(self):
        return '+'
if do_parseactions: PLUS_op_p.setParseAction(parseInfoFunc('PLUS_op'))

MINUS_op_p = Literal('-')
class MINUS_op(SPARQLOperator):
    def render(self):
        return '-'
if do_parseactions: MINUS_op_p.setParseAction(parseInfoFunc('MINUS_op'))

TIMES_op_p = Literal('*')
class TIMES_op(SPARQLOperator):
    def render(self):
        return '*'
if do_parseactions: TIMES_op_p.setParseAction(parseInfoFunc('TIMES_op'))

DIV_op_p = Literal('/')
class DIV_op(SPARQLOperator):
    def render(self):
        return '/'
if do_parseactions: DIV_op_p.setParseAction(parseInfoFunc('DIV_op'))

EQ_op_p = Literal('=') 
class EQ_op(SPARQLOperator):
    def render(self):
        return '='
if do_parseactions: EQ_op_p.setParseAction(parseInfoFunc('EQ_op'))

NE_op_p = Literal('!=') 
class NE_op(SPARQLOperator):
    def render(self):
        return '!='
if do_parseactions: NE_op_p.setParseAction(parseInfoFunc('NE_op'))

GT_op_p = Literal('>') 
class GT_op(SPARQLOperator):
    def render(self):
        return '>'
if do_parseactions: GT_op_p.setParseAction(parseInfoFunc('GT_op'))

LT_op_p = Literal('<') 
class LT_op(SPARQLOperator):
    def render(self):
        return '<'
if do_parseactions: LT_op_p.setParseAction(parseInfoFunc('LT_op'))

GE_op_p = Literal('>=') 
class GE_op(SPARQLOperator):
    def render(self):
        return '>='
if do_parseactions: GE_op_p.setParseAction(parseInfoFunc('GE_op'))

LE_op_p = Literal('<=') 
class LE_op(SPARQLOperator):
    def render(self):
        return '<='
if do_parseactions: LE_op_p.setParseAction(parseInfoFunc('LE_op'))

AND_op_p = Literal('&&')
class AND_op(SPARQLOperator):
    def render(self):
        return '&&'
if do_parseactions: AND_op_p.setParseAction(parseInfoFunc('AND_op'))
  
OR_op_p = Literal('||')
class OR_op(SPARQLOperator):
    def render(self):
        return '||'
if do_parseactions: OR_op_p.setParseAction(parseInfoFunc('OR_op'))

INVERSE_op_p = Literal('^')
class INVERSE_op(SPARQLOperator):
    def render(self):
        return '^'
if do_parseactions: INVERSE_op_p.setParseAction(parseInfoFunc('INVERSE_op'))


#
# Keywords
#

TYPE_kw_p = Keyword('a')
class TYPE_kw(SPARQLKeyword):
    def render(self):
        return 'a'
if do_parseactions: TYPE_kw_p.setParseAction(parseInfoFunc('TYPE_kw'))

DISTINCT_kw_p = CaselessKeyword('DISTINCT')
class DISTINCT_kw(SPARQLKeyword):
    def render(self):
        return 'DISTINCT'
if do_parseactions: DISTINCT_kw_p.setParseAction(parseInfoFunc('DISTINCT_kw'))

COUNT_kw_p = CaselessKeyword('COUNT')
class COUNT_kw(SPARQLKeyword):
    def render(self):
        return 'COUNT'
if do_parseactions: COUNT_kw_p.setParseAction(parseInfoFunc('COUNT_kw'))

SUM_kw_p = CaselessKeyword('SUM')
class SUM_kw(SPARQLKeyword):
    def render(self):
        return 'SUM'
if do_parseactions: SUM_kw_p.setParseAction(parseInfoFunc('SUM_kw'))

MIN_kw_p = CaselessKeyword('MIN') 
class MIN_kw(SPARQLKeyword):
    def render(self):
        return 'MIN'
if do_parseactions: MIN_kw_p.setParseAction(parseInfoFunc('MIN_kw'))

MAX_kw_p = CaselessKeyword('MAX') 
class MAX_kw(SPARQLKeyword):
    def render(self):
        return 'MAX'
if do_parseactions: MAX_kw_p.setParseAction(parseInfoFunc('MAX_kw'))

AVG_kw_p = CaselessKeyword('AVG') 
class AVG_kw(SPARQLKeyword):
    def render(self):
        return 'AVG'
if do_parseactions: AVG_kw_p.setParseAction(parseInfoFunc('AVG_kw'))

SAMPLE_kw_p = CaselessKeyword('SAMPLE') 
class SAMPLE_kw(SPARQLKeyword):
    def render(self):
        return 'SAMPLE'
if do_parseactions: SAMPLE_kw_p.setParseAction(parseInfoFunc('SAMPLE_kw'))

GROUP_CONCAT_kw_p = CaselessKeyword('GROUP_CONCAT') 
class GROUP_CONCAT_kw(SPARQLKeyword):
    def render(self):
        return 'GROUP_CONCAT'
if do_parseactions: GROUP_CONCAT_kw_p.setParseAction(parseInfoFunc('GROUP_CONCAT_kw'))

SEPARATOR_kw_p = CaselessKeyword('SEPARATOR')
class SEPARATOR_kw(SPARQLKeyword):
    def render(self):
        return 'SEPARATOR'
if do_parseactions: SEPARATOR_kw_p.setParseAction(parseInfoFunc('SEPARATOR_kw'))

NOT_kw_p = CaselessKeyword('NOT') + NotAny(CaselessKeyword('EXISTS') | CaselessKeyword('IN'))
class NOT_kw(SPARQLKeyword):
    def render(self):
        return 'NOT'
if do_parseactions: NOT_kw_p.setParseAction(parseInfoFunc('NOT_kw'))

EXISTS_kw_p = CaselessKeyword('EXISTS')
class EXISTS_kw(SPARQLKeyword):
    def render(self):
        return 'EXISTS'
if do_parseactions: EXISTS_kw_p.setParseAction(parseInfoFunc('EXISTS_kw'))

NOT_EXISTS_kw_p = CaselessKeyword('NOT') + CaselessKeyword('EXISTS')
class NOT_EXISTS_kw(SPARQLKeyword):
    def render(self):
        return 'NOT EXISTS'
if do_parseactions: NOT_EXISTS_kw_p.setParseAction(parseInfoFunc('NOT_EXISTS_kw'))

REPLACE_kw_p = CaselessKeyword('REPLACE')
class REPLACE_kw(SPARQLKeyword):
    def render(self):
        return 'REPLACE'
if do_parseactions: REPLACE_kw_p.setParseAction(parseInfoFunc('REPLACE_kw'))

SUBSTR_kw_p = CaselessKeyword('SUBSTR')
class SUBSTR_kw(SPARQLKeyword):
    def render(self):
        return 'SUBSTR'
if do_parseactions: SUBSTR_kw_p.setParseAction(parseInfoFunc('SUBSTR_kw'))

REGEX_kw_p = CaselessKeyword('REGEX')
class REGEX_kw(SPARQLKeyword):
    def render(self):
        return 'REGEX'
if do_parseactions: REGEX_kw_p.setParseAction(parseInfoFunc('REGEX_kw'))

STR_kw_p = CaselessKeyword('STR') 
class STR_kw(SPARQLKeyword):
    def render(self):
        return 'STR'
if do_parseactions: STR_kw_p.setParseAction(parseInfoFunc('STR_kw'))

LANG_kw_p = CaselessKeyword('LANG') 
class LANG_kw(SPARQLKeyword):
    def render(self):
        return 'LANG'
if do_parseactions: LANG_kw_p.setParseAction(parseInfoFunc('LANG_kw'))

LANGMATCHES_kw_p = CaselessKeyword('LANGMATCHES') 
class LANGMATCHES_kw(SPARQLKeyword):
    def render(self):
        return 'LANGMATCHES'
if do_parseactions: LANGMATCHES_kw_p.setParseAction(parseInfoFunc('LANGMATCHES_kw'))

DATATYPE_kw_p = CaselessKeyword('DATATYPE') 
class DATATYPE_kw(SPARQLKeyword):
    def render(self):
        return 'DATATYPE'
if do_parseactions: DATATYPE_kw_p.setParseAction(parseInfoFunc('DATATYPE_kw'))

BOUND_kw_p = CaselessKeyword('BOUND') 
class BOUND_kw(SPARQLKeyword):
    def render(self):
        return 'BOUND'
if do_parseactions: BOUND_kw_p.setParseAction(parseInfoFunc('BOUND_kw'))

IRI_kw_p = CaselessKeyword('IRI') 
class IRI_kw(SPARQLKeyword):
    def render(self):
        return 'IRI'
if do_parseactions: IRI_kw_p.setParseAction(parseInfoFunc('IRI_kw'))

URI_kw_p = CaselessKeyword('URI') 
class URI_kw(SPARQLKeyword):
    def render(self):
        return 'URI'
if do_parseactions: URI_kw_p.setParseAction(parseInfoFunc('URI_kw'))

BNODE_kw_p = CaselessKeyword('BNODE') 
class BNODE_kw(SPARQLKeyword):
    def render(self):
        return 'BNODE'
if do_parseactions: BNODE_kw_p.setParseAction(parseInfoFunc('BNODE_kw'))

RAND_kw_p = CaselessKeyword('RAND') 
class RAND_kw(SPARQLKeyword):
    def render(self):
        return 'RAND'
if do_parseactions: RAND_kw_p.setParseAction(parseInfoFunc('RAND_kw'))

ABS_kw_p = CaselessKeyword('ABS') 
class ABS_kw(SPARQLKeyword):
    def render(self):
        return 'ABS'
if do_parseactions: ABS_kw_p.setParseAction(parseInfoFunc('ABS_kw'))

CEIL_kw_p = CaselessKeyword('CEIL') 
class CEIL_kw(SPARQLKeyword):
    def render(self):
        return 'CEIL'
if do_parseactions: CEIL_kw_p.setParseAction(parseInfoFunc('CEIL_kw'))

FLOOR_kw_p = CaselessKeyword('FLOOR') 
class FLOOR_kw(SPARQLKeyword):
    def render(self):
        return 'FLOOR'
if do_parseactions: FLOOR_kw_p.setParseAction(parseInfoFunc('FLOOR_kw'))

ROUND_kw_p = CaselessKeyword('ROUND') 
class ROUND_kw(SPARQLKeyword):
    def render(self):
        return 'ROUND'
if do_parseactions: ROUND_kw_p.setParseAction(parseInfoFunc('ROUND_kw'))

CONCAT_kw_p = CaselessKeyword('CONCAT') 
class CONCAT_kw(SPARQLKeyword):
    def render(self):
        return 'CONCAT'
if do_parseactions: CONCAT_kw_p.setParseAction(parseInfoFunc('CONCAT_kw'))

STRLEN_kw_p = CaselessKeyword('STRLEN') 
class STRLEN_kw(SPARQLKeyword):
    def render(self):
        return 'STRLEN'
if do_parseactions: STRLEN_kw_p.setParseAction(parseInfoFunc('STRLEN_kw'))

UCASE_kw_p = CaselessKeyword('UCASE') 
class UCASE_kw(SPARQLKeyword):
    def render(self):
        return 'UCASE'
if do_parseactions: UCASE_kw_p.setParseAction(parseInfoFunc('UCASE_kw'))

LCASE_kw_p = CaselessKeyword('LCASE') 
class LCASE_kw(SPARQLKeyword):
    def render(self):
        return 'LCASE'
if do_parseactions: LCASE_kw_p.setParseAction(parseInfoFunc('LCASE_kw'))

ENCODE_FOR_URI_kw_p = CaselessKeyword('ENCODE_FOR_URI') 
class ENCODE_FOR_URI_kw(SPARQLKeyword):
    def render(self):
        return 'ENCODE_FOR_URI'
if do_parseactions: ENCODE_FOR_URI_kw_p.setParseAction(parseInfoFunc('ENCODE_FOR_URI_kw'))

CONTAINS_kw_p = CaselessKeyword('CONTAINS') 
class CONTAINS_kw(SPARQLKeyword):
    def render(self):
        return 'CONTAINS'
if do_parseactions: CONTAINS_kw_p.setParseAction(parseInfoFunc('CONTAINS_kw'))

STRSTARTS_kw_p = CaselessKeyword('STRSTARTS') 
class STRSTARTS_kw(SPARQLKeyword):
    def render(self):
        return 'STRSTARTS'
if do_parseactions: STRSTARTS_kw_p.setParseAction(parseInfoFunc('STRSTARTS_kw'))

STRENDS_kw_p = CaselessKeyword('STRENDS') 
class STRENDS_kw(SPARQLKeyword):
    def render(self):
        return 'STRENDS'
if do_parseactions: STRENDS_kw_p.setParseAction(parseInfoFunc('STRENDS_kw'))

STRBEFORE_kw_p = CaselessKeyword('STRBEFORE') 
class STRBEFORE_kw(SPARQLKeyword):
    def render(self):
        return 'STRBEFORE'
if do_parseactions: STRBEFORE_kw_p.setParseAction(parseInfoFunc('STRBEFORE_kw'))

STRAFTER_kw_p = CaselessKeyword('STRAFTER') 
class STRAFTER_kw(SPARQLKeyword):
    def render(self):
        return 'STRAFTER'
if do_parseactions: STRAFTER_kw_p.setParseAction(parseInfoFunc('STRAFTER_kw'))

YEAR_kw_p = CaselessKeyword('YEAR') 
class YEAR_kw(SPARQLKeyword):
    def render(self):
        return 'YEAR'
if do_parseactions: YEAR_kw_p.setParseAction(parseInfoFunc('YEAR_kw'))

MONTH_kw_p = CaselessKeyword('MONTH') 
class MONTH_kw(SPARQLKeyword):
    def render(self):
        return 'MONTH'
if do_parseactions: MONTH_kw_p.setParseAction(parseInfoFunc('MONTH_kw'))

DAY_kw_p = CaselessKeyword('DAY') 
class DAY_kw(SPARQLKeyword):
    def render(self):
        return 'DAY'
if do_parseactions: DAY_kw_p.setParseAction(parseInfoFunc('DAY_kw'))

HOURS_kw_p = CaselessKeyword('HOURS') 
class HOURS_kw(SPARQLKeyword):
    def render(self):
        return 'HOURS'
if do_parseactions: HOURS_kw_p.setParseAction(parseInfoFunc('HOURS_kw'))

MINUTES_kw_p = CaselessKeyword('MINUTES') 
class MINUTES_kw(SPARQLKeyword):
    def render(self):
        return 'MINUTES'
if do_parseactions: MINUTES_kw_p.setParseAction(parseInfoFunc('MINUTES_kw'))

SECONDS_kw_p = CaselessKeyword('SECONDS') 
class SECONDS_kw(SPARQLKeyword):
    def render(self):
        return 'SECONDS'
if do_parseactions: SECONDS_kw_p.setParseAction(parseInfoFunc('SECONDS_kw'))

TIMEZONE_kw_p = CaselessKeyword('TIMEZONE') 
class TIMEZONE_kw(SPARQLKeyword):
    def render(self):
        return 'TIMEZONE'
if do_parseactions: TIMEZONE_kw_p.setParseAction(parseInfoFunc('TIMEZONE_kw'))

TZ_kw_p = CaselessKeyword('TZ') 
class TZ_kw(SPARQLKeyword):
    def render(self):
        return 'TZ'
if do_parseactions: TZ_kw_p.setParseAction(parseInfoFunc('TZ_kw'))

NOW_kw_p = CaselessKeyword('NOW') 
class NOW_kw(SPARQLKeyword):
    def render(self):
        return 'NOW'
if do_parseactions: NOW_kw_p.setParseAction(parseInfoFunc('NOW_kw'))

UUID_kw_p = CaselessKeyword('UUID') 
class UUID_kw(SPARQLKeyword):
    def render(self):
        return 'UUID'
if do_parseactions: UUID_kw_p.setParseAction(parseInfoFunc('UUID_kw'))

STRUUID_kw_p = CaselessKeyword('STRUUID') 
class STRUUID_kw(SPARQLKeyword):
    def render(self):
        return 'STRUUID'
if do_parseactions: STRUUID_kw_p.setParseAction(parseInfoFunc('STRUUID_kw'))

MD5_kw_p = CaselessKeyword('MD5') 
class MD5_kw(SPARQLKeyword):
    def render(self):
        return 'MD5'
if do_parseactions: MD5_kw_p.setParseAction(parseInfoFunc('MD5_kw'))

SHA1_kw_p = CaselessKeyword('SHA1') 
class SHA1_kw(SPARQLKeyword):
    def render(self):
        return 'SHA1'
if do_parseactions: SHA1_kw_p.setParseAction(parseInfoFunc('SHA1_kw'))

SHA256_kw_p = CaselessKeyword('SHA256') 
class SHA256_kw(SPARQLKeyword):
    def render(self):
        return 'SHA256'
if do_parseactions: SHA256_kw_p.setParseAction(parseInfoFunc('SHA256_kw'))

SHA384_kw_p = CaselessKeyword('SHA384') 
class SHA384_kw(SPARQLKeyword):
    def render(self):
        return 'SHA384'
if do_parseactions: SHA384_kw_p.setParseAction(parseInfoFunc('SHA384_kw'))

SHA512_kw_p = CaselessKeyword('SHA512') 
class SHA512_kw(SPARQLKeyword):
    def render(self):
        return 'SHA512'
if do_parseactions: SHA512_kw_p.setParseAction(parseInfoFunc('SHA512_kw'))

COALESCE_kw_p = CaselessKeyword('COALESCE') 
class COALESCE_kw(SPARQLKeyword):
    def render(self):
        return 'COALESCE'
if do_parseactions: COALESCE_kw_p.setParseAction(parseInfoFunc('COALESCE_kw'))

IF_kw_p = CaselessKeyword('IF') 
class IF_kw(SPARQLKeyword):
    def render(self):
        return 'IF'
if do_parseactions: IF_kw_p.setParseAction(parseInfoFunc('IF_kw'))

STRLANG_kw_p = CaselessKeyword('STRLANG') 
class STRLANG_kw(SPARQLKeyword):
    def render(self):
        return 'STRLANG'
if do_parseactions: STRLANG_kw_p.setParseAction(parseInfoFunc('STRLANG_kw'))

STRDT_kw_p = CaselessKeyword('STRDT') 
class STRDT_kw(SPARQLKeyword):
    def render(self):
        return 'STRDT'
if do_parseactions: STRDT_kw_p.setParseAction(parseInfoFunc('STRDT_kw'))

sameTerm_kw_p = CaselessKeyword('sameTerm') 
class sameTerm_kw(SPARQLKeyword):
    def render(self):
        return 'sameTerm'
if do_parseactions: sameTerm_kw_p.setParseAction(parseInfoFunc('sameTerm_kw'))

isIRI_kw_p = CaselessKeyword('isIRI') 
class isIRI_kw(SPARQLKeyword):
    def render(self):
        return 'isIRI'
if do_parseactions: isIRI_kw_p.setParseAction(parseInfoFunc('isIRI_kw'))

isURI_kw_p = CaselessKeyword('isURI') 
class isURI_kw(SPARQLKeyword):
    def render(self):
        return 'isURI'
if do_parseactions: isURI_kw_p.setParseAction(parseInfoFunc('isURI_kw'))

isBLANK_kw_p = CaselessKeyword('isBLANK') 
class isBLANK_kw(SPARQLKeyword):
    def render(self):
        return 'isBLANK'
if do_parseactions: isBLANK_kw_p.setParseAction(parseInfoFunc('isBLANK_kw'))

isLITERAL_kw_p = CaselessKeyword('isLITERAL') 
class isLITERAL_kw(SPARQLKeyword):
    def render(self):
        return 'isLITERAL'
if do_parseactions: isLITERAL_kw_p.setParseAction(parseInfoFunc('isLITERAL_kw'))

isNUMERIC_kw_p = CaselessKeyword('isNUMERIC') 
class isNUMERIC_kw(SPARQLKeyword):
    def render(self):
        return 'isNUMERIC'
if do_parseactions: isNUMERIC_kw_p.setParseAction(parseInfoFunc('isNUMERIC_kw'))

IN_kw_p = CaselessKeyword('IN') 
class IN_kw(SPARQLKeyword):
    def render(self):
        return 'IN'
if do_parseactions: IN_kw_p.setParseAction(parseInfoFunc('IN_kw'))

NOT_IN_kw_p = CaselessKeyword('NOT') + CaselessKeyword('IN')
class NOT_IN_kw(SPARQLKeyword):
    def render(self):
        return 'NOT IN'
if do_parseactions: NOT_IN_kw_p.setParseAction(parseInfoFunc('NOT_IN_kw'))

# 
# Parsers and classes for terminals
#

# [173]   PN_LOCAL_ESC      ::=   '\' ( '_' | '~' | '.' | '-' | '!' | '$' | '&' | "'" | '(' | ')' | '*' | '+' | ',' | ';' | '=' | '/' | '?' | '#' | '@' | '%' ) 
PN_LOCAL_ESC_e = r'\\[_~.\-!$&\'()*+,;=/?#@%]'
PN_LOCAL_ESC_p = Regex(PN_LOCAL_ESC_e)
class PN_LOCAL_ESC(SPARQLTerminal): 
    pass
if do_parseactions: PN_LOCAL_ESC_p.setParseAction(parseInfoFunc('PN_LOCAL_ESC'))


# [172]   HEX       ::=   [0-9] | [A-F] | [a-f] 
HEX_e = r'[0-9A-Fa-f]'
HEX_p = Regex(HEX_e)
class HEX(SPARQLTerminal):  
    pass
if do_parseactions: HEX_p.setParseAction(parseInfoFunc('HEX'))

# [171]   PERCENT   ::=   '%' HEX HEX
PERCENT_e = r'%({})({})'.format( HEX_e, HEX_e)
PERCENT_p = Regex(PERCENT_e)
class PERCENT(SPARQLTerminal):   
    pass
if do_parseactions: PERCENT_p.setParseAction(parseInfoFunc('PERCENT'))

# [170]   PLX       ::=   PERCENT | PN_LOCAL_ESC 
PLX_e = r'({})|({})'.format( PERCENT_e, PN_LOCAL_ESC_e)
PLX_p = Regex(PLX_e)
class PLX(SPARQLTerminal):  
    pass
if do_parseactions: PLX_p.setParseAction(parseInfoFunc('PLX'))

# [164]   PN_CHARS_BASE     ::=   [A-Z] | [a-z] | [#x00C0-#x00D6] | [#x00D8-#x00F6] | [#x00F8-#x02FF] | [#x0370-#x037D] | [#x037F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF] 
PN_CHARS_BASE_e = r'[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\U00010000-\U000EFFFF]'
PN_CHARS_BASE_p = Regex(PN_CHARS_BASE_e)
class PN_CHARS_BASE(SPARQLTerminal):  
    pass
if do_parseactions: PN_CHARS_BASE_p.setParseAction(parseInfoFunc('PN_CHARS_BASE'))

# [165]   PN_CHARS_U        ::=   PN_CHARS_BASE | '_' 
PN_CHARS_U_e = r'({})|({})'.format( PN_CHARS_BASE_e, r'_')
PN_CHARS_U_p = Regex(PN_CHARS_U_e)
class PN_CHARS_U(SPARQLTerminal):  
    pass
if do_parseactions: PN_CHARS_U_p.setParseAction(parseInfoFunc('PN_CHARS_U'))

# [167]   PN_CHARS          ::=   PN_CHARS_U | '-' | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] 
PN_CHARS_e = r'({})|({})|({})|({})|({})|({})'.format( PN_CHARS_U_e, r'\-', r'[0-9]',  r'\u00B7', r'[\u0300-\u036F]', r'[\u203F-\u2040]')
PN_CHARS_p = Regex(PN_CHARS_e) 
class PN_CHARS(SPARQLTerminal):  
    pass
if do_parseactions: PN_CHARS_p.setParseAction(parseInfoFunc('PN_CHARS'))

# [169]   PN_LOCAL          ::=   (PN_CHARS_U | ':' | [0-9] | PLX ) ((PN_CHARS | '.' | ':' | PLX)* (PN_CHARS | ':' | PLX) )?
PN_LOCAL_e = r'(({})|({})|({})|({}))((({})|({})|({})|({}))*(({})|({})|({})))?'.format( PN_CHARS_U_e, r':', r'[0-9]', PLX_e, PN_CHARS_e, r'\.', r':', PLX_e, PN_CHARS_e, r':', PLX_e) 
PN_LOCAL_p = Regex(PN_LOCAL_e)
class PN_LOCAL(SPARQLTerminal):  
    pass
if do_parseactions: PN_LOCAL_p.setParseAction(parseInfoFunc('PN_LOCAL'))
            
# [168]   PN_PREFIX         ::=   PN_CHARS_BASE ((PN_CHARS|'.')* PN_CHARS)?
PN_PREFIX_e = r'({})((({})|({}))*({}))?'.format( PN_CHARS_BASE_e, PN_CHARS_e, r'\.', PN_CHARS_e)
PN_PREFIX_p = Regex(PN_PREFIX_e)
class PN_PREFIX(SPARQLTerminal):  
    pass
if do_parseactions: PN_PREFIX_p.setParseAction(parseInfoFunc('PN_PREFIX'))

# [166]   VARNAME   ::=   ( PN_CHARS_U | [0-9] ) ( PN_CHARS_U | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] )* 
VARNAME_e = r'(({})|({}))(({})|({})|({})|({})|({}))*'.format( PN_CHARS_U_e, r'[0-9]', PN_CHARS_U_e, r'[0-9]', r'\u00B7', r'[\u0030-036F]', r'[\u0203-\u2040]')
VARNAME_p = Regex(VARNAME_e)
class VARNAME(SPARQLTerminal):  
    pass
if do_parseactions: VARNAME_p.setParseAction(parseInfoFunc('VARNAME'))

# [163]   ANON      ::=   '[' WS* ']' 
ANON_p = Literal('[') + ']'
class ANON(SPARQLTerminal):  
    pass
if do_parseactions: ANON_p.setParseAction(parseInfoFunc('ANON'))

# [162]   WS        ::=   #x20 | #x9 | #xD | #xA 
# WS is not used
# In the SPARQL EBNF this production is used for defining NIL and ANON, but in this pyparsing implementation those are implemented differently

# [161]   NIL       ::=   '(' WS* ')' 
NIL_p = Literal('(') + ')'
class NIL(SPARQLTerminal):  
    pass
if do_parseactions: NIL_p.setParseAction(parseInfoFunc('NIL'))

# [160]   ECHAR     ::=   '\' [tbnrf\"']
ECHAR_e = r'\\[tbnrf\\"\']'
ECHAR_p = Regex(ECHAR_e) 
class ECHAR(SPARQLTerminal):  
    pass
if do_parseactions: ECHAR_p.setParseAction(parseInfoFunc('ECHAR'))
 
# [159]   STRING_LITERAL_LONG2      ::=   '"""' ( ( '"' | '""' )? ( [^"\] | ECHAR ) )* '"""'  
STRING_LITERAL_LONG2_e = r'"""((""|")?(({})|({})))*"""'.format(r'[^"\\]', ECHAR_e)
STRING_LITERAL_LONG2_p = Regex(STRING_LITERAL_LONG2_e)
class STRING_LITERAL_LONG2(SPARQLTerminal):  
    pass
STRING_LITERAL_LONG2_p.parseWithTabs()
if do_parseactions: STRING_LITERAL_LONG2_p.setParseAction(parseInfoFunc('STRING_LITERAL_LONG2'))

# [158]   STRING_LITERAL_LONG1      ::=   "'''" ( ( "'" | "''" )? ( [^'\] | ECHAR ) )* "'''" 
STRING_LITERAL_LONG1_e = r"'''(('|'')?(({})|({})))*'''".format(r"[^'\\]", ECHAR_e)
STRING_LITERAL_LONG1_p = Regex(STRING_LITERAL_LONG1_e)  
class STRING_LITERAL_LONG1(SPARQLTerminal):  
    pass
STRING_LITERAL_LONG1_p.parseWithTabs()
if do_parseactions: STRING_LITERAL_LONG1_p.setParseAction(parseInfoFunc('STRING_LITERAL_LONG1'))

# [157]   STRING_LITERAL2   ::=   '"' ( ([^#x22#x5C#xA#xD]) | ECHAR )* '"' 
STRING_LITERAL2_e = r'"(({})|({}))*"'.format(ECHAR_e, r'[^\u0022\u005C\u000A\u000D]')
STRING_LITERAL2_p = Regex(STRING_LITERAL2_e)
class STRING_LITERAL2(SPARQLTerminal):  
    pass
STRING_LITERAL2_p.parseWithTabs()
if do_parseactions: STRING_LITERAL2_p.setParseAction(parseInfoFunc('STRING_LITERAL2'))
                           
# [156]   STRING_LITERAL1   ::=   "'" ( ([^#x27#x5C#xA#xD]) | ECHAR )* "'" 
STRING_LITERAL1_e = r"'(({})|({}))*'".format(ECHAR_e, r'[^\u0027\u005C\u000A\u000D]')
STRING_LITERAL1_p = Regex(STRING_LITERAL1_e)
class STRING_LITERAL1(SPARQLTerminal):  
    pass
STRING_LITERAL1_p.parseWithTabs()
if do_parseactions: STRING_LITERAL1_p.setParseAction(parseInfoFunc('STRING_LITERAL1'))
                            
# [155]   EXPONENT          ::=   [eE] [+-]? [0-9]+ 
EXPONENT_e = r'[eE][+-][0-9]+'
EXPONENT_p = Regex(EXPONENT_e)
class EXPONENT(SPARQLTerminal):  
    pass
if do_parseactions: EXPONENT_p.setParseAction(parseInfoFunc('EXPONENT'))

# [148]   DOUBLE    ::=   [0-9]+ '.' [0-9]* EXPONENT | '.' ([0-9])+ EXPONENT | ([0-9])+ EXPONENT 
DOUBLE_e = r'([0-9]+\.[0-9]*({}))|(\.[0-9]+({}))|([0-9]+({}))'.format(EXPONENT_e, EXPONENT_e, EXPONENT_e)
DOUBLE_p = Regex(DOUBLE_e)
class DOUBLE(SPARQLTerminal):  
    pass
if do_parseactions: DOUBLE_p.setParseAction(parseInfoFunc('DOUBLE'))

# [154]   DOUBLE_NEGATIVE   ::=   '-' DOUBLE 
DOUBLE_NEGATIVE_e = r'\-({})'.format(DOUBLE_e)
DOUBLE_NEGATIVE_p = Regex(DOUBLE_NEGATIVE_e)
class DOUBLE_NEGATIVE(SPARQLTerminal):  
    pass
if do_parseactions: DOUBLE_NEGATIVE_p.setParseAction(parseInfoFunc('DOUBLE_NEGATIVE'))

# [151]   DOUBLE_POSITIVE   ::=   '+' DOUBLE 
DOUBLE_POSITIVE_e = r'\+({})'.format(DOUBLE_e)
DOUBLE_POSITIVE_p = Regex(DOUBLE_POSITIVE_e)
class DOUBLE_POSITIVE(SPARQLTerminal):  
    pass
if do_parseactions: DOUBLE_POSITIVE_p.setParseAction(parseInfoFunc('DOUBLE_POSITIVE'))

# [147]   DECIMAL   ::=   [0-9]* '.' [0-9]+ 
DECIMAL_e = r'[0-9]*\.[0-9]+'
DECIMAL_p = Regex(DECIMAL_e)
class DECIMAL(SPARQLTerminal):  
    pass
if do_parseactions: DECIMAL_p.setParseAction(parseInfoFunc('DECIMAL'))

# [153]   DECIMAL_NEGATIVE          ::=   '-' DECIMAL 
DECIMAL_NEGATIVE_e = r'\-({})'.format(DECIMAL_e)
DECIMAL_NEGATIVE_p = Regex(DECIMAL_NEGATIVE_e)
class DECIMAL_NEGATIVE(SPARQLTerminal):  
    pass
if do_parseactions: DECIMAL_NEGATIVE_p.setParseAction(parseInfoFunc('DECIMAL_NEGATIVE'))

# [150]   DECIMAL_POSITIVE          ::=   '+' DECIMAL 
DECIMAL_POSITIVE_e = r'\+({})'.format(DECIMAL_e)
DECIMAL_POSITIVE_p = Regex(DECIMAL_POSITIVE_e)
class DECIMAL_POSITIVE(SPARQLTerminal):  
    pass
if do_parseactions: DECIMAL_POSITIVE_p.setParseAction(parseInfoFunc('DECIMAL_POSITIVE'))

# [146]   INTEGER   ::=   [0-9]+ 
INTEGER_e = r'[0-9]+'
INTEGER_p = Regex(INTEGER_e)
class INTEGER(SPARQLTerminal):  
    pass
if do_parseactions: INTEGER_p.setParseAction(parseInfoFunc('INTEGER'))

# [152]   INTEGER_NEGATIVE          ::=   '-' INTEGER
INTEGER_NEGATIVE_e = r'\-({})'.format(INTEGER_e)
INTEGER_NEGATIVE_p = Regex(INTEGER_NEGATIVE_e)
class INTEGER_NEGATIVE(SPARQLTerminal):  
    pass
if do_parseactions: INTEGER_NEGATIVE_p.setParseAction(parseInfoFunc('INTEGER_NEGATIVE'))

# [149]   INTEGER_POSITIVE          ::=   '+' INTEGER 
INTEGER_POSITIVE_e = r'\+({})'.format(INTEGER_e)
INTEGER_POSITIVE_p = Regex(INTEGER_POSITIVE_e)
class INTEGER_POSITIVE(SPARQLTerminal):  
    pass
if do_parseactions: INTEGER_POSITIVE_p.setParseAction(parseInfoFunc('INTEGER_POSITIVE'))

# [145]   LANGTAG   ::=   '@' [a-zA-Z]+ ('-' [a-zA-Z0-9]+)* 
LANGTAG_e = r'@[a-zA-Z]+(\-[a-zA-Z0-9]+)*'
LANGTAG_p = Regex(LANGTAG_e)
class LANGTAG(SPARQLTerminal):  
    pass
if do_parseactions: LANGTAG_p.setParseAction(parseInfoFunc('LANGTAG'))

# [144]   VAR2      ::=   '$' VARNAME 
VAR2_e = r'\$({})'.format(VARNAME_e)
VAR2_p = Regex(VAR2_e)
class VAR2(SPARQLTerminal):  
    pass
if do_parseactions: VAR2_p.setParseAction(parseInfoFunc('VAR2'))

# [143]   VAR1      ::=   '?' VARNAME 
VAR1_e = r'\?({})'.format(VARNAME_e)
VAR1_p = Regex(VAR1_e)
class VAR1(SPARQLTerminal):  
    pass
if do_parseactions: VAR1_p.setParseAction(parseInfoFunc('VAR1'))

# [142]   BLANK_NODE_LABEL          ::=   '_:' ( PN_CHARS_U | [0-9] ) ((PN_CHARS|'.')* PN_CHARS)?
BLANK_NODE_LABEL_e = r'_:(({})|[0-9])((({})|\.)*({}))?'.format(PN_CHARS_U_e, PN_CHARS_e, PN_CHARS_e)
BLANK_NODE_LABEL_p = Regex(BLANK_NODE_LABEL_e)
class BLANK_NODE_LABEL(SPARQLTerminal):  
    pass
if do_parseactions: BLANK_NODE_LABEL_p.setParseAction(parseInfoFunc('BLANK_NODE_LABEL'))

# [140]   PNAME_NS          ::=   PN_PREFIX? ':'
PNAME_NS_e = r'({})?:'.format(PN_PREFIX_e)
PNAME_NS_p = Regex(PNAME_NS_e)
class PNAME_NS(SPARQLTerminal):  
    pass
if do_parseactions: PNAME_NS_p.setParseAction(parseInfoFunc('PNAME_NS'))

# [141]   PNAME_LN          ::=   PNAME_NS PN_LOCAL 
PNAME_LN_e = r'({})({})'.format(PNAME_NS_e, PN_LOCAL_e)
PNAME_LN_p = Regex(PNAME_LN_e)
class PNAME_LN(SPARQLTerminal):  
    pass
if do_parseactions: PNAME_LN_p.setParseAction(parseInfoFunc('PNAME_LN'))

# [139]   IRIREF    ::=   '<' ([^<>"{}|^`\]-[#x00-#x20])* '>' 
IRIREF_e = r'<[^<>"{}|^`\\\\\u0000-\u0020]*>'
IRIREF_p = Regex(IRIREF_e)
class IRIREF(SPARQLTerminal):  
    pass
if do_parseactions: IRIREF_p.setParseAction(parseInfoFunc('IRIREF'))

#
# Parsers and classes for non-terminals
#

# [138]   BlankNode         ::=   BLANK_NODE_LABEL | ANON 
BlankNode_p = BLANK_NODE_LABEL_p | ANON_p
class BlankNode(SPARQLNonTerminal):  
    pass
if do_parseactions: BlankNode_p.setParseAction(parseInfoFunc('BlankNode'))

# [137]   PrefixedName      ::=   PNAME_LN | PNAME_NS 
PrefixedName_p = PNAME_LN_p ^ PNAME_NS_p
class PrefixedName(SPARQLNonTerminal):  
    pass
if do_parseactions: PrefixedName_p.setParseAction(parseInfoFunc('PrefixedName'))

# [136]   iri       ::=   IRIREF | PrefixedName 
iri_p = IRIREF_p ^ PrefixedName_p
class iri(SPARQLNonTerminal):  
    pass
if do_parseactions: iri_p.setParseAction(parseInfoFunc('iri'))

# [135]   String    ::=   STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 
String_p = STRING_LITERAL1_p ^ STRING_LITERAL2_p ^ STRING_LITERAL_LONG1_p ^ STRING_LITERAL_LONG2_p
class String(SPARQLNonTerminal):  
    pass
String_p.parseWithTabs()
if do_parseactions: String_p.setParseAction(parseInfoFunc('String'))
 
# [134]   BooleanLiteral    ::=   'true' | 'false' 
BooleanLiteral_p = Literal('true') | Literal('false')
class BooleanLiteral(SPARQLNonTerminal):  
    pass
if do_parseactions: BooleanLiteral_p.setParseAction(parseInfoFunc('BooleanLiteral'))
 
# # [133]   NumericLiteralNegative    ::=   INTEGER_NEGATIVE | DECIMAL_NEGATIVE | DOUBLE_NEGATIVE 
NumericLiteralNegative_p = INTEGER_NEGATIVE_p ^ DECIMAL_NEGATIVE_p ^ DOUBLE_NEGATIVE_p
class NumericLiteralNegative(SPARQLNonTerminal):  
    pass
if do_parseactions: NumericLiteralNegative_p.setParseAction(parseInfoFunc('NumericLiteralNegative'))
 
# # [132]   NumericLiteralPositive    ::=   INTEGER_POSITIVE | DECIMAL_POSITIVE | DOUBLE_POSITIVE 
NumericLiteralPositive_p = INTEGER_POSITIVE_p ^ DECIMAL_POSITIVE_p ^ DOUBLE_POSITIVE_p
class NumericLiteralPositive(SPARQLNonTerminal):  
    pass
if do_parseactions: NumericLiteralPositive_p.setParseAction(parseInfoFunc('NumericLiteralPositive'))
 
# # [131]   NumericLiteralUnsigned    ::=   INTEGER | DECIMAL | DOUBLE 
NumericLiteralUnsigned_p = INTEGER_p ^ DECIMAL_p ^ DOUBLE_p
class NumericLiteralUnsigned(SPARQLNonTerminal):  
    pass
if do_parseactions: NumericLiteralUnsigned_p.setParseAction(parseInfoFunc('NumericLiteralUnsigned'))
# 
# # [130]   NumericLiteral    ::=   NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative 
NumericLiteral_p = NumericLiteralUnsigned_p | NumericLiteralPositive_p | NumericLiteralNegative_p
class NumericLiteral(SPARQLNonTerminal):  
    pass
if do_parseactions: NumericLiteral_p.setParseAction(parseInfoFunc('NumericLiteral'))

# [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
RDFLiteral_p = String_p('lexical_form') + Optional(Group ((LANGTAG_p('langtag') ^ ('^^' + iri_p('datatype_uri')))))
class RDFLiteral(SPARQLNonTerminal):  
    pass
if do_parseactions: RDFLiteral_p.setParseAction(parseInfoFunc('RDFLiteral'))

Expression_p = Forward()
class Expression(SPARQLNonTerminal):  
    pass
if do_parseactions: Expression_p.setParseAction(parseInfoFunc('Expression'))

# pattern and class to parse and render delimited Expression lists
ExpressionList_p = delimitedList(Expression_p)
class ExpressionList(SPARQLNonTerminal):
    def render(self):
        return ', '.join([v[1] if isinstance(v[1], str) else v[1].render() for v in self.getItems()])
if do_parseactions: ExpressionList_p.setParseAction(parseInfoFunc('ExpressionList'))
    
 
# [71]    ArgList   ::=   NIL | '(' 'DISTINCT'? Expression ( ',' Expression )* ')' 
ArgList_p = Group(NIL_p('nil')) | (LPAR_p + Optional(DISTINCT_kw_p('distinct')) + ExpressionList_p('expression_list') + RPAR_p)
class ArgList(SPARQLNonTerminal):  
    pass
if do_parseactions: ArgList_p.setParseAction(parseInfoFunc('ArgList'))


# [128]   iriOrFunction     ::=   iri ArgList? 
iriOrFunction_p = iri_p('iri') + Optional(Group(ArgList_p))('ArgList')
class iriOrFunction(SPARQLNonTerminal):  
    pass
if do_parseactions: iriOrFunction_p.setParseAction(parseInfoFunc('iriOrFunction'))

# [127]   Aggregate         ::=     'COUNT' '(' 'DISTINCT'? ( '*' | Expression ) ')' 
#             | 'SUM' '(' 'DISTINCT'? Expression ')' 
#             | 'MIN' '(' 'DISTINCT'? Expression ')' 
#             | 'MAX' '(' 'DISTINCT'? Expression ')' 
#             | 'AVG' '(' 'DISTINCT'? Expression ')' 
#             | 'SAMPLE' '(' 'DISTINCT'? Expression ')' 
#             | 'GROUP_CONCAT' '(' 'DISTINCT'? Expression ( ';' 'SEPARATOR' '=' String )? ')' 
Aggregate_p = ( COUNT_kw_p('count') + LPAR_p + Optional(DISTINCT_kw_p('distinct')) + ( ALL_VALUES_st_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( SUM_kw_p('sum') + LPAR_p + Optional(DISTINCT_kw_p('distinct')) + ( ALL_VALUES_st_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( MIN_kw_p('min') + LPAR_p + Optional(DISTINCT_kw_p('distinct')) + ( ALL_VALUES_st_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( MAX_kw_p('max') + LPAR_p + Optional(DISTINCT_kw_p('distinct')) + ( ALL_VALUES_st_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( AVG_kw_p('avg') + LPAR_p + Optional(DISTINCT_kw_p('distinct')) + ( ALL_VALUES_st_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( SAMPLE_kw_p('sample') + LPAR_p + Optional(DISTINCT_kw_p('distinct')) + ( ALL_VALUES_st_p('all') ^ Expression_p('expression') ) + RPAR_p ) | \
            ( GROUP_CONCAT_kw_p('group_concat') + LPAR_p + Optional(DISTINCT_kw_p('distinct')) + Expression_p('expression') + Optional( SEMICOL_p + SEPARATOR_kw_p + '=' + String_p('separator') ) + RPAR_p )
class Aggregate(SPARQLNonTerminal):  
    pass
if do_parseactions: Aggregate_p.setParseAction(parseInfoFunc('Aggregate'))

GroupGraphPattern_p = Forward()
class GroupGraphPattern(SPARQLNonTerminal):  
    pass
if do_parseactions: GroupGraphPattern_p.setParseAction(parseInfoFunc('GroupGraphPattern'))
 
# [126]   NotExistsFunc     ::=   'NOT' 'EXISTS' GroupGraphPattern 
NotExistsFunc_p = Group(NOT_EXISTS_kw_p + GroupGraphPattern_p('groupgraph'))
class NotExistsFunc(SPARQLNonTerminal):  
    pass
if do_parseactions: NotExistsFunc_p.setParseAction(parseInfoFunc('NotExistsFunc'))
 
# [125]   ExistsFunc        ::=   'EXISTS' GroupGraphPattern 
ExistsFunc_p = Group(EXISTS_kw_p + GroupGraphPattern_p('groupgraph'))
class ExistsFunc(SPARQLNonTerminal):  
    pass
if do_parseactions: ExistsFunc_p.setParseAction(parseInfoFunc('ExistsFunc'))
 
# [124]   StrReplaceExpression      ::=   'REPLACE' '(' Expression ',' Expression ',' Expression ( ',' Expression )? ')' 
StrReplaceExpression_p = Group(REPLACE_kw_p + LPAR_p + Expression_p('arg') + COMMA_p + Expression_p('pattern') + COMMA_p + Expression_p('replacement') + Optional(COMMA_p + Expression_p('flags')) + RPAR_p)
class StrReplaceExpression(SPARQLNonTerminal):  
    pass
if do_parseactions: StrReplaceExpression_p.setParseAction(parseInfoFunc('StrReplaceExpression'))
 
# [123]   SubstringExpression       ::=   'SUBSTR' '(' Expression ',' Expression ( ',' Expression )? ')' 
SubstringExpression_p = Group(SUBSTR_kw_p + LPAR_p + Expression_p('source') + COMMA_p + Expression_p('startloc') + Optional(COMMA_p + Expression_p('length')) + RPAR_p)
class SubstringExpression(SPARQLNonTerminal):  
    pass
if do_parseactions: SubstringExpression_p.setParseAction(parseInfoFunc('SubstringExpression'))
 
# [122]   RegexExpression   ::=   'REGEX' '(' Expression ',' Expression ( ',' Expression )? ')' 
RegexExpression_p = Group(REGEX_kw_p + LPAR_p + Expression_p('text') + COMMA_p + Expression_p('pattern') + Optional(COMMA_p + Expression_p('flags')) + RPAR_p)
class RegexExpression(SPARQLNonTerminal):  
    pass
if do_parseactions: RegexExpression_p.setParseAction(parseInfoFunc('RegexExpression'))

# [108]   Var       ::=   VAR1 | VAR2 
Var_p = VAR1_p | VAR2_p
class Var(SPARQLNonTerminal):  
    pass
if do_parseactions: Var_p.setParseAction(parseInfoFunc('Var'))

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
BuiltInCall_p = Aggregate_p | \
                STR_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                LANG_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                LANGMATCHES_kw_p + LPAR_p + Expression_p('language-tag') + COMMA_p + Expression_p('language-range') + RPAR_p    | \
                DATATYPE_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                BOUND_kw_p + LPAR_p + Var_p('var') + RPAR_p    | \
                IRI_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                URI_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                BNODE_kw_p + (LPAR_p + Expression_p('expression') + RPAR_p | NIL_p)    | \
                RAND_kw_p + NIL_p    | \
                ABS_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                CEIL_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                FLOOR_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                ROUND_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                CONCAT_kw_p + ExpressionList_p('expressionList')    | \
                SubstringExpression_p   | \
                STRLEN_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                StrReplaceExpression_p  | \
                UCASE_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                LCASE_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                ENCODE_FOR_URI_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                CONTAINS_kw_p + LPAR_p + Expression_p('arg1') + COMMA_p + Expression_p('arg2') + RPAR_p    | \
                STRSTARTS_kw_p + LPAR_p + Expression_p('arg1') + COMMA_p + Expression_p('arg2') + RPAR_p    | \
                STRENDS_kw_p + LPAR_p + Expression_p('arg1') + COMMA_p + Expression_p('arg2') + RPAR_p    | \
                STRBEFORE_kw_p + LPAR_p + Expression_p('arg1') + COMMA_p + Expression_p('arg2') + RPAR_p    | \
                STRAFTER_kw_p + LPAR_p + Expression_p('arg1') + COMMA_p + Expression_p('arg2') + RPAR_p    | \
                YEAR_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                MONTH_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                DAY_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                HOURS_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                MINUTES_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                SECONDS_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                TIMEZONE_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                TZ_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                NOW_kw_p + NIL_p    | \
                UUID_kw_p + NIL_p    | \
                STRUUID_kw_p + NIL_p    | \
                MD5_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                SHA1_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                SHA256_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                SHA384_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                SHA512_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                COALESCE_kw_p + ExpressionList_p('expressionList')    | \
                IF_kw_p + LPAR_p + Expression_p('expression1') + COMMA_p + Expression_p('expression2') + COMMA_p + Expression_p('expression3') + RPAR_p    | \
                STRLANG_kw_p + LPAR_p + Expression_p('lexicalForm') + COMMA_p + Expression_p('langTag') + RPAR_p    | \
                STRDT_kw_p + LPAR_p + Expression_p('lexicalForm') + COMMA_p + Expression_p('datatypeIRI') + RPAR_p    | \
                sameTerm_kw_p + LPAR_p + Expression_p('term1') + COMMA_p + Expression_p('term2') + RPAR_p    | \
                isIRI_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                isURI_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                isBLANK_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                isLITERAL_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                isNUMERIC_kw_p + LPAR_p + Expression_p('expression') + RPAR_p    | \
                RegexExpression_p | \
                ExistsFunc_p | \
                NotExistsFunc_p
class BuiltInCall(SPARQLNonTerminal):  
    pass
if do_parseactions: BuiltInCall_p.setParseAction(parseInfoFunc('BuiltInCall'))

# [120]   BrackettedExpression      ::=   '(' Expression ')' 
BracketedExpression_p = Group(LPAR_p + Expression_p('expression') + RPAR_p)
class BracketedExpression(SPARQLNonTerminal):  
    pass
if do_parseactions: BracketedExpression_p.setParseAction(parseInfoFunc('BracketedExpression'))

# [119]   PrimaryExpression         ::=   BrackettedExpression | BuiltInCall | iriOrFunction | RDFLiteral | NumericLiteral | BooleanLiteral | Var 
PrimaryExpression_p = BracketedExpression_p | BuiltInCall_p | iriOrFunction_p | RDFLiteral_p | NumericLiteral_p | BooleanLiteral_p | Var_p
class PrimaryExpression(SPARQLNonTerminal):  
    pass
if do_parseactions: PrimaryExpression_p.setParseAction(parseInfoFunc('PrimaryExpression'))

# [118]   UnaryExpression   ::=     '!' PrimaryExpression 
#             | '+' PrimaryExpression 
#             | '-' PrimaryExpression 
#             | PrimaryExpression 
UnaryExpression_p = NOT_op_p + PrimaryExpression_p | PLUS_op_p + PrimaryExpression_p | MINUS_op_p + PrimaryExpression_p | PrimaryExpression_p
class UnaryExpression(SPARQLNonTerminal):  
    pass
if do_parseactions: UnaryExpression_p.setParseAction(parseInfoFunc('UnaryExpression'))

# [117]   MultiplicativeExpression          ::=   UnaryExpression ( '*' UnaryExpression | '/' UnaryExpression )* 
MultiplicativeExpression_p = UnaryExpression_p + ZeroOrMore( TIMES_op_p + UnaryExpression_p | DIV_op_p + UnaryExpression_p )
class MultiplicativeExpression(SPARQLNonTerminal):  
    pass
if do_parseactions: MultiplicativeExpression_p.setParseAction(parseInfoFunc('MultiplicativeExpression'))

# [116]   AdditiveExpression        ::=   MultiplicativeExpression ( '+' MultiplicativeExpression | '-' MultiplicativeExpression | ( NumericLiteralPositive | NumericLiteralNegative ) ( ( '*' UnaryExpression ) | ( '/' UnaryExpression ) )* )* 
AdditiveExpression_p = MultiplicativeExpression_p + ZeroOrMore (PLUS_op_p + MultiplicativeExpression_p | MINUS_op_p  + MultiplicativeExpression_p | (NumericLiteralPositive_p | NumericLiteralNegative_p) + ZeroOrMore (TIMES_op_p + UnaryExpression_p | DIV_op_p + UnaryExpression_p))
class AdditiveExpression(SPARQLNonTerminal):  
    pass
if do_parseactions: AdditiveExpression_p.setParseAction(parseInfoFunc('AdditiveExpression'))

# [115]   NumericExpression         ::=   AdditiveExpression 
NumericExpression_p = AdditiveExpression_p + Empty()
class NumericExpression(SPARQLNonTerminal):  
    pass
if do_parseactions: NumericExpression_p.setParseAction(parseInfoFunc('NumericExpression'))

# [114]   RelationalExpression      ::=   NumericExpression ( '=' NumericExpression | '!=' NumericExpression | '<' NumericExpression | '>' NumericExpression | '<=' NumericExpression | '>=' NumericExpression | 'IN' ExpressionList | 'NOT' 'IN' ExpressionList )? 
RelationalExpression_p = NumericExpression_p + Optional( EQ_op_p + NumericExpression_p | \
                                                         NE_op_p + NumericExpression_p | \
                                                         LT_op_p + NumericExpression_p | \
                                                         GT_op_p + NumericExpression_p | \
                                                         LE_op_p + NumericExpression_p | \
                                                         GE_op_p + NumericExpression_p | \
                                                         IN_kw_p + ExpressionList_p | \
                                                         NOT_IN_kw_p + ExpressionList_p)
class RelationalExpression(SPARQLNonTerminal):  
    pass
if do_parseactions: RelationalExpression_p.setParseAction(parseInfoFunc('RelationalExpression'))

# [113]   ValueLogical      ::=   RelationalExpression 
ValueLogical_p = RelationalExpression_p + Empty()
class ValueLogical(SPARQLNonTerminal):  
    pass
if do_parseactions: ValueLogical_p.setParseAction(parseInfoFunc('ValueLogical'))

# [112]   ConditionalAndExpression          ::=   ValueLogical ( '&&' ValueLogical )* 
ConditionalAndExpression_p = ValueLogical_p + ZeroOrMore(AND_op_p + ValueLogical_p)
class ConditionalAndExpression(SPARQLNonTerminal):  
    pass
if do_parseactions: ConditionalAndExpression_p.setParseAction(parseInfoFunc('ConditionalAndExpression'))

# [111]   ConditionalOrExpression   ::=   ConditionalAndExpression ( '||' ConditionalAndExpression )* 
ConditionalOrExpression_p = ConditionalAndExpression_p + ZeroOrMore(OR_op_p + ConditionalAndExpression_p)
class ConditionalOrExpression(SPARQLNonTerminal):  
    pass
if do_parseactions: ConditionalOrExpression_p.setParseAction(parseInfoFunc('ConditionalOrExpression'))

# [110]   Expression        ::=   ConditionalOrExpression 
Expression_p << (ConditionalOrExpression_p + Empty())

# [109]   GraphTerm         ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | BlankNode | NIL 
GraphTerm_p =   iri_p | \
                RDFLiteral_p | \
                NumericLiteral_p | \
                BooleanLiteral_p | \
                BlankNode_p | \
                NIL_p
class GraphTerm(SPARQLNonTerminal):  
    pass
if do_parseactions: GraphTerm_p.setParseAction(parseInfoFunc('GraphTerm'))
                
# [107]   VarOrIri          ::=   Var | iri 
VarOrIri_p = Var_p | iri_p
class VarOrIri(SPARQLNonTerminal):  
    pass
if do_parseactions: VarOrIri_p.setParseAction(parseInfoFunc('VarOrIri'))

# [106]   VarOrTerm         ::=   Var | GraphTerm 
VarOrTerm_p = Var_p | GraphTerm_p
class VarOrTerm(SPARQLNonTerminal):  
    pass
if do_parseactions: VarOrTerm_p.setParseAction(parseInfoFunc('VarOrTerm'))

TriplesNodePath_p = Forward()
class TriplesNodePath(SPARQLNonTerminal):  
    pass
if do_parseactions: TriplesNodePath_p.setParseAction(parseInfoFunc('TriplesNodePath'))

# [105]   GraphNodePath     ::=   VarOrTerm | TriplesNodePath 
GraphNodePath_p = VarOrTerm_p | TriplesNodePath_p 

TriplesNode_p = Forward()
class TriplesNode(SPARQLNonTerminal):  
    pass
if do_parseactions: TriplesNode_p.setParseAction(parseInfoFunc('TriplesNode'))

# [104]   GraphNode         ::=   VarOrTerm | TriplesNode 
GraphNode_p = VarOrTerm_p ^ TriplesNode_p
class GraphNode(SPARQLNonTerminal):  
    pass
if do_parseactions: GraphNode_p.setParseAction(parseInfoFunc('GraphNode'))

# [103]   CollectionPath    ::=   '(' GraphNodePath+ ')' 
CollectionPath_p =  LPAR_p + OneOrMore(GraphNodePath_p) + RPAR_p
class CollectionPath(SPARQLNonTerminal):  
    pass
if do_parseactions: CollectionPath_p.setParseAction(parseInfoFunc('CollectionPath'))

# [102]   Collection        ::=   '(' GraphNode+ ')' 
Collection_p =  LPAR_p + OneOrMore(GraphNode_p) + RPAR_p
class Collection(SPARQLNonTerminal):  
    pass
if do_parseactions: Collection_p.setParseAction(parseInfoFunc('Collection'))

PropertyListPathNotEmpty_p = Forward()
class PropertyListPathNotEmpty(SPARQLNonTerminal):  
    pass
if do_parseactions: PropertyListPathNotEmpty_p.setParseAction(parseInfoFunc('PropertyListPathNotEmpty'))

# [101]   BlankNodePropertyListPath         ::=   '[' PropertyListPathNotEmpty ']'
BlankNodePropertyListPath_p =   LBRACK_p + PropertyListPathNotEmpty_p + RBRACK_p 
class BlankNodePropertyListPath(SPARQLNonTerminal):  
    pass
if do_parseactions: BlankNodePropertyListPath_p.setParseAction(parseInfoFunc('BlankNodePropertyListPath'))

# [100]   TriplesNodePath   ::=   CollectionPath | BlankNodePropertyListPath 
TriplesNodePath_p << (CollectionPath_p | BlankNodePropertyListPath_p) 

PropertyListNotEmpty_p = Forward()
class PropertyListNotEmpty(SPARQLNonTerminal):  
    pass
if do_parseactions: PropertyListNotEmpty_p.setParseAction(parseInfoFunc('PropertyListNotEmpty'))

# [99]    BlankNodePropertyList     ::=   '[' PropertyListNotEmpty ']' 
BlankNodePropertyList_p =   LBRACK_p + PropertyListNotEmpty_p + RBRACK_p 
class BlankNodePropertyList(SPARQLNonTerminal):  
    pass
if do_parseactions: BlankNodePropertyList_p.setParseAction(parseInfoFunc('BlankNodePropertyList'))

# [98]    TriplesNode       ::=   Collection | BlankNodePropertyList 
TriplesNode_p << (Collection_p | BlankNodePropertyList_p)

# [97]    Integer   ::=   INTEGER 
Integer_p = INTEGER_p + Empty()
class Integer(SPARQLNonTerminal):  
    pass
if do_parseactions: Integer_p.setParseAction(parseInfoFunc('Integer'))

# [96]    PathOneInPropertySet      ::=   iri | 'a' | '^' ( iri | 'a' ) 
PathOneInPropertySet_p =   iri_p | TYPE_kw_p | (INVERSE_op_p  + ( iri_p | TYPE_kw_p ))
class PathOneInPropertySet(SPARQLNonTerminal):  
    pass
if do_parseactions: PathOneInPropertySet_p.setParseAction(parseInfoFunc('PathOneInPropertySet'))

# pattern and class to parse and render delimited PathOneInPropertySet lists
PathOneInPropertySetList_p = delimitedList(PathOneInPropertySet_p, delim='|')
class PathOneInPropertySetList(SPARQLNonTerminal):
    def render(self):
        return ' | '.join([v[1] if isinstance(v[1], str) else v[1].render() for v in self.getItems()])
if do_parseactions: PathOneInPropertySetList_p.setParseAction(parseInfoFunc('PathOneInPropertySetList'))

# [95]    PathNegatedPropertySet    ::=   PathOneInPropertySet | '(' ( PathOneInPropertySet ( '|' PathOneInPropertySet )* )? ')' 
PathNegatedPropertySet_p = PathOneInPropertySet_p | (LPAR_p + Optional(PathOneInPropertySetList_p) + RPAR_p)
class PathNegatedPropertySet(SPARQLNonTerminal):  
    pass
if do_parseactions: PathNegatedPropertySet_p.setParseAction(parseInfoFunc('PathNegatedPropertySet'))

Path_p = Forward()
class Path(SPARQLNonTerminal):  
    pass
if do_parseactions: Path_p.setParseAction(parseInfoFunc('Path'))

# [94]    PathPrimary       ::=   iri | 'a' | '!' PathNegatedPropertySet | '(' Path ')' 
PathPrimary_p = iri_p | TYPE_kw_p | (NOT_op_p + PathNegatedPropertySet_p) | (LPAR_p + Path_p + RPAR_p)
class PathPrimary(SPARQLNonTerminal):  
    pass
if do_parseactions: PathPrimary_p.setParseAction(parseInfoFunc('PathPrimary'))

# [93]    PathMod   ::=   '?' | '*' | '+' 
PathMod_p = (~VAR1_p + Literal('?')) | Literal('*') | Literal('+')
# PathMod_p = Literal('?') | Literal('*') | Literal('+')
class PathMod(SPARQLNonTerminal):  
    pass
if do_parseactions: PathMod_p.setParseAction(parseInfoFunc('PathMod'))

# [91]    PathElt   ::=   PathPrimary PathMod? 
PathElt_p = PathPrimary_p + Optional(PathMod_p) 
class PathElt(SPARQLNonTerminal):  
    pass
if do_parseactions: PathElt_p.setParseAction(parseInfoFunc('PathElt'))

# [92]    PathEltOrInverse          ::=   PathElt | '^' PathElt 
PathEltOrInverse_p = PathElt_p | (INVERSE_op_p + PathElt_p)
class PathEltOrInverse(SPARQLNonTerminal):  
    pass
if do_parseactions: PathEltOrInverse_p.setParseAction(parseInfoFunc('PathEltOrInverse'))

# [90]    PathSequence      ::=   PathEltOrInverse ( '/' PathEltOrInverse )* 
PathSequence_p = delimitedList(PathEltOrInverse_p, delim='/')
class PathSequence(SPARQLNonTerminal):  
    def render(self):
        return ' / '.join([v[1] if isinstance(v[1], str) else v[1].render() for v in self.getItems()])
if do_parseactions: PathSequence_p.setParseAction(parseInfoFunc('PathSequence'))

# [89]    PathAlternative   ::=   PathSequence ( '|' PathSequence )* 
PathAlternative_p = delimitedList(PathSequence_p, delim='|')
class PathAlternative(SPARQLNonTerminal):
    def render(self):
        return ' | '.join([v[1] if isinstance(v[1], str) else v[1].render() for v in self.getItems()])
if do_parseactions: PathAlternative_p.setParseAction(parseInfoFunc('PathAlternative'))
 
# [88]    Path      ::=   PathAlternative
Path_p << (PathAlternative_p + Empty()) 

# [87]    ObjectPath        ::=   GraphNodePath 
ObjectPath_p = GraphNodePath_p + Empty() 
class ObjectPath(SPARQLNonTerminal):
    pass
if do_parseactions: ObjectPath_p.setParseAction(parseInfoFunc('ObjectPath'))

# [86]    ObjectListPath    ::=   ObjectPath ( ',' ObjectPath )* 
ObjectListPath_p = delimitedList(ObjectPath_p)
class ObjectListPath(SPARQLNonTerminal):
    def render(self):
        return ', '.join([v[1] if isinstance(v[1], str) else v[1].render() for v in self.getItems()])
if do_parseactions: ObjectListPath_p.setParseAction(parseInfoFunc('ObjectListPath'))

# [85]    VerbSimple        ::=   Var 
VerbSimple_p = Var_p + Empty() 
class VerbSimple(SPARQLNonTerminal):
    pass
if do_parseactions: VerbSimple_p.setParseAction(parseInfoFunc('VerbSimple'))

# [84]    VerbPath          ::=   Path
VerbPath_p = Path_p + Empty() 
class VerbPath(SPARQLNonTerminal):
    pass
if do_parseactions: VerbPath_p.setParseAction(parseInfoFunc('VerbPath'))

# [80]    Object    ::=   GraphNode 
Object_p = GraphNode_p + Empty() 
class Object(SPARQLNonTerminal):
    pass
if do_parseactions: Object_p.setParseAction(parseInfoFunc('Object'))
 
# [79]    ObjectList        ::=   Object ( ',' Object )* 
ObjectList_p = delimitedList(Object_p)
class ObjectList(SPARQLNonTerminal):
    def render(self):
        return ', '.join([v[1] if isinstance(v[1], str) else v[1].render() for v in self.getItems()])
if do_parseactions: ObjectList_p.setParseAction(parseInfoFunc('ObjectList'))

# [83]    PropertyListPathNotEmpty          ::=   ( VerbPath | VerbSimple ) ObjectListPath ( ';' ( ( VerbPath | VerbSimple ) ObjectList )? )* 
PropertyListPathNotEmpty_p << ((VerbPath_p | VerbSimple_p) + ObjectListPath_p +  ZeroOrMore(SEMICOL_p + Optional(( VerbPath_p | VerbSimple_p) + ObjectList_p)))

# [82]    PropertyListPath          ::=   PropertyListPathNotEmpty? 
PropertyListPath_p = Optional(PropertyListPathNotEmpty_p)
class PropertyListPath(SPARQLNonTerminal):
    pass
if do_parseactions: PropertyListPath_p.setParseAction(parseInfoFunc('PropertyListPath'))

# [81]    TriplesSameSubjectPath    ::=   VarOrTerm PropertyListPathNotEmpty | TriplesNodePath PropertyListPath 
TriplesSameSubjectPath_p = (VarOrTerm_p + PropertyListPathNotEmpty_p) | (TriplesNodePath_p + PropertyListPath_p)
class TriplesSameSubjectPath(SPARQLNonTerminal):
    pass
if do_parseactions: TriplesSameSubjectPath_p.setParseAction(parseInfoFunc('TriplesSameSubjectPath'))

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
