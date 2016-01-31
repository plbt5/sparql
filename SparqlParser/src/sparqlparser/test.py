from pyparsing import *
from sparqlparser.base import *
from sparqlparser.grammar import *
# from sparqlparser.func_test import *
# 
# RDFLiteral_p = Group(
#                      String_p('lexical_form') \
#                      + Optional(
#                                 Group (
#                                        (
#                                         LANGTAG_p('langtag') \
#                                         ^ \
#                                         ('^^' + iri_p('datatype'))
#                                         )
#                                        )
#                                 )('datatype')
#                  )('all')
#                      
# # [129]   RDFLiteral        ::=   String ( LANGTAG | ( '^^' iri ) )? 
# # l = ['"test"', '"test" @en-bf', "'test' ^^ <test>", "'test'^^:"]
# # printResults(l, 'RDFLiteral')
# 
# s = '"test" @en-bf'
# 
# r = RDFLiteral_p.parseString(s)
# 
# print(r)
# print(list(r.keys()))
# print(r[0])
# print(r[0].keys())


# def makeParseInfoFunc(classname):
# #     assert isinstance(eval(classname), ParseInfo)
#     def makeparseinfo(parseresults):
#         return makeParseInfoWithClass(classname, parseresults)
#     return makeparseinfo
# 
# def makeParseInfoWithClass(classname, parseresults):
#     assert isinstance(parseresults, ParseResults), type(parseresults)
#     return makeParseInfoWithClassAndName(classname, parseresults, parseresults.getName())
# 

def parseInfoFunc(classname):
    cls = globals()[classname]
    def makeparseinfo(parseresults):
#         print(cls)
        name = parseresults.getName()
        while len(parseresults) == 1 and isinstance(parseresults[0], ParseResults) and not parseresults[0].getName():
                parseresults = parseresults[0]
        items = []
        if isinstance(parseresults, str):
            return cls(name, parseresults)
        else:
            assert isinstance(parseresults, ParseResults)
            valuedict = dict((id(t), k) for (k, t) in parseresults.items())
            assert len(valuedict) == len(list(parseresults.items())), 'internal error: len(valuedict) = {}, len(parseresults.items) = {}'.format(len(valuedict), len(list(parseresults.items)))
            for t in parseresults:
                k = valuedict.get(id(t))
                if isinstance(t, (str, ParseInfo)):
                    items.append([k, t])
                else:
                    assert isinstance(t, ParseResults)
                    items.append([k, makeParseInfo(t)])
            return cls(name, items)  
    return makeparseinfo      
       
def test(classname):
    def fun(parseresults):
        print('hello')
        return PN_LOCAL_ESC(parseresults)
    return fun


PN_LOCAL_ESC_e = r'\\[_~.\-!$&\'()*+,;=/?#@%]'
PN_LOCAL_ESC_p = Regex(PN_LOCAL_ESC_e)
class PN_LOCAL_ESC(Terminal): 
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
PN_LOCAL_ESC_p.setParseAction(parseInfoFunc('PN_LOCAL_ESC'))

HEX_e = r'[0-9A-Fa-f]'
HEX_p = Regex(HEX_e)
class HEX(Terminal):  
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
HEX_p.setParseAction(parseInfoFunc('HEX'))

PERCENT_e = r'%({})({})'.format( HEX_e, HEX_e)
PERCENT_p = Regex(PERCENT_e)
class PERCENT(Terminal):   
    def assignPattern(self):
        self.__dict__['pattern'] = eval(self.__class__.__name__ + '_p')
PERCENT_p.setParseAction(parseInfoFunc('PERCENT'))
                                             
s = '\\&'
 
r = PN_LOCAL_ESC_p.parseString(s)
 
r[0].dump()

s = 'D'

r = HEX_p.parseString(s)

r[0].dump()

s = '%F0'

r = PERCENT_p.parseString(s)

r[0].dump()

# a = Word(alphas)
# n = Word(nums)
# s = 'abc def'
# p1 = ((a('a1') | n('n1')) + a('a2'))
# p2 = Group(p1)
# p3 = Group(p1)('p3')
# p4 = p1('p4')
# p5 = Group(p2)
# r1 = p1.parseString(s)
# r2 = p2.parseString(s)
# r3 = p3.parseString(s)
# r4 = p4.parseString(s)
# r5 = p5.parseString(s)
# 
# for r in [r1]:
#     print('getName:', r.getName())
#     print('keys:', list(r.keys()))
#     print(list(r.items()))
#     print()
#     print(r.dump())
#     print()
# 
# # print(r1)
# s1 = makeParseInfo(r1, r1.getName())
# print('\nS1:', s1.name)
# print('items:')
# s1.dumpItems(depth=2)
# print('dump:')
# s1.dump(depth=1)
# s2 = makeParseInfo(r1, r2.getName())
# print('\nS2:', s2.name)
# print('items:')
# s2.dumpItems(depth=2)
# print('dump:')
# s2.dump(depth=1)
# s3 = makeParseInfo(r1, r3.getName())
# print('\nS3:', s3.name)
# print('items:')
# s3.dumpItems(depth=2)
# print('dump:')
# s3.dump(depth=1)
# s4 = makeParseInfo(r1, r4.getName())
# print('\nS4:', s4.name)
# print('items:')
# s4.dumpItems(depth=2)
# print('dump:')
# s4.dump(depth=1)
# s5 = makeParseInfo(r1, r5.getName())
# print('\nS5:', s5.name)
# print('items:')
# s5.dumpItems(depth=2)
# print('dump:')
# s5.dump(depth=1)



    
