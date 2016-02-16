import unittest
from sparqlparser.base import *

# Next lines are temporary during development, to be deleted as implementions added to .base
GroupGraphPattern_p << Literal('{}')
TriplesNodePath_p << Literal('($TriplesNodePath)')
TriplesNode_p << Literal('($TriplesNode)')
PropertyListPathNotEmpty_p << Literal('$VerbPath ?ObjectListPath') 

class Test(unittest.TestCase):
    @classmethod
    def makeTestFunc(self, rule, testCases, info=True, debug=0):
        def testFunc():
            if info:
                print('\ntesting', rule, 'with', len(testCases[rule]['pass']), 'pass case(s) and', len(testCases[rule]['fail']), 'fail case(s)')
            if debug >= 3:
                print('\npass cases:', testCases[rule]['pass'])
                print('\nfail cases:', testCases[rule]['fail'])
                print()
            for p in testCases[rule]['pass']:
                if debug >= 1:
                    print('\npass:', p, end=''), 
                if debug >= 3:
                    print(' ( = ' + ' '.join([str(ord(c)) for c in p]), end=' )')
                e = eval(rule + '_p').parseString(p, parseAll=True)
                if debug >= 2:
                    print()
                    e[0].dump()
                    print()
                if debug >= 1:
                    print(' --> ' + str(e), end='')
                    if debug >= 3:
                        print(' ( = ' + ' '.join([str(ord(c)) for c in str(e)[2:-2]]), end=' )')
                assert e[0].isValid()
            for f in testCases[rule]['fail']:
                if debug >= 1:
                    print('\nfail:', f, end='')
                try:
                    e = eval(rule + '_p').parseString(f, parseAll=True)
                    if debug >= 1:
                        print(' --> ', e)
                    if debug >= 3:
                        print(' '.join([str(ord(c)) for c in f]), end=' = ')
                    assert False, 'Should raise ParseException'
                except ParseException:
                    pass
        return testFunc
    
    def setUp(self):
        self.testCases = {}
        

# [173]   PN_LOCAL_ESC      ::=   '\' ( '_' | '~' | '.' | '-' | '!' | '$' | '&' | "'" | '(' | ')' | '*' | '+' | ',' | ';' | '=' | '/' | '?' | '#' | '@' | '%' ) 
         
        self.testCases['PN_LOCAL_ESC'] = {'pass': ['\\&', '\\*'],
                                          'fail': ['b'] }
                
# [172]   HEX       ::=   [0-9] | [A-F] | [a-f] 
        
        self.testCases['HEX'] = {'pass': ['F', '1'],
                                 'fail': ['G', 'F0'] } 
    
# [171]   PERCENT   ::=   '%' HEX HEX
         
        self.testCases['PERCENT'] = {'pass':  ['%'+ s + t for s in self.testCases['HEX']['pass'] for t in self.testCases['HEX']['pass']],
                                     'fail':  ['%'+ s + t for s in self.testCases['HEX']['pass'] for t in self.testCases['HEX']['fail']] + \
                                        ['%'+ s + t for s in self.testCases['HEX']['fail'] for t in self.testCases['HEX']['pass']] + \
                                        [s + t for s in self.testCases['HEX']['pass'] for t in self.testCases['HEX']['pass']] + ['% 00']}

# [170]   PLX       ::=   PERCENT | PN_LOCAL_ESC 

        self.testCases['PLX'] = {'pass':  [s for s in self.testCases['PERCENT']['pass']] + [s for s in self.testCases['PN_LOCAL_ESC']['pass']],
                                 'fail':  ['\\x']}
        
# [164]   PN_CHARS_BASE     ::=   [A-Z] | [a-z] | [#x00C0-#x00D6] | [#x00D8-#x00F6] | [#x00F8-#x02FF] | [#x0370-#x037D] | [#x037F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF]
        
        self.testCases['PN_CHARS_BASE'] = {'pass':    ['S', 'd', '\u00C2', '\u00DA', '\u01FA', '\u037C', '\u200D', 
                                                       '\u2100', '\u2C00', '\u2FEF', '\u00C2', '\uA777', '\uFADC', '\uFFF0', '\U000AFFFC'],
                                           'fail':    ['\u2000', '_'] }
        
# [165]   PN_CHARS_U        ::=   PN_CHARS_BASE | '_' 
        
        self.testCases['PN_CHARS_U'] = {'pass': self.testCases['PN_CHARS_BASE']['pass'].copy(),
                                        'fail': self.testCases['PN_CHARS_BASE']['fail'].copy() }
        self.testCases['PN_CHARS_U']['pass'].append('_')
        self.testCases['PN_CHARS_U']['fail'].remove('_')

# [167]   PN_CHARS          ::=   PN_CHARS_U | '-' | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040]

        self.testCases['PN_CHARS'] = {'pass': self.testCases['PN_CHARS_U']['pass'] + ['\u00B7', '\u0345', '\u2040'],
                                      'fail': ['\u2000']}

# [169]   PN_LOCAL          ::=   (PN_CHARS_U | ':' | [0-9] | PLX ) ((PN_CHARS | '.' | ':' | PLX)* (PN_CHARS | ':' | PLX) )? 

        self.testCases['PN_LOCAL'] = {'pass': [], 'fail': []}
        self.PN_LOCALfirstPart = self.testCases['PN_CHARS_U']['pass'][::6] + [':'] + ['0', '7'] + self.testCases['PLX']['pass'][::3]
        self.PN_LOCALoptionalPart1 = self.testCases['PN_CHARS']['pass'][1::10] + ['.', ':'] + self.testCases['PLX']['pass'][:2]
        self.PN_LOCALoptionalPart2 = self.testCases['PN_CHARS']['pass'][2::10] + [':'] + self.testCases['PLX']['pass'][1::2]
        for p1 in self.PN_LOCALfirstPart:
            for p2a in self.PN_LOCALoptionalPart1:
                for p2b in self.PN_LOCALoptionalPart1:
                    for p3 in self.PN_LOCALoptionalPart2:
                        self.testCases['PN_LOCAL']['pass'] += [p1]
                        self.testCases['PN_LOCAL']['pass'] += [p1 + p3]
                        self.testCases['PN_LOCAL']['pass'] += [p1 + p2a + p3]
                        self.testCases['PN_LOCAL']['pass'] += [p1 + p2a + p2b + p3]
        self.testCases['PN_LOCAL']['fail'] = ['\n']
        
# [168]   PN_PREFIX         ::=   PN_CHARS_BASE ((PN_CHARS|'.')* PN_CHARS)?
    
        self.testCases['PN_PREFIX'] = {'pass': [], 'fail': []}
        self.PN_PREFIXfirstPart = self.testCases['PN_CHARS_BASE']['pass'][::5]
        self.PN_PREFIXoptionalPart1 = self.testCases['PN_CHARS']['pass'][1::5] + ['.']
        self.PN_PREFIXoptionalPart2 = self.testCases['PN_CHARS']['pass'][2::5]
        for p1 in self.PN_PREFIXfirstPart:
            for p2a in self.PN_PREFIXoptionalPart1:
                for p2b in self.PN_PREFIXoptionalPart1:
                    for p3 in self.PN_PREFIXoptionalPart2:
                        self.testCases['PN_PREFIX']['pass'] += [p1]
                        self.testCases['PN_PREFIX']['pass'] += [p1 + p3]
                        self.testCases['PN_PREFIX']['pass'] += [p1 + p2a + p3]
                        self.testCases['PN_PREFIX']['pass'] += [p1 + p2a + p2b + p3]
        self.testCases['PN_PREFIX']['fail'] = ['_']
    
# [166]   VARNAME   ::=   ( PN_CHARS_U | [0-9] ) ( PN_CHARS_U | [0-9] | #x00B7 | [#x0300-#x036F] | [#x203F-#x2040] )* 

        self.testCases['VARNAME'] = {'pass': [], 'fail': []}
        self.VARNAMEfirstPart = self.testCases['PN_CHARS_U']['pass'][::6] + ['4']
        self.VARNAMEsecondPart = self.testCases['PN_CHARS_U']['pass'][1::6] + ['9'] + ['\u0301']
        for p1 in self.VARNAMEfirstPart:
            for p2a in self.VARNAMEsecondPart:
                for p2b in self.VARNAMEsecondPart:
                        self.testCases['VARNAME']['pass'] += [p1]
                        self.testCases['VARNAME']['pass'] += [p1 + p2a]
                        self.testCases['VARNAME']['pass'] += [p1 + p2a + p2b]
        self.testCases['VARNAME']['fail'] = ['abc.de']
        
# [162]   WS        ::=   #x20 | #x9 | #xD | #xA 

        self.testCases['WS'] = {'pass': ['\u0020', '\u0009', '\u000D', '\u000A'],
                                'fail': ['\u2000', 'x']}

# [163]   ANON      ::=   '[' WS* ']' 

        self.testCases['ANON'] = {'pass': [], 'fail': []}   
        for p1a in self.testCases['WS']['pass']:
            for p1b in self.testCases['WS']['pass']:
                self.testCases['ANON']['pass'] += ['[' + ']']
                self.testCases['ANON']['pass'] += ['[' + p1a + ']']
                self.testCases['ANON']['pass'] += ['[' + p1a + p1b + ']']
        self.testCases['ANON']['fail'] += ['[ x]']

# [161]   NIL       ::=   '(' WS* ')' 

        self.testCases['NIL'] = {'pass': [], 'fail': []}  
        for p1a in self.testCases['WS']['pass']:
            for p1b in self.testCases['WS']['pass']:
                self.testCases['NIL']['pass'] += ['()']
                self.testCases['NIL']['pass'] += ['('+ p1a + ')']
                self.testCases['NIL']['pass'] += ['('+ p1a + p1b + ')']
        self.testCases['NIL']['fail'] += ['( x)']

# [160]   ECHAR     ::=   '\' [tbnrf\"'] 

        self.testCases['ECHAR'] = {'pass': [r'\t', r'\b', r'\n', r'\r', r'\f', r'\\', r'\"', r"\'"],
                                   'fail': ['( x)']}

# [159]   STRING_LITERAL_LONG2      ::=   '"""' ( ( '"' | '""' )? ( [^"\] | ECHAR ) )* '"""' 
        
        self.testCases['STRING_LITERAL_LONG2'] = {'pass': [], 'fail': []}  
        bracket = '"""' 
        quoteFills = ['','"', '""']
        text = ['\\t', '\\\\', 'a', '\u00C0\u00FA x\n', 'ab c', 'a \\r'] + self.testCases['ECHAR']['pass'][::3]
        for p1a in quoteFills:
            for p1b in quoteFills:
                for p2a in text:
                    for p2b in text:
                        self.testCases['STRING_LITERAL_LONG2']['pass'] += [bracket + p1a + p2a + bracket]
                        self.testCases['STRING_LITERAL_LONG2']['pass'] += [bracket + p1a + p2a + p1b + p2b + bracket]
        self.testCases['STRING_LITERAL_LONG2']['fail'] += ['"""k"""k""""']
        
# [158]   STRING_LITERAL_LONG1      ::=   "'''" ( ( "'" | "''" )? ( [^'\] | ECHAR ) )* "'''" 
        
        self.testCases['STRING_LITERAL_LONG1'] = {'pass': [], 'fail': []}
        bracket = "'''" 
        quoteFills = ["","'", "''"]
        text = ['\\t', '\\\\', 'a', '\u00C0\u00FA x\n', 'ab c', 'a \\r'] + self.testCases['ECHAR']['pass'][::3]
        for p1a in quoteFills:
            for p1b in quoteFills:
                for p2a in text:
                    for p2b in text:
                        self.testCases['STRING_LITERAL_LONG1']['pass'] += [bracket + p1a + p2a + bracket]
                        self.testCases['STRING_LITERAL_LONG1']['pass'] += [bracket + p1a + p2a + p1b + p2b + bracket]
        self.testCases['STRING_LITERAL_LONG1']['fail'] += ["'''k'''k''''"]
        
# [157]   STRING_LITERAL2   ::=   '"' ( ([^#x22#x5C#xA#xD]) | ECHAR )* '"' 
        
        self.testCases['STRING_LITERAL2'] = {'pass': ['"te\\n"', '"\u00C0"', '"blah blah"'],
                                             'fail': ['"\n"', '"""k"""k"""']} 
        
# [156]   STRING_LITERAL1   ::=   "'" ( ([^#x27#x5C#xA#xD]) | ECHAR )* "'" 

        self.testCases['STRING_LITERAL1'] = {'pass': ["'te\\n'", "'\u00C0'", "'blah blah'"],
                                             'fail': ["'\n'", "'''k'''k'''"]} 

# [155]   EXPONENT          ::=   [eE] [+-]? [0-9]+            

        self.testCases['EXPONENT'] = {'pass': ['E+0','e-34', 'E-4455', 'E-3'],
                                      'fail': ['e_34', 'E-', 'E3', 'E -3']}            

# [148]   DOUBLE    ::=   [0-9]+ '.' [0-9]* EXPONENT | '.' ([0-9])+ EXPONENT | ([0-9])+ EXPONENT 
         
        self.testCases['DOUBLE'] = {'pass': ['34.0E+12', '.45e-0', '9E-12'],
                                    'fail': ['.E12', '34.0 E3', 'E22']}
         
# [154]   DOUBLE_NEGATIVE   ::=   '-' DOUBLE 
        
        self.testCases['DOUBLE_NEGATIVE'] = {'pass': ['-34.0E+12', '-.45e-0', '-9E-12'],
                                             'fail': ['+34.0E+12', '- .E12', '34.0 E3', 'E22', '9E-12']} 
         
# # [151]   DOUBLE_POSITIVE   ::=   '+' DOUBLE 

        self.testCases['DOUBLE_POSITIVE'] = {'pass': ['+34.0E+12', '+.45e-0', '+9E-12'],
                                             'fail': ['-34.0E+12', '_ .E12', '34.0 E3', 'E22', '9E-12']} 

# [147]   DECIMAL   ::=   [0-9]* '.' [0-9]+ 

        self.testCases['DECIMAL'] = {'pass': ['34.0', '0.0', '.450'],
                                      'fail': ['3.4.5', '3.', '5']} 

# [153]   DECIMAL_NEGATIVE          ::=   '-' DECIMAL 

        self.testCases['DECIMAL_NEGATIVE'] = {'pass': ['-34.0', '-0.0', '-.450'],
                                              'fail': ['+3.4', '3.', '-5']} 

# [150]   DECIMAL_POSITIVE          ::=   '+' DECIMAL 

        self.testCases['DECIMAL_POSITIVE'] = {'pass': ['+34.0', '+0.0', '+.450'],
                                              'fail': ['-3.4', '3.', '+5']} 

# [146]   INTEGER   ::=   [0-9]+ 

        self.testCases['INTEGER'] = {'pass': ['3', '45', '056'],
                                     'fail':['-34', '3.', '0x34']} 

# [152]   INTEGER_NEGATIVE          ::=   '-' INTEGER

        self.testCases['INTEGER_NEGATIVE'] = {'pass': ['-3', '-45', '-056'],
                                              'fail':['-34.0, +34', '3', '+0x34']} 

# [149]   INTEGER_POSITIVE          ::=   '+' INTEGER 

        self.testCases['INTEGER_POSITIVE'] = {'pass':  ['+3', '+45', '+056'],
                                        'fail':['-34', '3', '-0x34']} 

# [145]   LANGTAG   ::=   '@' [a-zA-Z]+ ('-' [a-zA-Z0-9]+)* 

        self.testCases['LANGTAG'] = {'pass':   ['@sf', '@sd-f4g-234'],
                                     'fail':['@@sf', '@sd_f4g-234', '@s f', '@3sf']} 

# [144]   VAR2      ::=   '$' VARNAME 
     
        self.testCases['VAR2'] = {'pass': [], 'fail': []}
        for v in self.testCases['VARNAME']['pass']:
            self.testCases['VAR2']['pass'] += ['$'+ v]
        for v in self.testCases['VARNAME']['fail']:
            self.testCases['VAR2']['fail'] += [v, '?'+ v, '$$'+ v]
         
# [143]   VAR1      ::=   '?' VARNAME
            
        self.testCases['VAR1'] = {'pass': [], 'fail': []}
        for v in self.testCases['VARNAME']['pass']:
            self.testCases['VAR1']['pass'] += ['?'+ v]
        for v in self.testCases['VARNAME']['fail']:
            self.testCases['VAR1']['fail'] += [v, '$'+ v, '??'+ v]
            
# [142]   BLANK_NODE_LABEL          ::=   '_:' ( PN_CHARS_U | [0-9] ) ((PN_CHARS|'.')* PN_CHARS)?

        self.testCases['BLANK_NODE_LABEL'] = {'pass': [], 'fail': []}
        self.BLANK_NODE_LABELfirstPart = self.testCases['PN_CHARS_U']['pass'][::5] + ['0', '7']
        self.BLANK_NODE_LABELoptionalPart1 = self.testCases['PN_CHARS']['pass'][1::7] + ['.']
        self.BLANK_NODE_LABELoptionalPart2 = self.testCases['PN_CHARS']['pass'][2::7] 
        for p1 in self.BLANK_NODE_LABELfirstPart:
            for p2a in self.BLANK_NODE_LABELoptionalPart1:
                for p2b in self.BLANK_NODE_LABELoptionalPart1:
                    for p3 in self.BLANK_NODE_LABELoptionalPart2:
                        self.testCases['BLANK_NODE_LABEL']['pass'] += ['_:' + p1]
                        self.testCases['BLANK_NODE_LABEL']['pass'] += ['_:' + p1 + p3]
                        self.testCases['BLANK_NODE_LABEL']['pass'] += ['_:' + p1 + p2a + p3]
                        self.testCases['BLANK_NODE_LABEL']['pass'] += ['_:' + p1 + p2a + p2b + p3]
        self.testCases['BLANK_NODE_LABEL']['fail'] = ['_:.bla', 'bla', ':bla.clal_', '_:bla.clal.']

# [140]   PNAME_NS          ::=   PN_PREFIX? ':'

        self.testCases['PNAME_NS'] = {'pass': [p + ':' for p in self.testCases['PN_PREFIX']['pass']],
                                      'fail': ['_:', 'a:b', '_:a']}

# [141]   PNAME_LN          ::=   PNAME_NS PN_LOCAL 

        self.testCases['PNAME_LN'] = {'pass': [], 'fail': []}
        for p1 in self.testCases['PNAME_NS']['pass'][::200]:
            for p2 in self.testCases['PN_LOCAL']['pass'][::2000]:
                self.testCases['PNAME_LN']['pass'] += [p1 + p2]
        self.testCases['PNAME_LN']['fail'] += ['blah', ':d d']
            
# [139]   IRIREF    ::=   '<' ([^<>"{}|^`\]-[#x00-#x20])* '>' 

        self.testCases['IRIREF'] = {'pass': ['<testIri>', '<work;een/IRI>', '<test$iri:dach][t-het-wel>'],
                                      'fail': ['work IRI', '<foute}iri>', '<foute|iri>', '<nog\teen foute>', '<en]nogeen']}
        
# [138]   BlankNode         ::=   BLANK_NODE_LABEL | ANON 

        self.testCases['BlankNode'] = {'pass': self.testCases['BLANK_NODE_LABEL']['pass'] + self.testCases['ANON']['pass'],
                                       'fail': self.testCases['BLANK_NODE_LABEL']['fail']}
        
# [137]   PrefixedName      ::=   PNAME_LN | PNAME_NS 

        self.testCases['PrefixedName'] = {'pass': self.testCases['PNAME_LN']['pass'] + self.testCases['PNAME_NS']['pass'],
                                          'fail': self.testCases['PNAME_LN']['fail'] + ['_:']}
        
# [136]   iri       ::=   IRIREF | PrefixedName 

        self.testCases['iri'] = {'pass': self.testCases['IRIREF']['pass'] + self.testCases['PrefixedName']['pass'],
                                 'fail': self.testCases['IRIREF']['fail'] + self.testCases['PrefixedName']['fail']}

# [135]   String    ::=   STRING_LITERAL1 | STRING_LITERAL2 | STRING_LITERAL_LONG1 | STRING_LITERAL_LONG2 

        self.testCases['String'] = {'pass': self.testCases['STRING_LITERAL1']['pass'] + \
                                            self.testCases['STRING_LITERAL2']['pass'] + \
                                            self.testCases['STRING_LITERAL_LONG1']['pass'] + \
                                            self.testCases['STRING_LITERAL_LONG2']['pass'],
                                            
                                    'fail': self.testCases['STRING_LITERAL1']['fail'] +\
                                            self.testCases['STRING_LITERAL2']['fail'] +\
                                            self.testCases['STRING_LITERAL_LONG1']['fail'] +\
                                            self.testCases['STRING_LITERAL_LONG2']['fail']
                                    }
                                           
# [134]   BooleanLiteral    ::=   'true' | 'false' 
        
        self.testCases['BooleanLiteral'] = {'pass': ['true', 'false'],
                                            'fail': ['True', 'TRUE', 'False', 'FALSE', 'niet']}
        
# [133]   NumericLiteralNegative    ::=   INTEGER_NEGATIVE | DECIMAL_NEGATIVE | DOUBLE_NEGATIVE 

        self.testCases['NumericLiteralNegative'] = {'pass': self.testCases['INTEGER_NEGATIVE']['pass'] + \
                                                            self.testCases['DECIMAL_NEGATIVE']['pass'] + \
                                                            self.testCases['DOUBLE_NEGATIVE']['pass'],
                                                    'fail': self.testCases['INTEGER_POSITIVE']['pass'] + \
                                                            self.testCases['DECIMAL_POSITIVE']['pass'] + \
                                                            self.testCases['DOUBLE_POSITIVE']['pass'] + \
                                                            self.testCases['INTEGER']['pass'] + \
                                                            self.testCases['DECIMAL']['pass'] + \
                                                            self.testCases['DOUBLE']['pass']}
             
# [132]   NumericLiteralPositive    ::=   INTEGER_POSITIVE | DECIMAL_POSITIVE | DOUBLE_POSITIVE 

        self.testCases['NumericLiteralPositive'] = {'pass': self.testCases['INTEGER_POSITIVE']['pass'] + \
                                                            self.testCases['DECIMAL_POSITIVE']['pass'] + \
                                                            self.testCases['DOUBLE_POSITIVE']['pass'],
                                                    'fail': self.testCases['INTEGER_NEGATIVE']['pass'] + \
                                                            self.testCases['DECIMAL_NEGATIVE']['pass'] + \
                                                            self.testCases['DOUBLE_NEGATIVE']['pass'] + \
                                                            self.testCases['INTEGER']['pass'] + \
                                                            self.testCases['DECIMAL']['pass'] + \
                                                            self.testCases['DOUBLE']['pass']}

# [131]   NumericLiteralUnsigned    ::=   INTEGER | DECIMAL | DOUBLE 
        self.testCases['NumericLiteralUnsigned'] = {'pass': self.testCases['INTEGER']['pass'] + \
                                                            self.testCases['DECIMAL']['pass'] + \
                                                            self.testCases['DOUBLE']['pass'],
                                                    'fail': self.testCases['INTEGER_NEGATIVE']['pass'] + \
                                                            self.testCases['DECIMAL_NEGATIVE']['pass'] + \
                                                            self.testCases['DOUBLE_NEGATIVE']['pass'] + \
                                                            self.testCases['INTEGER_POSITIVE']['pass'] + \
                                                            self.testCases['DECIMAL_POSITIVE']['pass'] + \
                                                            self.testCases['DOUBLE_POSITIVE']['pass']} 
        
# [130]   NumericLiteral    ::=   NumericLiteralUnsigned | NumericLiteralPositive | NumericLiteralNegative 
        self.testCases['NumericLiteral'] = {'pass': self.testCases['NumericLiteralNegative']['pass'] + \
                                                    self.testCases['NumericLiteralPositive']['pass'] + \
                                                    self.testCases['NumericLiteralUnsigned']['pass'],
                                            'fail': ['544,55.6', '', '33.8F34']} 
        
# [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
        self.testCases['RDFLiteral'] = {'pass': [], 'fail': []}
        for p1 in self.testCases['String']['pass'][::100]:
            for p2 in self.testCases['LANGTAG']['pass'][::100]:
                for p3 in self.testCases['iri']['pass'][::100]:
                    self.testCases['RDFLiteral']['pass'] += [p1]
                    self.testCases['RDFLiteral']['pass'] += [p1 + p2]
                    self.testCases['RDFLiteral']['pass'] += [p1 + '^^' + p3]
                    self.testCases['RDFLiteral']['pass'] += ['"work string"^^<testiri>', '"work string"@sd-f4g-234']
        self.testCases['RDFLiteral']['fail'] += ['@sf^en', '@sf^^', 'sf^^<nl-be>', '"work string"^^testiri']
               
# Expression
# "Expression" at this point is a Forward declaration.
        self.testCases['Expression'] = {'pass': [], 'fail': []}
        self.testCases['Expression']['pass'] += ['"*Expression*"'] 
        self.testCases['Expression']['fail'] += ['"*NoExpression*'] 

# ExpressionList
# "ExpressionList" is an auxiliary production in our grammar. It does not occur in the SPARQL EBNF syntax.
# These testcases are just a few basic expressions. No further elaboration is foreseen.
        self.testCases['ExpressionList'] = {'pass': [],
                                        'fail': []}
        self.testCases['ExpressionList']['pass'] += ['"*Expression*", "*Expression*"'] 
        self.testCases['ExpressionList']['fail'] += ['*NoExpression*'] 
               
# [71]    ArgList   ::=   NIL | '(' 'DISTINCT'? Expression ( ',' Expression )* ')' 
        self.testCases['ArgList'] = {'pass': [], 'fail': []}
        for p1a in self.testCases['Expression']['pass']:
            for p1b in self.testCases['Expression']['pass']:
                self.testCases['ArgList']['pass'] += ['( )', '(Distinct ' + p1a + ')', '(DISTINCT ' + p1a +')', '(DISTINCT ' + p1a + ', ' + p1b + ')']
                self.testCases['ArgList']['fail'] += ['[]', 'Not an arglist', '(DISTINCT)']
        for p1 in self.testCases['Expression']['fail']:
            self.testCases['ArgList']['fail'] += [p1]
        
# [128]   iriOrFunction     ::=   iri ArgList? 
        self.testCases['iriOrFunction'] = {'pass': [], 'fail': []}
        for p1 in self.testCases['iri']['pass'][::100]:
            for p2 in self.testCases['ArgList']['pass'][::100]:
                self.testCases['iriOrFunction']['pass'] += [p1]
                self.testCases['iriOrFunction']['pass'] += [p1 + ' ' + p2]
                self.testCases['iriOrFunction']['pass'] += [p1 + p2]
        self.testCases['iriOrFunction']['fail'] += self.testCases['ArgList']['pass']
        
# [127]   Aggregate         ::=     'COUNT' '(' 'DISTINCT'? ( '*' | Expression ) ')'
        self.testCases['Aggregate'] = {'pass': [], 'fail': []}
#             | 'SUM' '(' 'DISTINCT'? Expression ')' 
#             | 'MIN' '(' 'DISTINCT'? Expression ')' 
#             | 'MAX' '(' 'DISTINCT'? Expression ')' 
#             | 'AVG' '(' 'DISTINCT'? Expression ')' 
#             | 'SAMPLE' '(' 'DISTINCT'? Expression ')'
        for op in ['COUNT', 'Sum', 'min', 'MAX', 'AVG', 'SAMPLE']:
            self.testCases['Aggregate']['pass'] += [op + '(*)', op + ' (* ) ', op + ' (DISTINCT *)']
            for p in self.testCases['Expression']['pass']: 
                self.testCases['Aggregate']['pass'] += [op + '(' + p + ' )', op + ' (DISTINCT ' + p + ')']
        self.testCases['Aggregate']['fail'] += [op + '()', op, op + ' (DISTINCT )'] 
        
#             | 'GROUP_CONCAT' '(' 'DISTINCT'? Expression ( ';' 'SEPARATOR' '=' String )? ')'
        for p in self.testCases['Expression']['pass']: 
            for s in self.testCases['String']['pass'][1::100]:
                self.testCases['Aggregate']['pass'] += ['GROUP_CONCAT(' + p + ' )', 'GROUP_CONCAT (DISTINCT ' + p + ' ; SEPARATOR = ' + s + ')']
        self.testCases['Aggregate']['fail'] += ['GROUP_CONCAT()', 'GROUP_CONCAT', 'GROUP_CONCAT (DISTINCT )']          

# GroupGraphPattern
# "GroupGraphPattern" at this point is a Forward declaration.
        self.testCases['GroupGraphPattern'] = {'pass': [], 'fail': []}
        self.testCases['GroupGraphPattern']['pass'] += ['{}'] 
        self.testCases['GroupGraphPattern']['fail'] += ['*NoGroupGraphPattern*'] 

# [126]   NotExistsFunc     ::=   'NOT' 'EXISTS' GroupGraphPattern 
        self.testCases['NotExistsFunc'] = {'pass': [], 'fail': []}
        for p in self.testCases['GroupGraphPattern']['pass']:
            self.testCases['NotExistsFunc']['pass'] += ['NOT exists ' + p]
            self.testCases['NotExistsFunc']['fail'] += ['EXISTS ' + p]

# [125]   ExistsFunc        ::=   'EXISTS' GroupGraphPattern 
        self.testCases['ExistsFunc'] = {'pass': [], 'fail': []}
        for p in self.testCases['GroupGraphPattern']['pass']:
            self.testCases['ExistsFunc']['pass'] += ['EXISTS ' + p]
            self.testCases['ExistsFunc']['fail'] += ['NOT EXISTS ' + p]
            
# [124]   StrReplaceExpression      ::=   'REPLACE' '(' Expression ',' Expression ',' Expression ( ',' Expression )? ')' 
        self.testCases['StrReplaceExpression'] = {'pass': [], 'fail': []}
        for p1 in self.testCases['Expression']['pass']:
            for p2 in self.testCases['Expression']['pass']:
                self.testCases['StrReplaceExpression']['pass'] += ['REPLACE (' + p1 + ' ,' + p2 + ',' + p1 + ')', 'REPLACE( ' + p1 + ' ,' + p2 + ',' + p1 + ' , ' + p2 + ')']
        for p1 in self.testCases['Expression']['pass']:
            for p2 in self.testCases['Expression']['pass']:
                self.testCases['StrReplaceExpression']['fail'] += ['REPLACE()', 'REPLACE(' + p1 + ')', 'REPLACE(' + p1 + ' , ' + p2 + ')']
        for p1 in self.testCases['Expression']['fail']:
            for p2 in self.testCases['Expression']['pass']:
                self.testCases['StrReplaceExpression']['fail'] += ['REPLACE ' + p1 + ')', 'REPLACE ' + p1 + ' ,' + p2 + ')', 'REPLACE ' + p2 + ' ,' + p1 + ',' + p2 + ')']
                
# [123]   SubstringExpression       ::=   'SUBSTR' '(' Expression ',' Expression ( ',' Expression )? ')' 
        self.testCases['SubstringExpression'] = {'pass': [], 'fail': []}
        for p1 in self.testCases['Expression']['pass']:
            for p2 in self.testCases['Expression']['pass']:
                self.testCases['SubstringExpression']['pass'] += ['SUBSTR (' + p1 + ' ,' + p2 + ')', 'SUBSTR( ' + p2 + ',' + p1 + ' , ' + p2 + ')']
        for p1 in self.testCases['Expression']['pass']:
            for p2 in self.testCases['Expression']['pass']:
                self.testCases['SubstringExpression']['fail'] += ['SUBSTR()', 'SUBSTR(' + p1 + ')', 'SUBSTR(' + p2 + ')']
        for p1 in self.testCases['Expression']['fail']:
            for p2 in self.testCases['Expression']['pass']:
                self.testCases['SubstringExpression']['fail'] += ['SUBSTR ' + p1 + ')', 'SUBSTR ' + p1 + ' ,' + p2 + ')']
                
# [122]   RegexExpression   ::=   'REGEX' '(' Expression ',' Expression ( ',' Expression )? ')' 
        self.testCases['RegexExpression'] = {'pass': [], 'fail': []}
        for p1 in self.testCases['Expression']['pass']:
            for p2 in self.testCases['Expression']['pass']:
                self.testCases['RegexExpression']['pass'] += ['REGEX (' + p1 + ' ,' + p2 + ')', 'REGEX( ' + p2 + ',' + p1 + ' , ' + p2 + ')']
        for p1 in self.testCases['Expression']['pass']:
            for p2 in self.testCases['Expression']['pass']:
                self.testCases['RegexExpression']['fail'] += ['REGEX()', 'REGEX(' + p1 + ')', 'REGEX(' + p2 + ')']
        for p1 in self.testCases['Expression']['fail']:
            for p2 in self.testCases['Expression']['pass']:
                self.testCases['RegexExpression']['fail'] += ['REGEX ' + p1 + ')', 'REGEX ' + p1 + ' ,' + p2 + ')']
                
# [108]   Var       ::=   VAR1 | VAR2             
        self.testCases['Var'] = {'pass': [], 'fail': []}
        self.testCases['Var']['pass'] += self.testCases['VAR1']['pass']
        self.testCases['Var']['pass'] += self.testCases['VAR2']['pass']
        self.testCases['Var']['fail'] += self.testCases['VARNAME']['pass']
        self.testCases['Var']['fail'] += ['??test', '$$test']

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
        self.testCases['BuiltInCall'] = {'pass': [], 'fail': []} 
        self.testCases['BuiltInCall']['pass'] += self.testCases['Aggregate']['pass']
        self.testCases['BuiltInCall']['pass'] += ['STR ( "*Expression*" )',
                                                'LANG ( "*Expression*" )',
                                                'LANGMATCHES ( "*Expression*" , "*Expression*" )',
                                                'DATATYPE ( "*Expression*" )',
                                                'BOUND ( $Var )',
                                                'BOUND ( ?Var )',
                                                'IRI ( "*Expression*" )',
                                                'URI ( "*Expression*" )',
                                                'BNODE ( "*Expression*" )',
                                                'BNODE ()',
                                                'RAND ()',
                                                'ABS ( "*Expression*" )',
                                                'CEIL ( "*Expression*" )',
                                                'FLOOR ( "*Expression*" )',
                                                'ROUND ( "*Expression*" )',
                                                'CONCAT "*Expression*"',
                                                'CONCAT "*Expression*", "*Expression*", "*Expression*"',
                                                'SUBSTR ( "*Expression*" , "*Expression*" )',
                                                'SUBSTR ( "*Expression*" , "*Expression*", "*Expression*" )',
                                                'STRLEN ( "*Expression*" )',
                                                'REPLACE ( "*Expression*" , "*Expression*", "*Expression*" )',
                                                'REPLACE ( "*Expression*" , "*Expression*", "*Expression*", "*Expression*" )',
                                                'UCASE ( "*Expression*" )',
                                                'LCASE ( "*Expression*" )',
                                                'ENCODE_FOR_URI ( "*Expression*" )',
                                                'CONTAINS ( "*Expression*" , "*Expression*" )',
                                                'STRSTARTS ( "*Expression*" , "*Expression*" )',
                                                'STRENDS ( "*Expression*" , "*Expression*" )',
                                                'STRBEFORE ( "*Expression*" , "*Expression*" )',
                                                'STRAFTER ( "*Expression*" , "*Expression*" )',
                                                'YEAR ( "*Expression*" )',
                                                'MONTH ( "*Expression*" )',
                                                'DAY ( "*Expression*" )',
                                                'HOURS ( "*Expression*" )',
                                                'MINUTES ( "*Expression*" )',
                                                'SECONDS ( "*Expression*" )',
                                                'TIMEZONE ( "*Expression*" )',
                                                'TZ ( "*Expression*" )',
                                                'NOW ()',
                                                'UUID ()',
                                                'STRUUID()',
                                                'MD5 ( "*Expression*" )',
                                                'SHA1 ( "*Expression*" )',
                                                'SHA256 ( "*Expression*" )',
                                                'SHA384 ( "*Expression*" )',
                                                'SHA512 ( "*Expression*" )',
                                                'COALESCE "*Expression*", "*Expression*"',
                                                'IF ( "*Expression*" , "*Expression*" , "*Expression*" )',
                                                'STRLANG ( "*Expression*" , "*Expression*" )',
                                                'STRDT ( "*Expression*" , "*Expression*" )',
                                                'sameTerm ( "*Expression*" , "*Expression*" )',
                                                'isIRI ( "*Expression*" )',
                                                'isURI ( "*Expression*" )',
                                                'isBLANK ( "*Expression*" )',
                                                'isLITERAL ( "*Expression*" )',
                                                'isNUMERIC ( "*Expression*" )',
                                                'REGEX ( "*Expression*" , "*Expression*" , "*Expression*" )',
                                                'EXISTS {}',
                                                'NOT EXISTS {}']
        self.testCases['BuiltInCall']['fail'] += ['COUNT DISTINCT (*)', 'sameTerm ("*Expression*", "*Expression*", "*Expression*")']

# [120]   BrackettedExpression      ::=   '(' Expression ')' 
        self.testCases['BracketedExpression'] = {'pass': ['(' + p + ')' for p in self.testCases['Expression']['pass']],
                                                 'fail': ['(' + p + ')' for p in self.testCases['Expression']['fail']]}           
        
# [119]   PrimaryExpression         ::=   BrackettedExpression | BuiltInCall | iriOrFunction | RDFLiteral | NumericLiteral | BooleanLiteral | Var 
        self.testCases['PrimaryExpression'] = {'pass': [], 'fail': []}
        self.testCases['PrimaryExpression']['pass'] += self.testCases['BracketedExpression']['pass']      
        self.testCases['PrimaryExpression']['pass'] += self.testCases['BuiltInCall']['pass']      
        self.testCases['PrimaryExpression']['pass'] += self.testCases['iriOrFunction']['pass']      
        self.testCases['PrimaryExpression']['pass'] += self.testCases['RDFLiteral']['pass'][::10]     
        self.testCases['PrimaryExpression']['pass'] += self.testCases['NumericLiteral']['pass']      
        self.testCases['PrimaryExpression']['pass'] += self.testCases['BooleanLiteral']['pass']      
        self.testCases['PrimaryExpression']['pass'] += self.testCases['Var']['pass']      
        self.testCases['PrimaryExpression']['fail'] += ['algebra']    

# [118]   UnaryExpression   ::=     '!' PrimaryExpression 
#             | '+' PrimaryExpression 
#             | '-' PrimaryExpression 
#             | PrimaryExpression 
        self.testCases['UnaryExpression'] = {'pass': [], 'fail': []}
        self.testCases['UnaryExpression']['pass'] += ['! ' + t for t in self.testCases['PrimaryExpression']['pass'][::4]]      
        self.testCases['UnaryExpression']['pass'] += ['+' + t for t in self.testCases['PrimaryExpression']['pass'][1::4]]      
        self.testCases['UnaryExpression']['pass'] += ['- ' + t for t in self.testCases['PrimaryExpression']['pass'][2::4]]      
        self.testCases['UnaryExpression']['pass'] += self.testCases['PrimaryExpression']['pass'][3::4] 
        self.testCases['UnaryExpression']['fail'] += ['algebra', '!meetkunde', '+ goniometrie', '-stereometrie']     

# [117]   MultiplicativeExpression          ::=   UnaryExpression ( '*' UnaryExpression | '/' UnaryExpression )* 
        self.testCases['MultiplicativeExpression'] = {'pass': [], 'fail': []}
        self.testCases['MultiplicativeExpression']['pass'] += ['<test>()']  
        for p1 in self.testCases['UnaryExpression']['pass'][::1000]:
            for p2 in self.testCases['UnaryExpression']['pass'][1::1000]:
                for p3 in self.testCases['UnaryExpression']['pass'][2::1000]:
                    self.testCases['MultiplicativeExpression']['pass'] += [p1]
                    self.testCases['MultiplicativeExpression']['pass'] += [p1 + '*' + p2]
                    self.testCases['MultiplicativeExpression']['pass'] += [p1 + '/ ' + p2 + '*' + p3]
        self.testCases['MultiplicativeExpression']['fail'] += ['* ' + '<test>']
        
# [116]   AdditiveExpression        ::=   MultiplicativeExpression ( '+' MultiplicativeExpression | '-' MultiplicativeExpression | ( NumericLiteralPositive | NumericLiteralNegative ) ( ( '*' UnaryExpression ) | ( '/' UnaryExpression ) )* )* 
        self.testCases['AdditiveExpression'] = {'pass': [], 'fail': []}
        for m in self.testCases['MultiplicativeExpression']['pass'][::10]:
            for n in self.testCases['NumericLiteralPositive']['pass'][::4] + self.testCases['NumericLiteralNegative']['pass'][::4]:
                for u in self.testCases['UnaryExpression']['pass'][::500]:
                    self.testCases['AdditiveExpression']['pass'] += [m]
                    self.testCases['AdditiveExpression']['pass'] += [m + '+ ' + m]
                    self.testCases['AdditiveExpression']['pass'] += [m + '-' + m + '-' + m]
                    self.testCases['AdditiveExpression']['pass'] += [m + n]
                    self.testCases['AdditiveExpression']['pass'] += [m + n + '*' + u]
                    self.testCases['AdditiveExpression']['pass'] += [m + n + '*' + u + '/' + u]
        self.testCases['AdditiveExpression']['fail'] = ['algebra']

            

        
# [115]   NumericExpression         ::=   AdditiveExpression 
        self.testCases['NumericExpression'] = {'pass': [], 'fail': []}
        for m in self.testCases['MultiplicativeExpression']['pass'][1::10]:
            for n in self.testCases['NumericLiteralPositive']['pass'][1::4] + self.testCases['NumericLiteralNegative']['pass'][::4]:
                for u in self.testCases['UnaryExpression']['pass'][1::500]:
                    self.testCases['NumericExpression']['pass'] += [m]
                    self.testCases['NumericExpression']['pass'] += [m + '+ ' + m]
                    self.testCases['NumericExpression']['pass'] += [m + '-' + m + '-' + m]
                    self.testCases['NumericExpression']['pass'] += [m + n]
                    self.testCases['NumericExpression']['pass'] += [m + n + '*' + u]
                    self.testCases['NumericExpression']['pass'] += [m + n + '*' + u + '/' + u]
        self.testCases['NumericExpression']['fail'] = ['algebra']

# [114]   RelationalExpression      ::=   NumericExpression ( '=' NumericExpression | '!=' NumericExpression | '<' NumericExpression | '>' NumericExpression | '<=' NumericExpression | '>=' NumericExpression | 'IN' ExpressionList | 'NOT' 'IN' ExpressionList )? 
        self.testCases['RelationalExpression'] = {'pass': [], 'fail': []}
        for n1 in self.testCases['NumericExpression']['pass'][::50]:
            for n2 in self.testCases['NumericExpression']['pass'][1::50]:
                for e in self.testCases['ExpressionList']['pass']:
                    self.testCases['RelationalExpression']['pass'] += [n1]
                    self.testCases['RelationalExpression']['pass'] += [n1 + ' = ' + n2]
                    self.testCases['RelationalExpression']['pass'] += [n1 + ' != ' + n2]
                    self.testCases['RelationalExpression']['pass'] += [n1 + ' < ' + n2]
                    self.testCases['RelationalExpression']['pass'] += [n1 + ' > ' + n2]
                    self.testCases['RelationalExpression']['pass'] += [n1 + ' <= ' + n2]
                    self.testCases['RelationalExpression']['pass'] += [n1 + ' >= ' + n2]
                    self.testCases['RelationalExpression']['pass'] += [n1 + ' IN ' + e]
                    self.testCases['RelationalExpression']['pass'] += [n1 + ' NOT IN ' + e]
        self.testCases['RelationalExpression']['fail'] = ['algebra']

# [113]   ValueLogical      ::=   RelationalExpression 
        self.testCases['ValueLogical'] = {'pass': self.testCases['RelationalExpression']['pass'], 'fail': self.testCases['RelationalExpression']['fail']}
        
# [112]   ConditionalAndExpression          ::=   ValueLogical ( '&&' ValueLogical )* 
        self.testCases['ConditionalAndExpression'] = {'pass': [], 'fail': []}
        for v1 in self.testCases['ValueLogical']['pass'][::100]:
            for v2 in self.testCases['ValueLogical']['pass'][1::100]:
                for v3 in self.testCases['ValueLogical']['pass'][2::100]:
                    self.testCases['ConditionalAndExpression']['pass'] += [v1]
                    self.testCases['ConditionalAndExpression']['pass'] += [v1 + ' && ' + v2]
                    self.testCases['ConditionalAndExpression']['pass'] += [v1 + ' && ' + v2 + ' && ' + v3]
        self.testCases['ConditionalAndExpression'][ 'fail'] += ['true || false']
        
# [111]   ConditionalOrExpression   ::=   ConditionalAndExpression ( '||' ConditionalAndExpression )* 
        self.testCases['ConditionalOrExpression'] = {'pass': [], 'fail': []}
        for v1 in self.testCases['ConditionalAndExpression']['pass'][::100]:
            for v2 in self.testCases['ConditionalAndExpression']['pass'][1::100]:
                for v3 in self.testCases['ConditionalAndExpression']['pass'][2::100]:
                    self.testCases['ConditionalOrExpression']['pass'] += [v1]
                    self.testCases['ConditionalOrExpression']['pass'] += [v1 + ' || ' + v2]
                    self.testCases['ConditionalOrExpression']['pass'] += [v1 + ' || ' + v2 + ' || ' + v3]
        self.testCases['ConditionalOrExpression'][ 'fail'] += ['algebra']
        
# [110]   Expression        ::=   ConditionalOrExpression 
#         self.testCases['Expression'] = {'pass': self.testCases['ConditionalOrExpression']['pass'], 'fail': self.testCases['ConditionalOrExpression']['fail']}
# Defined above due to Forward declaration

# [109]   GraphTerm         ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | BlankNode | NIL 
        self.testCases['GraphTerm'] = {'pass': [], 'fail': []}
        self.testCases['GraphTerm']['pass'] += self.testCases['RDFLiteral']['pass'][::200]
        self.testCases['GraphTerm']['pass'] += self.testCases['NumericLiteral']['pass']
        self.testCases['GraphTerm']['pass'] += self.testCases['BooleanLiteral']['pass']
        self.testCases['GraphTerm']['pass'] += self.testCases['BlankNode']['pass'][::200]
        self.testCases['GraphTerm']['pass'] += self.testCases['NIL']['pass']
        self.testCases['GraphTerm']['fail'] += ['algebra']

# [107]   VarOrIri          ::=   Var | iri 
        self.testCases['VarOrIri'] = {'pass': [], 'fail': []}
        self.testCases['VarOrIri']['pass'] += self.testCases['Var']['pass'][::200]
        self.testCases['VarOrIri']['pass'] += self.testCases['iri']['pass']      
        self.testCases['VarOrIri']['fail'] += ['algebra']

# [106]   VarOrTerm         ::=   Var | GraphTerm 
        self.testCases['VarOrTerm'] = {'pass': [], 'fail': []}
        self.testCases['VarOrTerm']['pass'] += self.testCases['Var']['pass'][::200]
        self.testCases['VarOrTerm']['pass'] += self.testCases['GraphTerm']['pass']      
        self.testCases['VarOrTerm']['fail'] += ['algebra']
        
# TriplesNodePath
# "TriplesNodePath" at this point is a Forward declaration.
        self.testCases['TriplesNodePath'] = {'pass': [], 'fail': []}
        self.testCases['TriplesNodePath']['pass'] += ['($TriplesNodePath)'] 
        self.testCases['TriplesNodePath']['fail'] += ['*NoTriplesNodePath*'] 
        
# [105]   GraphNodePath     ::=   VarOrTerm | TriplesNodePath 
        self.testCases['GraphNodePath'] = {'pass': [], 'fail': []}
        self.testCases['GraphNodePath']['pass'] += self.testCases['VarOrTerm']['pass']
        self.testCases['GraphNodePath']['pass'] += self.testCases['TriplesNodePath']['pass']      
        self.testCases['GraphNodePath']['fail'] += ['algebra']

# TriplesNode
# "TriplesNode" at this point is a Forward declaration.
        self.testCases['TriplesNode'] = {'pass': [], 'fail': []}
        self.testCases['TriplesNode']['pass'] += ['($TriplesNode)'] 
        self.testCases['TriplesNode']['fail'] += ['*NoTriplesNode*'] 
        
# [104]   GraphNode         ::=   VarOrTerm | TriplesNode 
        self.testCases['GraphNode'] = {'pass': [], 'fail': []}
        self.testCases['GraphNode']['pass'] += self.testCases['VarOrTerm']['pass']
        self.testCases['GraphNode']['pass'] += self.testCases['TriplesNode']['pass']      
        self.testCases['GraphNode']['fail'] += ['algebra']
        
# [103]   CollectionPath    ::=   '(' GraphNodePath+ ')' 
        self.testCases['CollectionPath'] = {'pass': [], 'fail': []}
        for g1 in self.testCases['GraphNodePath']['pass'][::10]:
            for g2 in self.testCases['GraphNodePath']['pass'][1::10]:
                self.testCases['CollectionPath']['pass'] += ['('+ g1 + ')']
                self.testCases['CollectionPath']['pass'] += ['('+ g1 + ' ' + g2 + ')']
        self.testCases['CollectionPath']['fail'] += ['algebra']

# [102]   Collection        ::=   '(' GraphNode+ ')' 
        self.testCases['Collection'] = {'pass': [], 'fail': []}
        for g1 in self.testCases['GraphNode']['pass'][::10]:
            for g2 in self.testCases['GraphNode']['pass'][1::10]:
                self.testCases['Collection']['pass'] += ['('+ g1 + ')']
                self.testCases['Collection']['pass'] += ['('+ g1 + ' ' + g2 + ')']
        self.testCases['Collection']['fail'] += ['algebra']
        
# PropertyListPathNotEmpty
# "PropertyListPathNotEmpty" at this point is a Forward declaration.
        self.testCases['PropertyListPathNotEmpty'] = {'pass': [], 'fail': []}
        self.testCases['PropertyListPathNotEmpty']['pass'] += ['$VerbPath ?ObjectListPath'] 
        self.testCases['PropertyListPathNotEmpty']['fail'] += ['*NoPropertyListPathNotEmpty*'] 
        
# [101]   BlankNodePropertyListPath         ::=   '[' PropertyListPathNotEmpty ']' 
        self.testCases['BlankNodePropertyListPath'] = {'pass': [], 'fail': []}
        for p in self.testCases['PropertyListPathNotEmpty']['pass']:
            self.testCases['BlankNodePropertyListPath']['pass'] += ['[' + p + ']'] 
        self.testCases['BlankNodePropertyListPath']['fail'] += ['[*NoPropertyListPathNotEmpty*]', '[PropertyListPathNotEmpty]'] 

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

            
    def tearDown(self):
        pass
    
#
#
# All Tests
#
#
                                       
    def testPN_LOCAL_ESC(self):
        Test.makeTestFunc('PN_LOCAL_ESC', self.testCases)()   
            
    def testHEX(self):
        Test.makeTestFunc('HEX', self.testCases)()
       
    def testPERCENT(self):
        Test.makeTestFunc('PERCENT', self.testCases)()
       
    def testPLX(self):
        Test.makeTestFunc('PLX', self.testCases)()
               
    def testPN_CHARS_BASE(self):
        Test.makeTestFunc('PN_CHARS_BASE', self.testCases)()
       
    def testPN_CHARS_U(self):
        Test.makeTestFunc('PN_CHARS_U', self.testCases)()
       
    def testPN_CHARS(self):
        Test.makeTestFunc('PN_CHARS', self.testCases)()
               
    def testPN_LOCAL(self):
        Test.makeTestFunc('PN_LOCAL', self.testCases)()     
           
    def testPN_PREFIX(self):
        Test.makeTestFunc('PN_PREFIX', self.testCases)()
               
    def testVARNAME(self):
        Test.makeTestFunc('VARNAME', self.testCases)()
      
# WS is not used
# In the SPARWQL EBNF this production is used for defining NIL and ANON, but in this pyparsing implementation those are implemented independently     
      
    def testANON(self):
        Test.makeTestFunc('ANON', self.testCases)()    
                  
    def testNIL(self):
        Test.makeTestFunc('NIL', self.testCases)()       
                       
    def testECHAR(self):
        Test.makeTestFunc('ECHAR', self.testCases)()       
                 
    def testSTRING_LITERAL_LONG2(self):
        Test.makeTestFunc('STRING_LITERAL_LONG2', self.testCases)()       
          
    def testSTRING_LITERAL_LONG1(self):
        Test.makeTestFunc('STRING_LITERAL_LONG1', self.testCases)()       
                  
    def testSTRING_LITERAL2(self):
        Test.makeTestFunc('STRING_LITERAL2', self.testCases)()       
                      
    def testSTRING_LITERAL1(self):
        Test.makeTestFunc('STRING_LITERAL1', self.testCases)()       
              
    def testEXPONENT(self):
        Test.makeTestFunc('EXPONENT', self.testCases)()       
#              
    def testDOUBLE(self):
        Test.makeTestFunc('DOUBLE', self.testCases)()       
#  
    def testDOUBLE_NEGATIVE(self):
        Test.makeTestFunc('DOUBLE_NEGATIVE', self.testCases)()       
#  
    def testDOUBLE_POSITIVE(self):
        Test.makeTestFunc('DOUBLE_POSITIVE', self.testCases)()       
#  
    def testDECIMAL(self):
        Test.makeTestFunc('DECIMAL', self.testCases)()                     
                      
    def testDECIMAL_NEGATIVE(self):
        Test.makeTestFunc('DECIMAL_NEGATIVE', self.testCases)()       
          
    def testDECIMAL_POSITIVE(self):
        Test.makeTestFunc('DECIMAL_POSITIVE', self.testCases)()       
          
    def testINTEGER(self):
        Test.makeTestFunc('INTEGER', self.testCases)()       
                      
    def testINTEGER_NEGATIVE(self):
        Test.makeTestFunc('INTEGER_NEGATIVE', self.testCases)()       
          
    def testINTEGER_POSITIVE(self):
        Test.makeTestFunc('INTEGER_POSITIVE', self.testCases)()       
                      
    def testLANGTAG(self):
        Test.makeTestFunc('LANGTAG', self.testCases)()       
          
    def testVAR2(self):
        Test.makeTestFunc('VAR2', self.testCases)()       
          
    def testVAR1(self):
        Test.makeTestFunc('VAR1', self.testCases)()       
           
    def testBLANK_NODE_LABEL(self):
        Test.makeTestFunc('BLANK_NODE_LABEL', self.testCases)()       
          
    def testPNAME_NS(self):
        Test.makeTestFunc('PNAME_NS', self.testCases)()       
          
    def testPNAME_LN(self):
        Test.makeTestFunc('PNAME_LN', self.testCases)()
          
    def testIRIREF(self):
        Test.makeTestFunc('IRIREF', self.testCases)()
            
    def testBlankNode(self):
        Test.makeTestFunc('BlankNode', self.testCases)()
          
    def testPrefixedName(self):
        Test.makeTestFunc('PrefixedName', self.testCases)()
          
    def testiri(self):
        Test.makeTestFunc('iri', self.testCases)()
          
    def testString(self):
        Test.makeTestFunc('String', self.testCases)()
         
    def testBooleanLiteral(self):
        Test.makeTestFunc('BooleanLiteral', self.testCases)()
       
    def testNumericLiteralNegative(self):
        Test.makeTestFunc('NumericLiteralNegative', self.testCases)()
        
    def testNumericLiteralPositive(self):
        Test.makeTestFunc('NumericLiteralPositive', self.testCases)()
         
    def testNumericLiteralUnsigned(self):
        Test.makeTestFunc('NumericLiteralUnsigned', self.testCases)()
         
    def testNumericLiteral(self):
        Test.makeTestFunc('NumericLiteral', self.testCases)()
        
    def testRDFLiteral(self):
        Test.makeTestFunc('RDFLiteral', self.testCases)()
       
    def testArgList(self):
        Test.makeTestFunc('ArgList', self.testCases)()
       
    def testiriOrFunction(self):
        Test.makeTestFunc('iriOrFunction', self.testCases)()
       
    def testAggregate(self):
        Test.makeTestFunc('Aggregate', self.testCases)()
       
    def testGroupGraphPattern(self):
        Test.makeTestFunc('GroupGraphPattern', self.testCases)()
       
    def testNotExistsFunc(self):
        Test.makeTestFunc('NotExistsFunc', self.testCases)()
       
    def testExistsFunc(self):
        Test.makeTestFunc('ExistsFunc', self.testCases)()
       
    def testStrReplaceExpression(self):
        Test.makeTestFunc('StrReplaceExpression', self.testCases)()
       
    def testSubstringExpression(self):
        Test.makeTestFunc('SubstringExpression', self.testCases)()
       
    def testRegexExpression(self):
        Test.makeTestFunc('RegexExpression', self.testCases)()
       
    def testVar(self):
        Test.makeTestFunc('Var', self.testCases)()
       
    def testBuiltInCall(self):
        Test.makeTestFunc('BuiltInCall', self.testCases)()
       
    def testBracketedExpression(self):
        Test.makeTestFunc('BracketedExpression', self.testCases)()
       
    def testPrimaryExpression(self):
        Test.makeTestFunc('PrimaryExpression', self.testCases)()
        
    def testUnaryExpression(self):
        Test.makeTestFunc('UnaryExpression', self.testCases)()
        
    def testMultiplicativeExpression(self):
        Test.makeTestFunc('MultiplicativeExpression', self.testCases)()
        
    def testAdditiveExpression(self):
        Test.makeTestFunc('AdditiveExpression', self.testCases)()
        
    def testNumericExpression(self):
        Test.makeTestFunc('NumericExpression', self.testCases)()
       
    def testRelationalExpression(self):
        Test.makeTestFunc('RelationalExpression', self.testCases)()
       
    def testValueLogical(self):
        Test.makeTestFunc('ValueLogical', self.testCases)()
       
    def testConditionalAndExpression(self):
        Test.makeTestFunc('ConditionalAndExpression', self.testCases)()
      
    def testConditionalOrExpression(self):
        Test.makeTestFunc('ConditionalOrExpression', self.testCases)()
      
    def testExpression(self):
        Test.makeTestFunc('Expression', self.testCases)()
             
    def testGraphTerm(self):
        Test.makeTestFunc('GraphTerm', self.testCases)()
             
    def testVarOrIri(self):
        Test.makeTestFunc('VarOrIri', self.testCases)()
      
    def testVarOrTerm(self):
        Test.makeTestFunc('VarOrTerm', self.testCases)()
    
    def testGraphNodePath(self):
        Test.makeTestFunc('GraphNodePath', self.testCases)()
    
    def testGraphNode(self):
        Test.makeTestFunc('GraphNode', self.testCases)()
     
    def testCollectionPath(self):
        Test.makeTestFunc('CollectionPath', self.testCases)()
  
    def testCollection(self):
        Test.makeTestFunc('Collection', self.testCases)()
  
    def testBlankNodePropertyListPath(self):
        Test.makeTestFunc('BlankNodePropertyListPath', self.testCases)()

# # [101]   BlankNodePropertyListPath         ::=   '[' PropertyListPathNotEmpty ']' 
# 
# # [100]   TriplesNodePath   ::=   CollectionPath | BlankNodePropertyListPath 
# 
# # [99]    BlankNodePropertyList     ::=   '[' PropertyListNotEmpty ']' 
# 
# # [98]    TriplesNode       ::=   Collection | BlankNodePropertyList 
# 
# # [97]    Integer   ::=   INTEGER 
# 
# # [96]    PathOneInPropertySet      ::=   iri | 'a' | '^' ( iri | 'a' ) 
# 
# # [95]    PathNegatedPropertySet    ::=   PathOneInPropertySet | '(' ( PathOneInPropertySet ( '|' PathOneInPropertySet )* )? ')' 
# 
# # [94]    PathPrimary       ::=   iri | 'a' | '!' PathNegatedPropertySet | '(' Path ')' 
# 
# # [93]    PathMod   ::=   '?' | '*' | '+' 
# 
# # [92]    PathEltOrInverse          ::=   PathElt | '^' PathElt 
# 
# # [91]    PathElt   ::=   PathPrimary PathMod? 
# 
# # [90]    PathSequence      ::=   PathEltOrInverse ( '/' PathEltOrInverse )* 
# 
# # [89]    PathAlternative   ::=   PathSequence ( '|' PathSequence )* 
# 
# # [88]    Path      ::=   PathAlternative 
# 
# # [87]    ObjectPath        ::=   GraphNodePath 
# 
# # [86]    ObjectListPath    ::=   ObjectPath ( ',' ObjectPath )* 
# 
# # [85]    VerbSimple        ::=   Var 
# 
# # [84]    VerbPath          ::=   Path 
# 
# # [83]    PropertyListPathNotEmpty          ::=   ( VerbPath | VerbSimple ) ObjectListPath ( ';' ( ( VerbPath | VerbSimple ) ObjectList )? )* 
# 
# # [82]    PropertyListPath          ::=   PropertyListPathNotEmpty? 
# 
# # [81]    TriplesSameSubjectPath    ::=   VarOrTerm PropertyListPathNotEmpty | TriplesNodePath PropertyListPath 
# 
# # [80]    Object    ::=   GraphNode 
# 
# # [79]    ObjectList        ::=   Object ( ',' Object )* 
# 
# # [78]    Verb      ::=   VarOrIri | 'a' 
# 
# # [77]    PropertyListNotEmpty      ::=   Verb ObjectList ( ';' ( Verb ObjectList )? )* 
# 
# # [76]    PropertyList      ::=   PropertyListNotEmpty? 
# 
# # [75]    TriplesSameSubject        ::=   VarOrTerm PropertyListNotEmpty | TriplesNode PropertyList 
# 
# # [74]    ConstructTriples          ::=   TriplesSameSubject ( '.' ConstructTriples? )? 
# 
# # [73]    ConstructTemplate         ::=   '{' ConstructTriples? '}' 
# 
# # [72]    ExpressionList    ::=   NIL | '(' Expression ( ',' Expression )* ')' 
# 
# # [70]    FunctionCall      ::=   iri ArgList 
# 
# # [69]    Constraint        ::=   BrackettedExpression | BuiltInCall | FunctionCall 
# 
# # [68]    Filter    ::=   'FILTER' Constraint 
# 
# # [67]    GroupOrUnionGraphPattern          ::=   GroupGraphPattern ( 'UNION' GroupGraphPattern )* 
# 
# # [66]    MinusGraphPattern         ::=   'MINUS' GroupGraphPattern 
# 
# # [65]    DataBlockValue    ::=   iri | RDFLiteral | NumericLiteral | BooleanLiteral | 'UNDEF' 
# 
# # [64]    InlineDataFull    ::=   ( NIL | '(' Var* ')' ) '{' ( '(' DataBlockValue* ')' | NIL )* '}' 
# 
# # [63]    InlineDataOneVar          ::=   Var '{' DataBlockValue* '}' 
# 
# # [62]    DataBlock         ::=   InlineDataOneVar | InlineDataFull 
# 
# # [61]    InlineData        ::=   'VALUES' DataBlock 
# 
# # [60]    Bind      ::=   'BIND' '(' Expression 'AS' Var ')' 
# 
# # [59]    ServiceGraphPattern       ::=   'SERVICE' 'SILENT'? VarOrIri GroupGraphPattern 
# 
# # [58]    GraphGraphPattern         ::=   'GRAPH' VarOrIri GroupGraphPattern 
# 
# # [57]    OptionalGraphPattern      ::=   'OPTIONAL' GroupGraphPattern 
# 
# # [56]    GraphPatternNotTriples    ::=   GroupOrUnionGraphPattern | OptionalGraphPattern | MinusGraphPattern | GraphGraphPattern | ServiceGraphPattern | Filter | Bind | InlineData 
# 
# # [55]    TriplesBlock      ::=   TriplesSameSubjectPath ( '.' TriplesBlock? )? 
# 
# # [54]    GroupGraphPatternSub      ::=   TriplesBlock? ( GraphPatternNotTriples '.'? TriplesBlock? )* 
# 
# # [53]    GroupGraphPattern         ::=   '{' ( SubSelect | GroupGraphPatternSub ) '}' 
# 
# # [52]    TriplesTemplate   ::=   TriplesSameSubject ( '.' TriplesTemplate? )? 
# 
# # [51]    QuadsNotTriples   ::=   'GRAPH' VarOrIri '{' TriplesTemplate? '}' 
# 
# # [50]    Quads     ::=   TriplesTemplate? ( QuadsNotTriples '.'? TriplesTemplate? )* 
# 
# # [49]    QuadData          ::=   '{' Quads '}' 
# 
# # [48]    QuadPattern       ::=   '{' Quads '}' 
# 
# # [47]    GraphRefAll       ::=   GraphRef | 'DEFAULT' | 'NAMED' | 'ALL' 
# 
# # [46]    GraphRef          ::=   'GRAPH' iri 
# 
# # [45]    GraphOrDefault    ::=   'DEFAULT' | 'GRAPH'? iri 
# 
# # [44]    UsingClause       ::=   'USING' ( iri | 'NAMED' iri ) 
# 
# # [43]    InsertClause      ::=   'INSERT' QuadPattern 
# 
# # [42]    DeleteClause      ::=   'DELETE' QuadPattern 
# 
# # [41]    Modify    ::=   ( 'WITH' iri )? ( DeleteClause InsertClause? | InsertClause ) UsingClause* 'WHERE' GroupGraphPattern 
# 
# # [40]    DeleteWhere       ::=   'DELETE WHERE' QuadPattern 
# 
# # [39]    DeleteData        ::=   'DELETE DATA' QuadData 
# 
# # [38]    InsertData        ::=   'INSERT DATA' QuadData 
# 
# # [37]    Copy      ::=   'COPY' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
# 
# # [36]    Move      ::=   'MOVE' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
# 
# # [35]    Add       ::=   'ADD' 'SILENT'? GraphOrDefault 'TO' GraphOrDefault 
# 
# # [34]    Create    ::=   'CREATE' 'SILENT'? GraphRef 
# 
# # [33]    Drop      ::=   'DROP' 'SILENT'? GraphRefAll 
# 
# # [32]    Clear     ::=   'CLEAR' 'SILENT'? GraphRefAll 
# 
# # [31]    Load      ::=   'LOAD' 'SILENT'? iri ( 'INTO' GraphRef )? 
# 
# # [30]    Update1   ::=   Load | Clear | Drop | Add | Move | Copy | Create | InsertData | DeleteData | DeleteWhere | Modify 
# 
# # [29]    Update    ::=   Prologue ( Update1 ( ';' Update )? )? 
# 
# # [28]    ValuesClause      ::=   ( 'VALUES' DataBlock )? 
# 
# # [27]    OffsetClause      ::=   'OFFSET' INTEGER 
# 
# # [26]    LimitClause       ::=   'LIMIT' INTEGER 
# 
# # [25]    LimitOffsetClauses        ::=   LimitClause OffsetClause? | OffsetClause LimitClause? 
# 
# # [24]    OrderCondition    ::=   ( ( 'ASC' | 'DESC' ) BrackettedExpression ) 
# 
# #             | ( Constraint | Var ) 
# 
# # [23]    OrderClause       ::=   'ORDER' 'BY' OrderCondition+ 
# 
# # [22]    HavingCondition   ::=   Constraint 
# 
# # [21]    HavingClause      ::=   'HAVING' HavingCondition+ 
# 
# # [20]    GroupCondition    ::=   BuiltInCall | FunctionCall | '(' Expression ( 'AS' Var )? ')' | Var 
# 
# # [19]    GroupClause       ::=   'GROUP' 'BY' GroupCondition+ 
# 
# # [18]    SolutionModifier          ::=   GroupClause? HavingClause? OrderClause? LimitOffsetClauses? 
# 
# # [17]    WhereClause       ::=   'WHERE'? GroupGraphPattern 
# 
# # [16]    SourceSelector    ::=   iri 
# 
# # [15]    NamedGraphClause          ::=   'NAMED' SourceSelector 
# 
# # [14]    DefaultGraphClause        ::=   SourceSelector 
# 
# # [13]    DatasetClause     ::=   'FROM' ( DefaultGraphClause | NamedGraphClause ) 
# 
# # [12]    AskQuery          ::=   'ASK' DatasetClause* WhereClause SolutionModifier 
# 
# # [11]    DescribeQuery     ::=   'DESCRIBE' ( VarOrIri+ | '*' ) DatasetClause* WhereClause? SolutionModifier 
# 
# # [10]    ConstructQuery    ::=   'CONSTRUCT' ( ConstructTemplate DatasetClause* WhereClause SolutionModifier | DatasetClause* 'WHERE' '{' TriplesTemplate? '}' SolutionModifier ) 
# 
# # [9]     SelectClause      ::=   'SELECT' ( 'DISTINCT' | 'REDUCED' )? ( ( Var | ( '(' Expression 'AS' Var ')' ) )+ | '*' ) 
# 
# # [8]     SubSelect         ::=   SelectClause WhereClause SolutionModifier ValuesClause 
# 
# # [7]     SelectQuery       ::=   SelectClause DatasetClause* WhereClause SolutionModifier 
# 
# # [6]     PrefixDecl        ::=   'PREFIX' PNAME_NS IRIREF 
# 
# # [5]     BaseDecl          ::=   'BASE' IRIREF 
# 
# # [4]     Prologue          ::=   ( BaseDecl | PrefixDecl )* 
# 
# # [3]     UpdateUnit        ::=   Update 
# 
# # [2]     Query     ::=   Prologue 
# 
# #             ( SelectQuery | ConstructQuery | DescribeQuery | AskQuery ) 
# 
# #             ValuesClause 
# 
# # [1]     QueryUnit         ::=   Query 

        

        
        
if __name__ == "__main__":
    unittest.main()
