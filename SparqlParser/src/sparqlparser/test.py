from pyparsing import *
from sparqlparser.base import *


# s = "'work' ^^<work>"
# 
# r = RDFLiteral(s)

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

# Aword_p = Word(alphas)
# class Aword(SPARQLTerminal):
#     def assignPattern(self):
#         return eval(self.__class__.__name__ + '_p')
# Aword_p.setParseAction(parseInfoFunc('Aword'))
# 
# 
# s = 'algebra'
# 
# r = Aword(s)
# 
# r.dump()


        
class ParsePattern(type):
    def __new__(cls, name, bases, namespace, **kwds):
        result = type.__new__(cls, name, bases, dict(namespace))
        result.pattern = eval(name+'_p')
        return result


Bword_p = Word(alphas)
class Bword(metaclass=ParsePattern):
    pass

print(Bword.pattern)
#     def assignPattern(self):
#         return eval(self.__class__.__name__ + '_p')
# Aword_p.setParseAction(parseInfoFunc('Aword'))


print(Bword.pattern == Bword_p)

bw = Bword()
print(bw.getPattern())
bw.test()



    